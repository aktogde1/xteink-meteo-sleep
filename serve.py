import http.server, os, sys, urllib.request, uuid
role = sys.argv[1] if len(sys.argv) > 1 else "site"
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# /relay и /save — не публичный API: отвечаем только своему origin и file:// (Origin "null").
# Чужой Origin = чужой сайт дёргает локальный сервер как прокси в домашнюю сеть.
ORIGIN_OK = {"http://localhost:8765", "http://127.0.0.1:8765", "null", ""}
def origin_ok(handler):
    return handler.headers.get("Origin", "") in ORIGIN_OK

class NoCache:
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, must-revalidate")
        super().end_headers()

class Site(NoCache, http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/relay-check"):
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"ok")
            return
        super().do_GET()
    def do_POST(self):
        if self.path.startswith("/relay"):
            if not origin_ok(self):
                self.send_error(403); return
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query)
            addr = q.get("addr", [""])[0]
            name = (q.get("name", ["sleep.bmp"])[0])[:80].replace("/", "_")
            data = self.rfile.read(int(self.headers.get("Content-Length", 0) or 0))
            bnd = "----xms" + uuid.uuid4().hex
            mp = (('--%s\r\nContent-Disposition: form-data; name="file"; filename="%s"\r\nContent-Type: image/bmp\r\n\r\n' % (bnd, name)).encode()
                  + data + ("\r\n--%s--\r\n" % bnd).encode())
            req = urllib.request.Request(addr, data=mp, method="POST")
            req.add_header("Content-Type", "multipart/form-data; boundary=" + bnd)
            try:
                up = urllib.request.urlopen(req, timeout=120)
                out = ("status:" + str(up.getcode())).encode()
            except Exception as e:
                out = ("ERR " + str(e)).encode()
            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(out)
            return
        if self.path != "/save":
            self.send_error(404); return
        if not origin_ok(self):
            self.send_error(403); return
        data = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        with open("sleep-test.bmp", "wb") as f:
            f.write(data)
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, *a): pass

class FakeReader(NoCache, http.server.BaseHTTPRequestHandler):
    # имитация inkMOD: без CORS-заголовков, как настоящий ридер
    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        if self.path.startswith("/upload"):
            with open("upload-test.bin", "wb") as f:
                f.write(body)
            out = b"ok"
        elif self.path.startswith("/api/settings"):
            with open("settings-test.txt", "wb") as f:
                f.write(self.path.encode() + b" | " + body)
            out = b"Applied 1 setting(s)"
        else:
            self.send_error(404); return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(out)
    def log_message(self, *a): pass

if role == "reader":
    http.server.ThreadingHTTPServer(("127.0.0.1", 8766), FakeReader).serve_forever()
else:
    http.server.ThreadingHTTPServer(("127.0.0.1", 8765), Site).serve_forever()

# Development Guide (agent / contributor blueprint)

**Xteink Meteo Sleep** is a **single-page single-file web app** (`index.html`): plain JS + canvas, no build step, no dependencies, no server required.
`serve.py` is the local dev server (site + upload relay to the reader); **`meteo-server.bat`** launches it and opens the page — the novice route to one-click install.
This document is the code map — it tells you where things live so you don't have to search every time.
**Rule of the project: whenever you change structure, update this file in the same commit.**

## Current status

- Tested **only** on Xteink X4 + inkMOD 1.1.7 — field reports for other devices/firmware are welcome.
- Interface languages: **Русский · English** (auto-detected from the browser, switchable via the header badges, `?lang=xx` URL override).
- Donations: Tribute + crypto (USDT/BTC/ETH), badges in the header.

## Page structure (`index.html`, in file order)

| Section | What lives there |
|---|---|
| `<style>` | All CSS. Colors **only** via CSS variables; dark theme = `@media (prefers-color-scheme: dark)` overriding the variables (soft dark, not black) |
| `#compatPop` | Top popup (cookie-notice style): firmware compatibility + tested-on note; dismissible via «Понятно» button, stored in `lsx.compatSeen` |
| header (`.nav`) | Centered brand; right side: lang badges (Русский/English), ♥ Tribute badge, ₮ Crypto badge, GitHub badge |
| `#controls` | Generator groups: City → Device (X4/X3) → **Card theme** (single dark-card toggle) → buttons (Install to reader / Download sleep.bmp / Refresh) → Reader address (single field; stored in `lsx.reader`) + hint («Enter the IP address shown on your e-reader in File Transfer mode») + `#httpsNote` (shown on HTTPS, links to index.html & meteo-server.bat). No forecast-days selector anymore: the card always shows an hourly forecast for the rest of today |
| `#preview` | Canvas `#card` — live card preview |
| `.foot` | Footer: data credits (Open-Meteo, local moon math), credits line, no-affiliation disclaimer |
| `<script>` | Everything: `I18N` (ru/en), drawing, BMP writer, network, reader upload, crypto modal, init |

## “Where do I change …?” cheat table

| Task | Where |
|---|---|
| Card layout / block order | `drawCard(dayOffset)` — fixed block set (`W` is a const), flow-based `y` cursor. Last block (`W.fc`) is the **hourly forecast for the rest of today**: rows are auto-fitted (step between hours grows until the remaining day fits above the footer) |
| Weather icons look | `drawIcon` / `drawSun` / `drawCloud` / `drawMoon` |
| Weather condition wording | `I18N.<lang>.wmo` + `wmoKey()` (order matters: snow 71–77 before shower `<= 82`!) |
| Add a UI string | add key to **both** `I18N` blocks (ru, en) + `data-i18n="key"` on the element |
| New device size | `DEVICES` map (`x4: [480,800]`, `x3: [480,640]`) + a `data-dev` button in `#deviceSeg` |
| Donation link | `DONATE_URL` (app) / donate badge (header) |
| Crypto addresses | `CRYPTO` array |
| Reader address handling | `readerAddress()` (single `#readerAddr` field, prepends `http://`, stores in `lsx.reader`) |
| Compat popup texts | `bnFw`, `rmTested`, `okBtn` keys; visibility stored in `lsx.compatSeen` |
| Install endpoints | `installOnReader()`: the direct route first does a one-time no-cors reachability probe, then `sendOne()` → `relaySend` (local relay, progress, relay `ERR…` body = failure) or `directSend` (blind cross-origin POST, response unreadable); then `/api/settings` `{"sleepScreen":3}` |
| Card theme | `theme` var (`"light"`/`"dark"`) + `#themeSeg` toggle; stored in `lsx.invert` (legacy key) |

## Languages

`I18N = { ru: {...}, en: {...} }`. Detection order: `?lang=` URL param → `lsx.lang` (saved by the badges) → browser language (`ru` → ru, otherwise en). All strings (UI + card + statuses) live in the dicts; dates via `Intl.DateTimeFormat` with `LOCALE`.

## External APIs (free, no keys)

- Forecast, sunrise/sunset, precipitation probability, wind: `api.open-meteo.com/v1/forecast` (`daily` for the «днём/ночью», sunrise/sunset block + `hourly=temperature_2m,weather_code,precipitation_probability` for the hourly block, `forecast_days=2` — the hourly block filters to the rest of the local day at the *place*, using `current.time` for comparison, never tomorrow)
- City search: `geocoding-api.open-meteo.com/v1/search` — **flaky, sometimes down** → fallback: Nominatim `search`
- Localized city name on language switch: Nominatim `reverse` (`zoom=10`, `accept-language`)
- WMO codes → `wmoKey()` (order matters: snow 71–77 **before** shower `<= 82`)

## Reader upload protocol (inkMOD 1.1.x / CrossPoint)

1. Reader in **File Transfer mode** (inkMOD: hold power ~20 s). Address: `http://inkmod.local`, the IP shown on the reader screen, or `http://192.168.4.1` on the `InkMOD-Reader` hotspot.
2. `POST {addr}/upload?path=<folder>` — multipart, field `file`. inkMOD lock screens live in the `/Sleep` folder; the single install writes `sleep.bmp`.
3. `POST {addr}/api/settings` — `{"sleepScreen":3}` (= "Custom image"; verified in inkMOD `src/SettingsList.h → buildSleepScreenSetting`).
4. **Cross-origin reality:** the reader sends no CORS headers → every XHR always fires `onerror`, even on success. Requests still arrive. Therefore: a one-time no-cors `fetch` probe checks reachability (network fail ≠ CORS fail), per-file errors are ignored, and byte-level upload progress is impossible (no upload events cross-origin without CORS).
5. **Chrome Private Network Access** blocks requests from public HTTPS sites (GitHub Pages) to the reader on the home network → the one-click buttons work from the **local file** or `localhost` only; on the online version the buttons are disabled with a warning.

## Local development

```bash
python serve.py site    # http://localhost:8765 — site + /relay-check + /relay (upload relay, multipart built server-side; /relay and /save only accept Origin: localhost or file:// — otherwise any site could use the server as a LAN proxy)
python serve.py reader  # fake inkMOD reader on http://127.0.0.1:8766 (writes uploads to upload-test.bin)
```

- `serve.py` sends `Cache-Control: no-store` (stale browser cache once shipped a broken build — do not remove).
- `meteo-server.bat` (repo) starts the site server and opens the page; the relay makes the one-click buttons work 100% offline-of-CORS.

## Release flow

1. Edit `index.html` (+ this file if structure changed).
2. Test on `localhost:8765`: RU/EN search of a cyrillic query, hourly rows for early-morning (many hours left → 2 h step) and late-evening (few hours left → 1 h step) syncs, BMP size exactly `480*3*800 + 54 = 1152054`, install against the fake reader, both themes, footer in both languages.
3. Commit and push to `main` with git.
4. GitHub Pages redeploys automatically from `main` (~1 min).

## Known gotchas

1. `drawCloud` fills with `BG` — restore `ctx.fillStyle = FG` at the end of every draw function, else text turns invisible.
2. HTML blocks must exist before the `<script>` runs; `let y` in `drawCard` must be declared (strict mode + gating blocks).
3. Python `\uD83D`-style surrogate escapes in patch scripts crash utf-8 writes and truncate files to 0 bytes — use `chr(0x1F4CC)`/`fromCodePoint`, guard with `html.encode('utf-8')` before writing.
4. History note: `f7611e6` deleted `sendOne`/`relaySend`/`directSend` but kept the call — the install button died silently; restored in `0d673cb`. Don't remove helpers without grepping callers.
5. Same lesson on the CSS side: that cleanup also dropped the `.bar`/`#pfill` styles (progress bar silently invisible) and left rules for removed blocks (`nav.menu`, `#about`, `header.site`, `.home`, `.iconLink`, `details`, `code`) plus the undefined `--acc2`/`--gold` references. When removing a feature, grep the HTML for its classes/ids and the CSS for the vars those rules used.

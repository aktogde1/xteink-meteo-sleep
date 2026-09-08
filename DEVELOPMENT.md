# Development Guide (agent / contributor blueprint)

The site is a **single page** (`index.html`): sticky centered brand, nav menu (Generator / Idea / Roadmap / Install / Releases), compatibility banner, the generator, the project idea section, footer. All logic and translations live in this one file. (`app.html` is just a redirect stub.)

For the local one-click install there is also `serve.py` — a tiny local server (site + upload relay to the reader) and a `Метео Сервер.bat` launcher.

This document is the code map — it tells you where things live so you don't have to search every time.
**Rule of the project: whenever you change structure, update this file in the same commit.**

## File layout

### `index.html` (landing)

| Section | What lives there |
|---|---|
| `<style>` | Landing styles; dark adjustments via `@media (prefers-color-scheme: dark)` where needed |
| `.nav` | Sticky dark navbar: centered brand, menu (Generator / Idea / Roadmap / Install), lang badges (RU/EN), ♥ donate badge, GitHub badge; burger menu below 720px |
| `.hero` | Centered headline + tagline + CTA buttons (Open generator → `app.html`) |
| `.compat` | Compatibility banner: BMP works on any firmware; address = what the reader shows; placement depends on firmware; tested only on X4 + inkMOD 1.1.7 |
| `#features` | 6 feature cards |
| `#idea` | Project idea quote |
| `#roadmap` | Timeline (`L[LANG].rl` — items as `[done|next, title, desc]`) |
| `#install` | Two install paths side by side |
| `<script>` → `L` | Landing translations (same 6 languages) |

### `app.html` (generator)

| Section (in file order) | What lives there |
|---|---|
| `<style>` | Same CSS-variable system as before |
| header | ← Home link, lang badges, crypto badge, donate badge, GitHub octocat |
| `#controls` | City → Device → Forecast days → **Card widgets** (checkboxes) → install/download/refresh buttons → Reader → details (install details / manual / sources) |
| `#preview` | Canvas `#card` |
| `<script>` → `I18N` | All UI + card strings per language (`ru, en, zh, es, de, vi`); placeholders via `tf()` |
| `<script>` → drawing | `drawSun`, `drawCloud`, `drawIcon`, `drawMoon`, `drawCard` |
| `<script>` → `encodeBMP` | Hand-written 24-bit BMP writer (threshold 140 → 2 colors) |
| `<script>` → network | `searchCity()` (Open-Meteo → Nominatim fallback), `loadWeather()` |
| `<script>` → `installOnReader()` | Push + apply sleep screen |

## “Where do I change …?” cheat table

| Task | Where |
|---|---|
| Card layout / widget order | `drawCard()` in `app.html` — every block is gated by `W.*` |
| Which widgets exist / defaults | `W` object (top of app.html script) + `wMap` (checkbox wiring) + the `#wg*` checkboxes in HTML |
| Weather icons look | `drawIcon` / `drawSun` / `drawCloud` / `drawMoon` |
| Weather condition wording | `I18N.<lang>.wmo` + `wmoKey()` (order matters: snow before shower!) |
| Add a UI string | add key to **all** `I18N` blocks + `data-i18n="key"` on the element (both files have their own dicts) |
| Add a language | copy `I18N` block (app), `L` block (landing), add `LOCALE` entry, add `.badge.lang` in both headers |
| New device size | `DEVICES` map |
| Donation link | `DONATE_URL` (app) / donate badge href (landing) |
| Crypto addresses | `CRYPTO` array (app) |
| Reader default address | `DEFAULT_READER` (app) |
| Install endpoints | `installOnReader()` (`/upload?path=/Sleep` + `/api/settings` `{"sleepScreen":3}`) |
| Multi-day pack (ZIP + upload to reader) | `buildPackFiles()` → `makeZip()`/`crc32()`/`xhrUpload()`; handlers `packZip.onclick` / `packReader.onclick` |
| Reader folder for the pack | `#rfolder` input (default `/Weather`, stored in `lsx.rfolder`) |
| Compat banner texts | `bnFw` + `rmTested` (app), `.compat` block (landing) |

## Widget system

`W = { date, cur, dn, sm, moon, fc, city }` (booleans, default true). Persisted in `localStorage["lsx.widgets"]`. Checkboxes (`#wgDate` … `#wgCity`) map via `wMap`. `drawCard()` skips gated blocks; the divider before the forecast is drawn only if something above it was drawn.

## External APIs (all free, no keys)

- Forecast + sunrise/sunset: `api.open-meteo.com/v1/forecast`
- City search: `geocoding-api.open-meteo.com/v1/search` — **flaky** → fallback Nominatim `search` (`jsonv2`, `addressdetails=1`)
- Localized city name: Nominatim `reverse` (`zoom=10`, `accept-language`)
- WMO codes → `wmoKey()` (order matters: snow 71–77 before shower `<= 82`)

## Known gotchas

1. `drawCloud` fills with `BG` — every draw function must restore `ctx.fillStyle = FG` at the end, else following text is white-on-white.
2. HTML blocks must exist **before** the `<script>` tag runs — a modal inserted after `</body>`… before `</html>` but after the script breaks init with `null.onclick`.
3. Python `\uD83D`-style surrogate escapes crash utf-8 `write()` **and truncate the file to 0 bytes**. Use `String.fromCodePoint(0x1F4CC)` in JS / `chr(0x1F4CC)` in Python, and `html.encode('utf-8')` as a guard before writing.
4. Localized city name: Open-Meteo geocoder does NOT return Russian names reliably → Nominatim reverse with `accept-language`; airports (`feature_code` starting `AIR`) are excluded, PPL-priority, 0.3° threshold.
5. localStorage keys: `lsx.city`, `lsx.device`, `lsx.days`, `lsx.invert`, `lsx.reader`, `lsx.lang` (landing + app), `lsx.widgets`.
6. The generator page must be opened **locally** (file://) for the install button to reach the reader; GitHub Pages is HTTPS → mixed content blocks it (handled with a warning + `?lang=` override still works).

## Reader install protocol (inkMOD 1.1.x / CrossPoint)

1. Reader in **File Transfer mode** (inkMOD: hold power, ~20 s).
2. Address: `http://inkmod.local`, or the IP on the reader screen, or `http://192.168.4.1` on the `InkMOD-Reader` hotspot.
3. `POST {addr}/upload?path=/Sleep` — multipart, field `file`, name `sleep.bmp`.
4. `POST {addr}/api/settings` — `{"sleepScreen":3}` (= "Custom image", verified in inkMOD `SettingsList.h`).
5. Sent with `fetch(..., { mode: "no-cors" })` — unreadable responses, network errors still caught.

## Local development

```bash
python serve.py site    # landing + app on http://localhost:8765 (POST /save → sleep-test.bmp)
python serve.py reader  # fake inkMOD reader on http://localhost:8766
```

## Release flow

1. Edit `index.html` (landing) and/or `app.html` (generator) + docs.
2. Test on `localhost:8765`: RU+EN search of a cyrillic query, extreme temps (+39/−12) for overlap, widgets on/off, BMP size exactly `480*3*800 + 54 = 1152054`, install against the fake reader, mobile viewport.
3. Push: `python gh_push.py <repoPath> <localFile> ["message"]` (needs `.gh-token`, fine-grained PAT, Contents RW, expires ~monthly).
4. Pages redeploys automatically from `main`.

## Tested on

- Device: Xteink X4
- Firmware: inkMOD 1.1.7
- Nothing else — reports for X3 / X4 Pro / CrossPoint / other inkMOD versions are very welcome.

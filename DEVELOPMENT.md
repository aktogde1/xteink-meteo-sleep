# Development Guide (agent / contributor blueprint)

Xteink Meteo Sleep is a **single-file web app** (`index.html`): plain JS + canvas, no build step, no dependencies.
This document is the code map — it tells you where things live so you don't have to search the file every time.
**Rule of the project: whenever you change structure, update this file in the same commit.**

## File layout inside `index.html`

| Section (in file order) | What lives there |
|---|---|
| `<style>` | All CSS. Colors **only** via CSS variables (`--bg`, `--panel`, `--fg`, `--acc`, …). Dark theme = `@media (prefers-color-scheme: dark)` overriding the variables — it is intentionally *soft* (dark gray, not black) |
| `<header>` | Brand + header links: lang badges (RU/EN), donate badge (Tribute), GitHub octocat icon |
| `<main>` → `#controls` | UI groups: City → Device → Forecast days → Card (invert + buttons) → Reader → collapsible details (install details, manual install, data sources, project idea, roadmap) |
| `<main>` → `#preview` | The canvas (`#card`) showing the live card preview |
| `<script>` → `I18N` | **All** UI + card strings, one object per language: `ru, en, zh, es, de, vi`. Placeholders use `{name}` syntax, resolved by `tf()` |
| `<script>` → drawing | `drawSun`, `drawCloud`, `drawIcon` (kind→glyph), `drawMoon` (pixel raster of the lit/unlit side), `drawCard` (the whole card layout) |
| `<script>` → `encodeBMP` | Hand-written 24-bit BMP writer (bottom-up, luminance threshold 140 → exactly 2 colors) |
| `<script>` → network | `searchCity()` (geocoder + Nominatim fallback), `loadWeather()` (Open-Meteo forecast) |
| `<script>` → `installOnReader()` | Pushes `sleep.bmp` to the reader + applies the sleep-screen mode |

## “Where do I change …?” cheat table

| Task | Where |
|---|---|
| Card layout / text position | `drawCard()` — everything is flow-based (`y` cursor), sizes proportional to `w` |
| Weather icons look | `drawIcon` / `drawSun` / `drawCloud` / `drawMoon` |
| Weather condition wording | dict `I18N.<lang>.wmo` + key mapping `wmoKey()` (open-meteo WMO codes → dict keys) |
| Moon phase names | `I18N.<lang>.moon` (8 phases, computed in `moonPhase()`) |
| Add a UI string | add key to **all** `I18N` blocks + `data-i18n="key"` attribute on the element |
| Add a language | copy one `I18N` block, add entry to `LOCALE`, add a `.badge.lang` button in the header |
| New device size | `DEVICES` map (`x4: [480,800]`, `x4pro: [480,800]`, `x3: [480,640]`) |
| Donation link | `DONATE_URL` (empty string hides the badge) |
| Crypto addresses | `CRYPTO` array (badge + modal rows, incl. qr.crypt.bot links) |
| Reader default address | `DEFAULT_READER` (user's address is stored in `localStorage["lsx.reader"]`) |
| Install logic / endpoints | `installOnReader()` |

## External APIs (all free, no keys)

- Forecast + sunrise/sunset: `api.open-meteo.com/v1/forecast` (`current=…`, `daily=…`, `timezone=auto`)
- City search: `geocoding-api.open-meteo.com/v1/search` — **flaky, sometimes down entirely**
  → fallback: Nominatim (`nominatim.openstreetmap.org/search`, `format=jsonv2&addressdetails=1`)
- Localized city name on language switch: Nominatim `reverse` (`zoom=10`, `accept-language=…` → `address.city`)
- Open-Meteo WMO weather codes are mapped to icons in `wmoKey()` / `wmoKind()` and to wording in `I18N.<lang>.wmo`

⚠️ Order matters in `wmoKey()` (e.g. snow codes 71–77 must be checked **before** the `<= 82` shower range).

## Known gotchas (learned the hard way)

1. **Canvas fillStyle reset** — `drawCloud` fills with `BG` to occlude what's behind; every draw function must restore `ctx.fillStyle = FG` at the end, otherwise all following `fillText` is white-on-white (invisible).
2. **HTML blocks must be inserted *before* the `<script>` tag** — anything after it doesn't exist when the script runs → `null.onclick` crash at init.
3. **Python `\uXXXX` surrogates** — emoji assembled from surrogate escapes (`\uD83D\xDCxx`) crash `file.write()` in utf-8 **and truncate the file to 0 bytes**. Use `chr(0x1F4CC)` / real characters, and always `html.encode('utf-8')` as a guard **before** writing.
4. City search: Open-Meteo geocoder matching depends on the `language` param → `searchCity()` tries `LANG → no param → en`. City *names are localized on language switch* via Nominatim reverse (airports excluded, `feature_code` starting with `AIR` is skipped; distance threshold 0.3°).
5. localStorage keys are prefixed `lsx.*` (`lsx.city`, `lsx.device`, `lsx.days`, `lsx.invert`, `lsx.reader`, `lsx.lang` is **not** persisted — language is auto-detected, `?lang=xx` URL param overrides for sharing).

## Reader install protocol (inkMOD 1.1.x / CrossPoint)

1. Reader must be in **File Transfer mode** (web server on). inkMOD: hold the power button (~20 s).
2. Address: mDNS `http://inkmod.local`, or the IP shown on the reader screen, or `http://192.168.4.1` on the `InkMOD-Reader` hotspot.
3. `POST {addr}/upload?path=/Sleep` — multipart form, field **`file`**, filename **`sleep.bmp`** (inkMOD takes the custom lock screen from the `/Sleep` folder; overwrites existing).
4. `POST {addr}/api/settings` — body `{"sleepScreen":3}` (index 3 = "Custom image"; verified against inkMOD `src/SettingsList.h → buildSleepScreenSetting`).
5. Both requests are sent with `fetch(..., { mode: "no-cors" })` — the reader sends no CORS headers, so responses are unreadable (fire-and-forget; network errors are still caught).

## Local development

```bash
python serve.py site    # serves index.html on http://localhost:8765 (POST /save stores raw body → sleep-test.bmp)
python serve.py reader  # fake inkMOD reader on http://localhost:8766 (POST /upload, POST /api/settings, NO CORS headers)
```
Point the site's reader address at `http://127.0.0.1:8766` to test the install flow end-to-end without hardware.

## Release flow

1. Edit `index.html` / docs.
2. Test on `localhost:8765`: RU+EN search, extreme temps (+39 / −12) for icon overlap, BMP size must be exactly `480*3*800 + 54 = 1152054` bytes, install against the fake reader.
3. Push: `python gh_push.py <repoPath> <localFile> ["message"]` (GitHub contents API; requires `.gh-token` — a fine-grained PAT with **Contents: Read/Write** on this repo only; it expires ~monthly and must then be re-issued).
4. GitHub Pages redeploys automatically from `main`.

## Tested on

- Device: Xteink X4
- Firmware: inkMOD 1.1.7
- Nothing else — field reports for X3 / X4 Pro / CrossPoint / other inkMOD versions are very welcome.

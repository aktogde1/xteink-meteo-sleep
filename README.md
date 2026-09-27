# Xteink Meteo Sleep 🌙

[![Language](https://img.shields.io/badge/lang-%D0%A0%D1%83%D1%81%D1%81%D0%BA%D0%B8%D0%B9-2f6f3e?style=flat)](README.ru.md)
[![Donate](https://img.shields.io/badge/%E2%99%A5-Donate%20via%20Tribute-D64072?style=flat)](https://web.tribute.tg/d/Q5J)

**[👉 Open the web app](https://aktogde1.github.io/xteink-meteo-sleep/?lang=en)**

Weather, daily tasks, moon phase, and sunrise/sunset — or a QR business card — on the lock screen of **Xteink X4 / X3** e-readers (**inkMOD** / **CrossPoint** firmware). The X4 layout also fits X4C and X4 Pro.

![Lock screen card](screenshot-en.png)

## What is it

A browser-based generator: choose a city, add today's tasks, select your reader, and download a ready-to-use `sleep.bmp`. It is a single HTML file with no build step, account, or hosted backend.

On the card: weekday and date, daytime maximum, nighttime temperature, weather summary, sunrise and sunset, moon phase, daily tasks, city, and update time. The card uses exactly two colors for crisp e-ink output.

Tasks are stored only in the current browser. The X4 layout shows up to 5 tasks; X3 shows up to 3. Drag tasks to reorder them, mark them complete, or delete them. The first tasks in the list are the ones placed on the card.

Use the day arrows to plan cards up to 6 days ahead. Every date has its own task list. The reader cannot rotate these cards automatically: select a day, download its `sleep.bmp`, and install that file when needed.

Interface languages: **English · Русский** — auto-detected from your browser (switcher in the header).

**QR card mode:** a large QR code centered on the screen, pointing to a profile, channel, or website. Pick “Card type → QR card”, paste the link, and download `sleep.bmp`. The QR is generated locally by the embedded [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) library (MIT, ~20 KB).

> **Want live self-hosted dashboards instead?** If flashing custom firmware and running a small home server is your thing, look at [Tesserae](https://github.com/dmellok/tesserae) + [CrossInk](https://github.com/dmellok/CrossInk). This tool is the other route: no firmware, no server — just a `sleep.bmp` from a web page.

## Quick start

1. Open the [web app](https://aktogde1.github.io/xteink-meteo-sleep/?lang=en)
2. Enter your city and press **Search**
3. Choose the card day, then add and reorder its tasks
4. Select X4 or X3 and press **Refresh forecast**. Use X4 for X4C and X4 Pro too
5. Press **Download sleep.bmp**, then copy it to the `Sleep` folder on the microSD, replacing the existing file
6. Set the sleep screen to **Custom image** and lock the reader

## One-click install (from a computer)

Download [`index.html`](https://raw.githubusercontent.com/aktogde1/xteink-meteo-sleep/main/index.html) and open it on your laptop. Use the **"Refresh card & install"** button:

1. Reader — in File Transfer mode (on inkMOD: hold the power button, the server is up in ~20 s)
2. Laptop — on the same Wi-Fi network (or on the reader's `InkMOD-Reader` hotspot, address `http://192.168.4.1`)
3. The reader address is pre-filled (the one shown on its screen) — press the button → the image flies to the reader and the "Custom image" mode is set automatically

The page also auto-detects a tiny local relay (if you serve it through one) and routes the upload through it — same button, same result.

**Even simpler:** download [`meteo-server.bat`](meteo-server.bat) (and [`serve.py`](serve.py) next to it) and run the bat — it starts a local server and opens the page where one-click install works without any browser restrictions (Python required).

> **Why doesn't the button work on the online version?** The web app is served over HTTPS while the reader lives on your home network over HTTP. Browsers block those requests (mixed content) — there is no way around it. The local file is fully featured.

## Devices

| Button | Resolution |
|---|---|
| X4 (X4 / X4C / X4 Pro) | 480×800 |
| X3 | 480×640 |

## Under the hood

- One `index.html` file, plain JS + canvas, no build step; the single embedded library is `qrcode-generator` (MIT, ~20 KB minified) for offline QR generation in the business card mode
- Weather, daytime/nighttime temperatures, and sunrise/sunset — [Open-Meteo](https://open-meteo.com/) (open API, no sign-up); city — their geocoder
- Tasks — browser `localStorage`; no account and no cloud sync
- Moon phase — synodic cycle math (29.53 days from the reference new moon on 2000-01-06)
- The BMP is hand-written in JS: 24-bit, bottom-up, luminance threshold 140 → exactly 2 colors
- Install to reader: `POST /upload?path=/Sleep` (multipart, field `file`) + `POST /api/settings` `{"sleepScreen":3}` — index 3 = "Custom image" on inkMOD 1.1.x. Served through a local relay? The page detects it via `/relay-check` and sends through it; otherwise the upload goes directly to the reader

## Compatibility

Tested on Xteink X4 + inkMOD 1.1.7. The X4 size also covers X4C and X4 Pro. CrossPoint and X3 are supported via card sizes and the manual route; feedback welcome.

## Support the project ♥

If the generator was useful — you can [donate via Tribute](https://web.tribute.tg/d/Q5J) (Telegram). Not required, but much appreciated 🙂

**Crypto:**

[![USDT](https://img.shields.io/badge/USDT-TRC20-26A17B?style=flat)](https://qr.crypt.bot/?url=TXkyArvXBQyFqSMcfK7pFeeaCyaYgenUg1)
[![BTC](https://img.shields.io/badge/BTC-Bitcoin-F7931A?style=flat)](https://qr.crypt.bot/?url=bc1qyp7rcyasjk6k0eh84qc8wvveaptyqnkmmt33p6)
[![ETH](https://img.shields.io/badge/ETH-Ethereum-627EEA?style=flat)](https://qr.crypt.bot/?url=0x68ba5c4b009579525fac3318AcD4Ec00938C5Ca4)

- USDT (TRC20): `TXkyArvXBQyFqSMcfK7pFeeaCyaYgenUg1` — [QR](https://qr.crypt.bot/?url=TXkyArvXBQyFqSMcfK7pFeeaCyaYgenUg1)
- BTC: `bc1qyp7rcyasjk6k0eh84qc8wvveaptyqnkmmt33p6` — [QR](https://qr.crypt.bot/?url=bc1qyp7rcyasjk6k0eh84qc8wvveaptyqnkmmt33p6)
- ETH: `0x68ba5c4b009579525fac3318AcD4Ec00938C5Ca4` — [QR](https://qr.crypt.bot/?url=0x68ba5c4b009579525fac3318AcD4Ec00938C5Ca4)

## Development

The whole app is a single `index.html` — but it has a map. See **[DEVELOPMENT.md](DEVELOPMENT.md)** for the code layout, a "where do I change …" cheat table, known gotchas and the release flow. The project idea is shown on the site itself (the 💡 section).

## License

MIT. Not affiliated with Xteink, inkMOD or CrossPoint. Weather data — Open-Meteo (non-commercial use).

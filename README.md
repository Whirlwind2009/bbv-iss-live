# 🛰️ BBV ISS LIVE — Mission Control

**Birla Balika Vidyapeeth, Pilani · Computer Science Exhibition · Annual Day 2026**
*One Planet. One Orbit. Live Data.*

A student-built Python dashboard that requests the International Space Station's **reported** position from a public API, validates it, and shows it on a map with honest status labels.

> **What it is not:** it does not intercept ISS radio, talk to the station, or use NASA's internal telemetry. Positions come from a third-party public API ([Where the ISS at?](https://wheretheiss.at/w/developer)). Check its terms and limits before the event.

## What visitors see
| Mode | Shows |
|---|---|
| 🛰️ **Orbit Watch** | World map, latest ISS marker, recent ground track, India box, Pilani |
| 🌍 **Earth in Motion** | A globe that turns to follow the station |
| 🧪 **Space Data Lab** | Raw JSON → validated values → saved readings table and charts, plus the **Data Detective** challenge and CSV download |

Status badge: **LIVE** (data ≤ 30 s old) · **DELAYED** · **OFFLINE DEMO** (internet/API failed → a clearly labelled replay of a *simulated* orbit, never shown as real).

## Run it on your computer
```bash
git clone https://github.com/<your-username>/bbv-iss-live.git
cd bbv-iss-live
python -m venv .venv
.venv\Scripts\activate            # Windows   (Mac/Linux: source .venv/bin/activate)
pip install -r requirements.txt
streamlit run app.py
```

## Deploy (Streamlit Community Cloud)
1. Push this folder to a GitHub repository (public, or private with access granted).
2. Go to <https://share.streamlit.io> → **Create app** → pick the repo, branch `main`, main file `app.py`.
3. Deploy, then copy the app URL.
4. Make the QR code for the exhibit table:
   `pip install -r requirements-dev.txt` then `python scripts/make_qr.py <your-app-url>` → `qr_code.png`.

## Project map (where each Grade XII idea lives)
| File | Purpose | Grade XII concepts |
|---|---|---|
| `iss_core.py` | Fetch, validate, status, history, CSV, ground track | variables, dictionaries, functions, conditionals, loops, lists, exception handling, file handling, modules |
| `viz.py` | Plotly map and charts | using libraries |
| `app.py` | Streamlit screens (thin: it only *uses* `iss_core`) | modules, functions |
| `scripts/make_sample_data.py` | Builds the simulated replay file | loops, maths, file handling |
| `tests/` | Automated checks (`pytest`) | testing, functions |

**The core logic in plain words**
```
every 15 s:
    try: request the position → parse JSON
         validate (fields, numbers, ranges, timestamp)
         save to history + CSV
    except: show OFFLINE DEMO (replay), say why
    show coordinates, data age, map
```
Library code vs our code: `requests` does HTTP, `pandas` organises tables, `Plotly` draws, `Streamlit` renders the page — *we* write the checking, the logic and the explanation.

## Reliability & rehearsal checklist
- [ ] Open the deployed URL on **every** display computer on the school network, one day before.
- [ ] Tick **Force OFFLINE DEMO** in the sidebar and check the replay banner is clear. Then unplug the internet and check again.
- [ ] Keep NASA's official [Spot the Station](https://spotthestation.nasa.gov/tracking_map.cfm) tracker open on a second screen as a backup.
- [ ] Keep a local copy of this repo and `data/sample_readings.csv`.
- [ ] Test browser zoom / full-screen (F11), cables and display scaling.
- [ ] Refresh is 10–30 s (default 15). The app never calls the API more than once per 8 s. Don't lower this.
- [ ] No visitor data is collected; no login needed.

## Things to know
- **History file:** the app appends readings to `data/readings.csv` (ignored by git). On Streamlit Cloud this storage is temporary and resets on restart — that is fine; the Data Lab also keeps readings in memory and offers a CSV download.
- **Sample replay:** `data/sample_readings.csv` is a **simulated** circular orbit (51.6° inclination, ~93 min), *not* real observations. Regenerate with `python scripts/make_sample_data.py`.
- **Map outlines** (coastlines/countries) are loaded by Plotly from `cdn.plot.ly`, so the browser needs internet to draw them. For fully offline maps: download `https://cdn.plot.ly/world_110m.json` into `static/topojson/` (the app then serves it itself). This optional step needs the file to be added on a connected computer; it was not testable while writing the app.
- **"Is it over India?"** compares the position with a rough rectangle (6.5–35.7° N, 68.1–97.4° E). Inside the outline is not the same as directly overhead, and a single coordinate cannot predict the next pass — use NASA's Spot the Station for sightings.
- The ISS is an international partnership; India's planned **Bharatiya Antariksh Station** is a separate Indian programme.
- API address can be overridden for testing: set environment variable `ISS_API_URL`.

## Tests
```bash
pip install -r requirements-dev.txt
pytest
```
38 tests cover validation, failure handling (network mocked), data age/status, ground-track date-line splitting, CSV round-trip and a headless run of all three screens in live and offline modes.

## Credits
Data: [Where the ISS at?](https://wheretheiss.at/w/developer) · ISS facts: [NASA](https://www.nasa.gov/missions/station/spot-the-station-frequently-asked-questions/) · Built with Python, Streamlit, Plotly, pandas and requests.

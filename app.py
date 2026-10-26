"""BBV ISS LIVE - Mission Control
Birla Balika Vidyapeeth, Pilani | Computer Science Exhibition

A student-built Python dashboard that shows where the International Space
Station is *reported* to be, using a public API.  It is NOT a radio
interception and cannot control the station.

Run:  streamlit run app.py
"""

import os
import time

import pandas as pd
import streamlit as st

import iss_core as core
import viz

HERE = os.path.dirname(os.path.abspath(__file__))
LIVE_CSV = os.path.join(HERE, "data", "readings.csv")          # written while running
SAMPLE_CSV = os.path.join(HERE, "data", "sample_readings.csv")  # simulated replay data
MIN_GAP_S = 8            # never call the API more often than this

# Optional: serve Plotly's map outlines from this repo so maps also work without
# internet.  See README ("Map outlines").  Does nothing if the file is absent.
PLOT_CONFIG = {}
if os.path.exists(os.path.join(HERE, "static", "topojson", "world_110m.json")):
    PLOT_CONFIG = {"topojsonURL": "app/static/topojson/"}

MODES = ["🛰️ Orbit Watch", "🌍 Earth in Motion", "🧪 Space Data Lab"]
STATUS_COLOURS = {core.STATUS_LIVE: "#2ecc71",
                  core.STATUS_DELAYED: "#ffab5e",
                  core.STATUS_OFFLINE: "#ff7b7b"}

st.set_page_config(page_title="BBV ISS LIVE", page_icon="🛰️", layout="wide")

st.markdown("""
<style>
.block-container {padding-top: 1.4rem; max-width: 1250px;}
.badge {display:inline-block; padding:6px 16px; border-radius:99px; font-weight:800;
        letter-spacing:.08em; color:#0a1330; font-size:0.95rem;}
.tagline {color:#ffd84d; font-weight:700; letter-spacing:.04em;}
.note {color:#a9bbe6; font-size:0.85rem;}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------------------
# Session state and data refresh
# --------------------------------------------------------------------------
@st.cache_data
def load_sample():
    return core.load_readings(SAMPLE_CSV)


def init_state():
    ss = st.session_state
    ss.setdefault("history", [])        # list of validated live readings
    ss.setdefault("last_fetch", 0.0)
    ss.setdefault("live_ok", False)
    ss.setdefault("error", None)
    ss.setdefault("raw", None)          # last raw JSON, for the Data Lab
    ss.setdefault("saved_ok", True)
    ss.setdefault("replay_i", 0)
    ss.setdefault("challenge", None)


def refresh_data(force_offline):
    """Try to get a fresh live reading; remember whether it worked."""
    ss = st.session_state
    if force_offline:
        ss.live_ok = False
        ss.error = "Offline demo mode selected."
        return
    if time.time() - ss.last_fetch < MIN_GAP_S and ss.history:
        return                          # polite: do not hammer the API
    ss.last_fetch = time.time()
    try:
        raw = core.fetch_raw()
        reading = core.validate_data(raw)
        ss.raw = raw
        ss.history = core.add_reading(ss.history, reading)
        ss.saved_ok = core.save_reading(LIVE_CSV, reading)
        ss.live_ok = True
        ss.error = None
    except core.ISSDataError as err:
        ss.live_ok = False
        ss.error = str(err)


def current_view():
    """Return (readings_to_plot, latest_reading, status) for the screen."""
    ss = st.session_state
    if ss.live_ok and ss.history:
        latest = ss.history[-1]
        age = core.data_age_seconds(latest)
        return ss.history, latest, core.get_status(age)

    # Offline: replay the saved SIMULATED orbit, clearly labelled.
    sample = load_sample()
    if not sample:
        return [], None, core.STATUS_OFFLINE
    ss.replay_i = (ss.replay_i + 1) % len(sample)
    window = sample[max(0, ss.replay_i - 40): ss.replay_i + 1]
    return window, window[-1], core.STATUS_OFFLINE


# --------------------------------------------------------------------------
# Reusable page pieces
# --------------------------------------------------------------------------
def status_badge(status):
    colour = STATUS_COLOURS[status]
    st.markdown(f'<span class="badge" style="background:{colour}">● {status}</span>',
                unsafe_allow_html=True)


def metrics_row(latest, status):
    ss = st.session_state
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Latitude", f"{latest['latitude']:.2f}°")
    c2.metric("Longitude", f"{latest['longitude']:.2f}°")
    c3.metric("Altitude", f"{latest['altitude_km']:.0f} km")
    kmh = latest["velocity_kmh"]
    c4.metric("Speed (km/h)", f"{kmh:,.0f}", f"{core.kmh_to_kms(kmh):.2f} km/s", delta_color="off")
    if status == core.STATUS_OFFLINE:
        c5.metric("Data age", "n/a (replay)")
    else:
        c5.metric("Data age", core.format_age(core.data_age_seconds(latest)))

    if status == core.STATUS_OFFLINE:
        last = ss.history[-1] if ss.history else None
        extra = (f" Last real reading was {core.format_age(core.data_age_seconds(last))} ago."
                 if last else "")
        st.warning("**OFFLINE DEMO** - showing a saved *simulated* orbit replay, "
                   "not the real ISS position. " + (f"Reason: {ss.error}." if ss.error else "") + extra)
    else:
        st.caption(f"Observation time: {core.utc_text(latest['timestamp'])}  ·  "
                   f"{core.ist_text(latest['timestamp'])}  ·  "
                   f"Source: {core.SOURCE_NAME}")


def india_line(latest, status):
    prefix = "Replay: " if status == core.STATUS_OFFLINE else ""
    if core.is_over_india(latest["latitude"], latest["longitude"]):
        st.success(f"🇮🇳 {prefix}The reported position is inside India's rough bounding box. "
                   "(That is not the same as being directly overhead.)")
    else:
        st.info(f"🌐 {prefix}The reported position is outside India's rough bounding box. "
                f"Distance from Pilani: about {core.distance_from_pilani_km(latest):,.0f} km.")


def footer():
    st.markdown("---")
    st.markdown(
        '<span class="note">Position values are <b>reported data from a public API</b>, not a '
        "direct radio signal from the station. This exhibit cannot communicate with or control the ISS. "
        "Approximate NASA facts: ~28,000 km/h, ~90 min per orbit, ~16 sunrises and sunsets a day. "
        "The ISS is an international partnership; India's planned Bharatiya Antariksh Station is a "
        "separate Indian programme. No visitor data is collected.</span>",
        unsafe_allow_html=True)


# --------------------------------------------------------------------------
# The three display modes (inside one auto-refreshing fragment)
# --------------------------------------------------------------------------
def render_live(mode, force_offline):
    refresh_data(force_offline)
    readings, latest, status = current_view()
    if latest is None:
        st.error("No data available - the sample replay file is missing.")
        return

    status_badge(status)
    metrics_row(latest, status)
    if not st.session_state.saved_ok and status != core.STATUS_OFFLINE:
        st.caption("⚠️ History file is not writable here; readings are kept in memory only.")

    if mode == MODES[0]:                                    # ---- Orbit Watch
        fig = viz.build_map(readings, latest, "natural earth",
                            marker_name="ISS (replay)" if status == core.STATUS_OFFLINE
                            else "ISS (latest reported)")
        st.plotly_chart(fig, config=PLOT_CONFIG)
        india_line(latest, status)

    elif mode == MODES[1]:                                  # ---- Earth in Motion
        fig = viz.build_map(readings, latest, "orthographic", rotate_to_latest=True)
        st.plotly_chart(fig, config=PLOT_CONFIG)
        st.caption("The globe turns to keep the station in the centre. "
                   "The yellow line is the recent ground track; the dotted box is a rough outline of India.")
        india_line(latest, status)

    else:                                                   # ---- Space Data Lab
        left, right = st.columns(2)
        with left:
            st.subheader("1 · Raw JSON (as received)")
            if status == core.STATUS_OFFLINE or not st.session_state.raw:
                st.info("No live response right now. Replay row shown instead.")
                st.json(core.reading_to_row(latest))
            else:
                st.json(st.session_state.raw, expanded=True)
        with right:
            st.subheader("2 · After Python validation")
            st.code(
                f"latitude     = {latest['latitude']:.4f}\n"
                f"longitude    = {latest['longitude']:.4f}\n"
                f"altitude_km  = {latest['altitude_km']:.1f}\n"
                f"velocity_kmh = {latest['velocity_kmh']:.0f}\n"
                f"timestamp    = {latest['timestamp']}   # {core.utc_text(latest['timestamp'])}\n"
                f"status       = '{status}'",
                language="python")
            st.caption("Checks done: all fields present · numbers valid · latitude/longitude in range · "
                       "altitude and speed plausible · timestamp read and age calculated.")

        st.subheader("3 · Saved readings")
        table = pd.DataFrame([core.reading_to_row(r) for r in readings[-15:]][::-1])
        st.dataframe(table.drop(columns=["utc"]), hide_index=True)
        if len(readings) > 2:
            c1, c2 = st.columns(2)
            c1.plotly_chart(viz.metric_chart(readings, "altitude_km", "Altitude over time", "km"))
            c2.plotly_chart(viz.metric_chart(readings, "velocity_kmh", "Speed over time", "km/h"))


def data_detective():
    """Visitor challenge: freeze a coordinate, guess the place, then reveal it."""
    ss = st.session_state
    st.markdown("---")
    st.subheader("🕵️ Data Detective")
    st.write("Freeze a reading, read the latitude and longitude, **guess where on Earth** "
             "the marker will appear - then reveal it.")
    live_ready = bool(ss.history) and ss.live_ok
    b1, b2 = st.columns([1, 1])
    if b1.button("🎯 New challenge", disabled=not live_ready):
        ss.challenge = {"reading": dict(ss.history[-1]), "revealed": False}
    if not live_ready:
        st.caption("Needs a live reading (not available in offline demo).")
    ch = ss.challenge
    if ch:
        r = ch["reading"]
        st.markdown(f"### Latitude **{r['latitude']:.2f}°**  ·  Longitude **{r['longitude']:.2f}°**")
        if b2.button("🔍 Reveal on the map"):
            ch["revealed"] = True
        if ch["revealed"]:
            st.plotly_chart(viz.build_map([r], r, "natural earth", marker_name="Challenge position"),
                            config=PLOT_CONFIG)
            st.write(f"Distance from Pilani: about **{core.distance_from_pilani_km(r):,.0f} km**. "
                     f"Visibility reported: *{r['visibility']}*.")

    with st.expander("Live or stale? - how to read the data age"):
        st.write("A marker is only 'live' if its **timestamp is recent**. Compare the *Observation time* "
                 f"with the clock: under {core.LIVE_LIMIT_S} s is LIVE, older is DELAYED, and when the "
                 "internet fails we show OFFLINE DEMO with a saved simulated replay. "
                 "Always check the age before trusting a value.")


# --------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------
init_state()

with st.sidebar:
    st.markdown("## 🛰️ BBV ISS LIVE")
    st.markdown('<div class="tagline">One Planet. One Orbit. Live Data.</div>', unsafe_allow_html=True)
    mode = st.radio("Display mode", MODES)
    refresh_s = st.slider("Refresh every (seconds)", 10, 30, 15)
    force_offline = st.checkbox("Force OFFLINE DEMO (rehearsal)")
    st.markdown("---")
    st.markdown('<span class="note">Built with Python · Streamlit · Plotly · GitHub<br>'
                f"Data: {core.SOURCE_NAME}<br>"
                "Birla Balika Vidyapeeth, Pilani</span>", unsafe_allow_html=True)

st.title("BBV ISS LIVE — Mission Control")
st.caption("From Code to Cosmos: how Python turns space data into knowledge.")

live_view = st.fragment(run_every=refresh_s)(render_live)
live_view(mode, force_offline)

if mode == MODES[2]:
    data_detective()
    if st.session_state.history:
        st.download_button("⬇️ Download saved readings (CSV)",
                           core.readings_to_csv_text(st.session_state.history),
                           file_name="iss_readings.csv", mime="text/csv")
footer()

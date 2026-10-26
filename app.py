"""BBV ISS LIVE - Mission Control
Birla Balika Vidyapeeth, Pilani | Computer Science Exhibition

A student-built Python dashboard that shows where the International Space
Station is *reported* to be, using a public API.  It is NOT a radio
interception and cannot control the station.

Run:  streamlit run app.py
Exhibit screens:  open the app address followed by  ?kiosk=1
"""

import os
import time
from datetime import datetime

import pandas as pd
import streamlit as st

import branding
import config
import i18n
import iss_core as core
import team
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

MODE_IDS = ["orbit", "globe", "lab", "team"]
STATUS_KEYS = {core.STATUS_LIVE: "st_live",
               core.STATUS_DELAYED: "st_delayed",
               core.STATUS_OFFLINE: "st_offline"}
STATUS_COLOURS = {core.STATUS_LIVE: "#2ecc71",
                  core.STATUS_DELAYED: "#ffab5e",
                  core.STATUS_OFFLINE: "#ff7b7b"}

# --------------------------------------------------------------------------
# Page set-up: URL options  ?kiosk=1  ?lang=hi
# --------------------------------------------------------------------------
params = st.query_params
KIOSK = str(params.get("kiosk", "")).lower() in ("1", "true", "yes")
LANG_FROM_URL = "hi" if str(params.get("lang", "")).lower() == "hi" else "en"

st.set_page_config(page_title="BBV ISS LIVE", page_icon="🛰️", layout="wide",
                   initial_sidebar_state="collapsed" if KIOSK else "expanded")

BASE_CSS = """
<style>
.block-container {padding-top: 4rem; max-width: 1250px;}
.badge {display:inline-block; padding:6px 16px; border-radius:99px; font-weight:800;
        letter-spacing:.08em; color:#0a1330; font-size:0.95rem;}
.tagline {color:#ffd84d; font-weight:700; letter-spacing:.04em;}
.note {color:#a9bbe6; font-size:0.85rem;}
.hdr {display:flex; align-items:center; gap:18px; margin-bottom:6px;}
.hdr img {width:92px; height:92px; border-radius:50%; background:#fff; padding:3px;
          box-shadow:0 0 0 3px #ffffff22;}
.hdr-school {color:#ffd84d; font-weight:800; letter-spacing:.06em; font-size:1.0rem;}
.hdr-sub {color:#a9bbe6; font-size:0.82rem; margin-bottom:2px;}
.hdr-title {font-size:2.2rem; font-weight:800; line-height:1.1; margin:2px 0;}
.hdr-tag {color:#a9bbe6; font-size:0.95rem;}
.fact {background:#101c44; border:1.5px solid #2a4a9a; border-radius:14px;
       padding:12px 18px; margin-top:10px;}
.fact b {color:#ffd84d;}
.fact small {color:#a9bbe6;}
.qrbox {display:flex; align-items:center; gap:16px; margin-top:8px;}
.qrbox img {width:120px; height:120px; border-radius:8px; background:#fff;}
.pgrid {display:grid; grid-template-columns:repeat(auto-fit,minmax(270px,1fr)); gap:18px;
        margin:8px 0 22px;}
.pcard {background:linear-gradient(180deg,#112357,#0d1b45); border:1.5px solid #2a4a9a;
        border-radius:18px; padding:18px; text-align:center;}
.avatar {width:150px; height:150px; border-radius:50%; margin:0 auto 10px; overflow:hidden;
         border:4px solid #ffd84d; background:#16306f; display:flex; align-items:center;
         justify-content:center; font-size:2.6rem; font-weight:800; color:#ffd84d;}
.avatar img {width:100%; height:100%; object-fit:cover; object-position:50% 18%;}
.pname {font-size:1.25rem; font-weight:800;}
.psub {color:#6ec6ff; font-weight:600; margin-bottom:8px;}
.role {text-align:left; background:#0a1330; border-radius:10px; padding:8px 12px;
       margin-top:8px; font-size:0.88rem;}
.role b {color:#ffd84d;}
.role span {color:#a9bbe6;}
.sec {font-size:1.3rem; font-weight:800; color:#6ec6ff; margin-top:14px;}
</style>
"""

BIG_CSS = """
<style>
[data-testid="stMetricValue"] {font-size: 3.3rem !important;}
[data-testid="stMetricLabel"] p {font-size: 1.35rem !important;}
[data-testid="stMetricDelta"] {font-size: 1.2rem !important;}
.badge {font-size: 1.7rem; padding: 10px 26px;}
.hdr-title {font-size: 3.2rem;} .hdr-school {font-size: 1.5rem;} .hdr-sub {font-size:1.1rem;}
.hdr img {width:130px; height:130px;}
.fact {font-size: 1.5rem; padding: 18px 26px;}
.stAlert p, .stCaption, [data-testid="stCaptionContainer"] {font-size: 1.15rem !important;}
.pname {font-size: 1.8rem;} .role {font-size: 1.15rem;} .avatar {width:200px; height:200px;}
</style>
"""

KIOSK_CSS = """
<style>
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"], [data-testid="stHeader"], [data-testid="stToolbar"],
[data-testid="stDecoration"], footer, #MainMenu {display: none !important;}
.block-container {padding-top: 0.6rem; max-width: 1500px;}
</style>
"""

st.markdown(BASE_CSS, unsafe_allow_html=True)


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
    ss.setdefault("last_replay", 0.0)
    ss.setdefault("challenge", None)
    ss.setdefault("opened_at", time.time())


def refresh_data(force_offline, refresh_s):
    """Try to get a fresh live reading; remember whether it worked."""
    ss = st.session_state
    if force_offline:
        ss.live_ok = False
        ss.error = "Offline demo mode selected."
        return
    gap = max(MIN_GAP_S, refresh_s - 1)
    if time.time() - ss.last_fetch < gap and ss.history:
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


def current_view(refresh_s):
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
    if time.time() - ss.last_replay >= max(MIN_GAP_S, refresh_s - 1):
        ss.replay_i = (ss.replay_i + 1) % len(sample)
        ss.last_replay = time.time()
    window = sample[max(0, ss.replay_i - 40): ss.replay_i + 1]
    return window, window[-1], core.STATUS_OFFLINE


# --------------------------------------------------------------------------
# Reusable page pieces (all text goes through tr -> English or Hindi)
# --------------------------------------------------------------------------
def age_text(seconds, lang):
    return core.format_age(seconds, tuple(i18n.tr(lang, "units_time").split("|")))


def render_header(lang):
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    logo = branding.logo_uri()
    img = f'<img src="{logo}" alt="BBV logo">' if logo else ""
    st.markdown(
        f'<div class="hdr">{img}<div>'
        f'<div class="hdr-school">{tr("school_name")}</div>'
        f'<div class="hdr-sub">{tr("school_line1")} · {tr("school_line2")}</div>'
        f'<div class="hdr-title">{tr("title")}</div>'
        f'<div class="hdr-tag">{tr("subtitle")}</div>'
        f'</div></div>', unsafe_allow_html=True)


def status_badge(status, lang):
    colour = STATUS_COLOURS[status]
    label = i18n.tr(lang, STATUS_KEYS[status])
    st.markdown(f'<span class="badge" style="background:{colour}">● {label}</span>',
                unsafe_allow_html=True)


def metrics_row(latest, status, lang):
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    ss = st.session_state
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(tr("lat"), f"{latest['latitude']:.2f}°")
    c2.metric(tr("lon"), f"{latest['longitude']:.2f}°")
    c3.metric(tr("alt"), f"{latest['altitude_km']:.0f} {tr('unit_km')}")
    kmh = latest["velocity_kmh"]
    c4.metric(tr("speed"), f"{kmh:,.0f}", f"{core.kmh_to_kms(kmh):.2f} {tr('km_s')}",
              delta_color="off")
    if status == core.STATUS_OFFLINE:
        c5.metric(tr("age"), tr("age_replay"))
    else:
        c5.metric(tr("age"), age_text(core.data_age_seconds(latest), lang))

    if status == core.STATUS_OFFLINE:
        last = ss.history[-1] if ss.history else None
        last_text = (tr("last_real", age=age_text(core.data_age_seconds(last), lang))
                     if last else "")
        reason = tr("reason", err=ss.error) if ss.error else ""
        st.warning(tr("offline_warn", reason=reason, last=last_text))
    else:
        st.caption(tr("obs_caption", utc=core.utc_text(latest["timestamp"]),
                      ist=core.ist_text(latest["timestamp"]), src=core.SOURCE_NAME))


def india_line(latest, status, lang):
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    prefix = tr("prefix_replay") if status == core.STATUS_OFFLINE else tr("prefix_none")
    if core.is_over_india(latest["latitude"], latest["longitude"]):
        st.success(tr("india_in", prefix=prefix))
    else:
        km = f"{core.distance_from_pilani_km(latest):,.0f}"
        st.info(tr("india_out", prefix=prefix, km=km))


def map_labels(lang):
    return {"india": i18n.tr(lang, "lbl_india"), "track": i18n.tr(lang, "lbl_track"),
            "pilani": i18n.tr(lang, "lbl_pilani")}


def render_orbit_counter(lang):
    """Orbits completed since the exhibition opened (simple elapsed-time maths)."""
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    now = time.time()
    start = core.parse_start_time(config.EXHIBITION_START)
    if start is None or start > now:
        start = st.session_state.opened_at
        when = tr("when_screen")
    else:
        when = datetime.fromtimestamp(start, core.IST).strftime("%d %b %Y, %H:%M IST")
    elapsed = now - start
    orbits = core.orbits_completed(elapsed, config.ORBIT_PERIOD_MIN)
    st.markdown(f"##### {tr('oc_title')}")
    c1, c2, c3 = st.columns(3)
    c1.metric(tr("oc_orbits"), f"{orbits}")
    c2.metric(tr("oc_sun"), f"{orbits}")
    c3.metric(tr("oc_time"), age_text(elapsed, lang))
    st.caption(f"{tr('oc_since', when=when)} {tr('oc_note', p=config.ORBIT_PERIOD_MIN)}")


def render_fact(lang):
    facts = i18n.STRINGS[lang]["facts"]
    fact = facts[int(time.time() // config.FACT_SECONDS) % len(facts)]
    st.markdown(f'<div class="fact"><b>{i18n.tr(lang, "fact_hdr")}</b> {fact} '
                f'<small>({i18n.tr(lang, "fact_note")})</small></div>',
                unsafe_allow_html=True)


def render_team(lang):
    """Meet the Team page (photos are optional - see team.py)."""
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)

    def avatar(person):
        uri = branding.photo_uri(person["photo"]) if team.SHOW_PHOTOS else ""
        if uri:
            return f'<div class="avatar"><img src="{uri}" alt=""></div>'
        return f'<div class="avatar">{branding.initials(person["name"])}</div>'

    students = ""
    for p in team.STUDENTS:
        roles = "".join(
            f'<div class="role"><b>{tr("role_" + r + "_t")}</b><br>'
            f'<span>{tr("role_" + r + "_d")}</span></div>' for r in p["roles"])
        students += (f'<div class="pcard">{avatar(p)}<div class="pname">{p["name"]}</div>'
                     f'<div class="psub">{tr("class_xi")}</div>{roles}</div>')
    mentors = ""
    for p in team.MENTORS:
        mentors += (f'<div class="pcard">{avatar(p)}<div class="pname">{p["name"]}</div>'
                    f'<div class="psub">{p["post"]}</div>'
                    f'<div class="note">{tr("mentor_role")}</div></div>')
    st.markdown(f'<div class="sec">{tr("team_title")} — {tr("team_sub")}</div>'
                f'<div class="sec" style="color:#ffd84d">{tr("team_students")}</div>'
                f'<div class="pgrid">{students}</div>'
                f'<div class="sec" style="color:#ffd84d">{tr("team_mentors")}</div>'
                f'<div class="pgrid">{mentors}</div>', unsafe_allow_html=True)


def render_footer(lang):
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    st.markdown("---")
    url = branding.current_app_url()
    qr = branding.qr_uri(url)
    qr_html = ""
    if qr:
        qr_html = (f'<div class="qrbox"><img src="{qr}" alt="QR code">'
                   f'<div><b>{tr("qr_title")}</b><br><span class="note">{url}</span></div></div>')
    st.markdown(qr_html + f'<p class="note" style="margin-top:10px">{tr("footer_note")}</p>',
                unsafe_allow_html=True)


# --------------------------------------------------------------------------
# The display modes (inside one auto-refreshing fragment)
# --------------------------------------------------------------------------
def render_live(mode, force_offline, lang, big, attract, refresh_s):
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    if attract:                                   # screens rotate by the clock
        slot = int(time.time() // config.ATTRACT_SECONDS)
        mode = MODE_IDS[slot % len(MODE_IDS)]

    refresh_data(force_offline, refresh_s)
    if mode == "team":
        render_team(lang)
        return

    readings, latest, status = current_view(refresh_s)
    if latest is None:
        st.error(tr("no_data"))
        return

    status_badge(status, lang)
    metrics_row(latest, status, lang)
    if not st.session_state.saved_ok and status != core.STATUS_OFFLINE:
        st.caption(tr("hist_not_writable"))
    height = 640 if big else 520
    marker = tr("lbl_iss_replay") if status == core.STATUS_OFFLINE else tr("lbl_iss")

    if mode == "orbit":                                     # ---- Orbit Watch
        fig = viz.build_map(readings, latest, "natural earth", marker_name=marker,
                            labels=map_labels(lang), height=height)
        st.plotly_chart(fig, config=PLOT_CONFIG)
        india_line(latest, status, lang)
        render_fact(lang)
        render_orbit_counter(lang)

    elif mode == "globe":                                   # ---- Earth in Motion
        fig = viz.build_map(readings, latest, "orthographic", rotate_to_latest=True,
                            marker_name=marker, labels=map_labels(lang), height=height)
        st.plotly_chart(fig, config=PLOT_CONFIG)
        st.caption(tr("globe_caption"))
        india_line(latest, status, lang)
        render_fact(lang)
        render_orbit_counter(lang)

    else:                                                   # ---- Space Data Lab
        left, right = st.columns(2)
        with left:
            st.subheader(tr("lab_1"))
            if status == core.STATUS_OFFLINE or not st.session_state.raw:
                st.info(tr("lab_no_live"))
                st.json(core.reading_to_row(latest))
            else:
                st.json(st.session_state.raw, expanded=True)
        with right:
            st.subheader(tr("lab_2"))
            st.code(
                f"latitude     = {latest['latitude']:.4f}\n"
                f"longitude    = {latest['longitude']:.4f}\n"
                f"altitude_km  = {latest['altitude_km']:.1f}\n"
                f"velocity_kmh = {latest['velocity_kmh']:.0f}\n"
                f"timestamp    = {latest['timestamp']}   # {core.utc_text(latest['timestamp'])}\n"
                f"status       = '{status}'",
                language="python")
            st.caption(tr("lab_checks"))

        st.subheader(tr("lab_3"))
        table = pd.DataFrame([core.reading_to_row(r) for r in readings[-15:]][::-1])
        st.dataframe(table.drop(columns=["utc"]), hide_index=True)
        if len(readings) > 2:
            c1, c2 = st.columns(2)
            c1.plotly_chart(viz.metric_chart(readings, "altitude_km", tr("chart_alt"), tr("unit_km")))
            c2.plotly_chart(viz.metric_chart(readings, "velocity_kmh", tr("chart_speed"), tr("unit_kmh")))
        render_fact(lang)


def data_detective(lang):
    """Visitor challenge: freeze a coordinate, guess the place, then reveal it."""
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)
    ss = st.session_state
    st.markdown("---")
    st.subheader(tr("det_title"))
    st.write(tr("det_intro"))
    live_ready = bool(ss.history) and ss.live_ok
    b1, b2 = st.columns([1, 1])
    if b1.button(tr("det_new"), disabled=not live_ready):
        ss.challenge = {"reading": dict(ss.history[-1]), "revealed": False}
    if not live_ready:
        st.caption(tr("det_needs"))
    ch = ss.challenge
    if ch:
        r = ch["reading"]
        st.markdown("### " + tr("det_coords", lat=f"{r['latitude']:.2f}", lon=f"{r['longitude']:.2f}"))
        if b2.button(tr("det_reveal")):
            ch["revealed"] = True
        if ch["revealed"]:
            st.plotly_chart(viz.build_map([r], r, "natural earth", marker_name=tr("lbl_challenge"),
                                          labels=map_labels(lang)), config=PLOT_CONFIG)
            st.write(tr("det_dist", km=f"{core.distance_from_pilani_km(r):,.0f}",
                        vis=r["visibility"]))

    with st.expander(tr("det_stale_title")):
        st.write(tr("det_stale_body", limit=core.LIVE_LIMIT_S))


# --------------------------------------------------------------------------
# Page layout
# --------------------------------------------------------------------------
init_state()

with st.sidebar:
    lang_label = st.radio(
        "Language / भाषा", list(i18n.LANGS), key="lang_choice", horizontal=True,
        index=0 if LANG_FROM_URL == "en" else 1)
    lang = i18n.LANGS[lang_label]
    tr = lambda k, **kw: i18n.tr(lang, k, **kw)

    st.markdown("## 🛰️ BBV ISS LIVE")
    st.markdown(f'<div class="tagline">{tr("tagline")}</div>', unsafe_allow_html=True)
    attract = st.checkbox(tr("attract"), value=KIOSK, key="attract")
    if attract:
        st.caption(tr("attract_note", s=config.ATTRACT_SECONDS))
    mode = st.radio(tr("display_mode"), MODE_IDS, key="mode", disabled=attract,
                    format_func=lambda m: tr("mode_" + m))
    refresh_s = st.slider(tr("refresh"), 10, 30, 15)
    big = st.checkbox(tr("big_text"), value=KIOSK, key="big")
    force_offline = st.checkbox(tr("force_offline"))
    st.markdown("---")
    st.markdown(f'<span class="note">{tr("built_with")}<br>'
                f'{tr("data_src", src=core.SOURCE_NAME)}<br>{tr("school_name")}</span>',
                unsafe_allow_html=True)

if big:
    st.markdown(BIG_CSS, unsafe_allow_html=True)
if KIOSK:
    st.markdown(KIOSK_CSS, unsafe_allow_html=True)

render_header(lang)

if mode == "team" and not attract:
    render_team(lang)                       # static page: no refreshing needed
else:
    every = min(refresh_s, 5) if attract else refresh_s   # attract mode checks the clock often
    live_view = st.fragment(run_every=every)(render_live)
    live_view(mode, force_offline, lang, big, attract, refresh_s)

if mode == "lab" and not attract:
    data_detective(lang)
    if st.session_state.history:
        st.download_button(tr("dl_csv"), core.readings_to_csv_text(st.session_state.history),
                           file_name="iss_readings.csv", mime="text/csv")
render_footer(lang)

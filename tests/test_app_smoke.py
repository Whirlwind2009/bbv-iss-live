"""Smoke tests: run the whole Streamlit app headlessly (network mocked)."""
import os
import re
import sys
import time

import pytest
from streamlit.testing.v1 import AppTest

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, ROOT)
import iss_core as core  # noqa: E402
import config  # noqa: E402

APP = os.path.join(ROOT, "app.py")
MODES = ["orbit", "globe", "lab", "team"]


def fake_raw():
    return {"latitude": 28.0, "longitude": 76.0, "altitude": 420.0, "velocity": 27600.0,
            "timestamp": int(time.time()), "visibility": "daylight"}


def start(monkeypatch, live=True, query=None):
    monkeypatch.setattr(core, "save_reading", lambda *a, **k: True)
    if live:
        monkeypatch.setattr(core, "fetch_raw", lambda *a, **k: fake_raw())
    else:
        def fail(*a, **k):
            raise core.ISSDataError("no internet")
        monkeypatch.setattr(core, "fetch_raw", fail)
    at = AppTest.from_file(APP, default_timeout=30)
    for k, v in (query or {}).items():
        at.query_params[k] = v
    at.run()
    return at


def all_text(at):
    parts = [m.value for m in at.markdown] + [m.value for m in at.warning]
    parts += [m.value for m in at.info] + [m.value for m in at.success] + [m.value for m in at.caption]
    return "\n".join(parts)


@pytest.mark.parametrize("mode", MODES)
def test_live(monkeypatch, mode):
    at = start(monkeypatch, True)
    at.radio(key="mode").set_value(mode).run()
    assert not at.exception
    if mode == "team":
        assert "Omanshi Dubey" in all_text(at) and "Nishi Soni" in all_text(at)
    else:
        assert "LIVE" in all_text(at)


@pytest.mark.parametrize("mode", ["orbit", "globe", "lab"])
def test_offline_replay(monkeypatch, mode):
    at = start(monkeypatch, False)
    at.radio(key="mode").set_value(mode).run()
    assert not at.exception
    assert any("OFFLINE DEMO" in m.value for m in at.warning)


def test_hindi_toggle(monkeypatch):
    at = start(monkeypatch, True)
    at.radio(key="lang_choice").set_value("हिन्दी").run()
    assert not at.exception
    text = all_text(at)
    assert "लाइव" in text and "बिरला बालिका विद्यापीठ" in text


@pytest.mark.parametrize("mode", ["lab", "orbit"])
def test_hindi_every_mode(monkeypatch, mode):
    at = start(monkeypatch, False, {"lang": "hi"})
    at.radio(key="mode").set_value(mode).run()
    assert not at.exception


def test_orbit_counter_and_fact_shown(monkeypatch):
    at = start(monkeypatch, True)
    text = all_text(at)
    assert "Orbit counter" in text and "Did you know?" in text


def test_kiosk_attract_mode(monkeypatch):
    at = start(monkeypatch, True, {"kiosk": "1"})
    assert not at.exception
    assert at.checkbox(key="attract").value is True
    assert at.radio(key="mode").disabled is True
    # consecutive time slots show orbit, globe, lab, team in turn
    base = 1_800_000_000            # a multiple of ATTRACT_SECONDS
    seen = []
    for slot in range(4):
        monkeypatch.setattr(time, "time", lambda s=slot: base + s * config.ATTRACT_SECONDS + 1.0)
        at.run()
        assert not at.exception
        text = all_text(at) + "\n".join(h.value for h in at.subheader)
        seen.append("team" if "Student team" in text else "lab" if "Raw JSON" in text
                    else "globe" if "The globe turns" in text else "orbit")
    assert seen == ["orbit", "globe", "lab", "team"]


def test_data_detective_flow(monkeypatch):
    at = start(monkeypatch, True)
    at.radio(key="mode").set_value("lab").run()
    [b for b in at.button if "New challenge" in b.label][0].click().run()
    [b for b in at.button if "Reveal" in b.label][0].click().run()
    assert not at.exception
    assert any("Distance from Pilani" in m.value for m in at.markdown)

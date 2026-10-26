import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import iss_core as core  # noqa: E402

GOOD = {"latitude": 14.52, "longitude": 72.83, "altitude": 408.2,
        "velocity": 27600.5, "timestamp": 1_767_225_600, "visibility": "daylight"}


def reading(lat, lon, ts=1):
    return {"timestamp": ts, "latitude": lat, "longitude": lon,
            "altitude_km": 420.0, "velocity_kmh": 27600.0, "visibility": "x"}


# ---- validation -----------------------------------------------------------
def test_validate_good():
    r = core.validate_data(GOOD)
    assert r["latitude"] == 14.52 and r["timestamp"] == 1_767_225_600


@pytest.mark.parametrize("field", ["latitude", "longitude", "altitude", "velocity", "timestamp"])
def test_validate_missing_field(field):
    bad = dict(GOOD)
    del bad[field]
    with pytest.raises(core.ISSDataError):
        core.validate_data(bad)


@pytest.mark.parametrize("field,value", [
    ("latitude", 120), ("longitude", -200), ("altitude", 5), ("velocity", 5),
    ("latitude", "abc"), ("latitude", None), ("longitude", True),
    ("latitude", float("nan")), ("timestamp", 0)])
def test_validate_bad_values(field, value):
    bad = dict(GOOD, **{field: value})
    with pytest.raises(core.ISSDataError):
        core.validate_data(bad)


def test_validate_not_a_dict():
    with pytest.raises(core.ISSDataError):
        core.validate_data([1, 2, 3])


# ---- fetching (network mocked) -------------------------------------------
def test_fetch_timeout(monkeypatch):
    def boom(*a, **k):
        raise requests.Timeout("slow")
    monkeypatch.setattr(core.requests, "get", boom)
    with pytest.raises(core.ISSDataError):
        core.fetch_raw()


def test_fetch_ok(monkeypatch):
    class Resp:
        def raise_for_status(self): pass
        def json(self): return GOOD
    monkeypatch.setattr(core.requests, "get", lambda *a, **k: Resp())
    assert core.fetch_position()["longitude"] == 72.83


def test_fetch_bad_json(monkeypatch):
    class Resp:
        def raise_for_status(self): pass
        def json(self): raise ValueError("not json")
    monkeypatch.setattr(core.requests, "get", lambda *a, **k: Resp())
    with pytest.raises(core.ISSDataError):
        core.fetch_raw()


# ---- time and status --------------------------------------------------------
def test_status_and_age():
    r = reading(0, 0, ts=1000)
    assert core.data_age_seconds(r, now=1010) == 10
    assert core.data_age_seconds(r, now=900) == 0          # never negative
    assert core.get_status(10) == core.STATUS_LIVE
    assert core.get_status(core.LIVE_LIMIT_S + 1) == core.STATUS_DELAYED


def test_format_age():
    assert core.format_age(5) == "5 s"
    assert core.format_age(75) == "1 min 15 s"
    assert core.format_age(3700) == "1 h 1 min"


# ---- calculations ---------------------------------------------------------
def test_india_box():
    assert core.is_over_india(28.37, 75.6)          # Pilani
    assert not core.is_over_india(51.0, 0.0)        # near London


def test_haversine():
    assert core.haversine_km(10, 10, 10, 10) == pytest.approx(0)
    assert core.haversine_km(0, 0, 0, 90) == pytest.approx(10007.5, rel=0.01)


def test_speed_conversion():
    assert core.kmh_to_kms(27600) == pytest.approx(7.667, abs=0.01)


# ---- history and ground track ---------------------------------------------
def test_add_reading_dedupes_and_trims():
    h = []
    core.add_reading(h, reading(0, 0, ts=1))
    core.add_reading(h, reading(0, 1, ts=1))        # same timestamp -> ignored
    assert len(h) == 1
    for t in range(2, 20):
        core.add_reading(h, reading(0, t, ts=t), max_len=5)
    assert len(h) == 5 and h[-1]["timestamp"] == 19


def test_track_splits_at_date_line():
    pts = [reading(10, 170, 1), reading(11, 178, 2), reading(12, -178, 3), reading(13, -170, 4)]
    segments = core.split_track(pts)
    assert len(segments) == 2 and len(segments[0]) == 2 and len(segments[1]) == 2
    lats, lons = core.track_with_gaps(pts)
    assert None in lats and None in lons


def test_track_no_split():
    segments = core.split_track([reading(0, 10, 1), reading(1, 20, 2)])
    assert len(segments) == 1


# ---- CSV ------------------------------------------------------------------------
def test_csv_roundtrip(tmp_path):
    path = str(tmp_path / "sub" / "r.csv")
    assert core.save_reading(path, reading(1.5, 2.5, ts=10))
    assert core.save_reading(path, reading(3.5, 4.5, ts=20))
    loaded = core.load_readings(path)
    assert [r["timestamp"] for r in loaded] == [10, 20]
    assert loaded[1]["latitude"] == pytest.approx(3.5)


def test_load_missing_file_and_bad_rows(tmp_path):
    assert core.load_readings(str(tmp_path / "nope.csv")) == []
    p = tmp_path / "bad.csv"
    p.write_text("timestamp,latitude,longitude,altitude_km,velocity_kmh,visibility\n"
                 "1,2,3,4,5,x\nbad,row\n")
    assert len(core.load_readings(str(p))) == 1


def test_save_unwritable(tmp_path):
    blocker = tmp_path / "file"
    blocker.write_text("x")
    assert core.save_reading(str(blocker / "r.csv"), reading(0, 0)) is False


def test_sample_data_is_valid():
    path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_readings.csv")
    rows = core.load_readings(path)
    assert len(rows) > 100
    for r in rows:
        assert -52 <= r["latitude"] <= 52 and -180 <= r["longitude"] <= 180

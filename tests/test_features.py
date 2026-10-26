import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import branding  # noqa: E402
import i18n  # noqa: E402
import iss_core as core  # noqa: E402
import team  # noqa: E402


def placeholders(text):
    return set(re.findall(r"{(\w+)}", text)) if isinstance(text, str) else None


def test_languages_have_same_keys_and_placeholders():
    en, hi = i18n.STRINGS["en"], i18n.STRINGS["hi"]
    assert set(en) == set(hi)
    for key in en:
        if key == "facts":
            assert len(en[key]) == len(hi[key]) >= 6
        else:
            assert placeholders(en[key]) == placeholders(hi[key]), key


def test_tr_fills_values_and_falls_back():
    assert "5" in i18n.tr("en", "attract_note", s=5)
    assert i18n.tr("xx", "tagline") == i18n.STRINGS["en"]["tagline"]


def test_orbits_completed():
    assert core.orbits_completed(0) == 0
    assert core.orbits_completed(-5) == 0
    assert core.orbits_completed(92.9 * 60 * 3 + 10) == 3
    assert core.orbits_completed(24 * 3600) == 15        # about 15.5 orbits a day


def test_parse_start_time():
    assert core.parse_start_time(None) is None
    assert core.parse_start_time("not a date") is None
    ist = core.parse_start_time("2026-11-14 09:00")
    utc = core.parse_start_time("2026-11-14T03:30:00+00:00")
    assert ist == utc                                     # 09:00 IST == 03:30 UTC


def test_app_url_from_headers():
    assert branding.app_url_from_headers({"Host": "bbv.streamlit.app"}) == "https://bbv.streamlit.app"
    assert branding.app_url_from_headers({"Host": "localhost:8501"}) == ""
    assert branding.app_url_from_headers({}, "https://x.example/") == "https://x.example"
    assert branding.app_url_from_headers({"X-Forwarded-Host": "a.b.app, c.d"}) == "https://a.b.app"


def test_qr_is_png_data_uri():
    assert branding.qr_uri("https://bbv.streamlit.app").startswith("data:image/png;base64,")
    assert branding.qr_uri("") == ""


def test_logo_and_photos_exist():
    assert branding.logo_uri().startswith("data:image/png")
    for person in team.STUDENTS + team.MENTORS:
        assert branding.photo_uri(person["photo"]).startswith("data:image/jpeg"), person["name"]


def test_initials():
    assert branding.initials("Ms. Radha Gupta") == "RG"
    assert branding.initials("Mr. Shobhit Daga") == "SD"


def test_roles_have_texts_in_both_languages():
    for person in team.STUDENTS:
        for r in person["roles"]:
            for lang in ("en", "hi"):
                assert i18n.STRINGS[lang]["role_%s_t" % r] and i18n.STRINGS[lang]["role_%s_d" % r]


def test_format_age_units_translate():
    assert core.format_age(75, ("से", "मिनट", "घं")) == "1 मिनट 15 से"
    assert len(i18n.tr("hi", "units_time").split("|")) == 3

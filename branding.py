"""branding.py - school logo, team photos and the QR code panel."""

import base64
import functools
import os

import segno

import config

HERE = os.path.dirname(os.path.abspath(__file__))


@functools.lru_cache(maxsize=None)
def data_uri(relative_path, mime):
    """Read a picture from the repo and return it as a data: URI ('' if missing)."""
    path = os.path.join(HERE, relative_path)
    try:
        with open(path, "rb") as f:
            encoded = base64.b64encode(f.read()).decode("ascii")
    except OSError:
        return ""
    return f"data:{mime};base64,{encoded}"


def logo_uri():
    return data_uri("assets/logo.png", "image/png")


def photo_uri(filename):
    return data_uri(os.path.join("assets", "team", filename), "image/jpeg")


def initials(name):
    """'Ms. Radha Gupta' -> 'RG' (used when a photo is not available)."""
    words = [w for w in name.replace(".", " ").split() if w.lower() not in ("ms", "mr", "mrs", "dr")]
    return "".join(w[0].upper() for w in words[:2])


def app_url_from_headers(headers, override=""):
    """Work out the public address of the app.  Returns '' on a local computer."""
    if override:
        return override.rstrip("/")
    host = (headers.get("X-Forwarded-Host") or headers.get("Host") or "").split(",")[0].strip()
    if not host or host.startswith(("localhost", "127.", "0.0.0.0", "192.168.", "10.")):
        return ""
    return f"https://{host}"


def current_app_url():
    """Public app address, from config.py or the browser request."""
    if config.APP_URL:
        return config.APP_URL.rstrip("/")
    try:
        import streamlit as st
        return app_url_from_headers(dict(st.context.headers))
    except Exception:
        return ""


@functools.lru_cache(maxsize=8)
def qr_uri(url):
    """QR code for the URL as a PNG data: URI."""
    if not url:
        return ""
    qr = segno.make(url, error="m")
    return qr.png_data_uri(scale=6, border=2, dark="#0a1330", light="#ffffff")

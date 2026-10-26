"""iss_core.py - the data logic of BBV ISS LIVE.

Everything a student needs to explain lives here, in plain Python:
variables, dictionaries, functions, conditionals, loops, lists,
exception handling and CSV file handling.  The Streamlit user interface
(app.py) only *uses* these functions.

Data flow:  API  ->  JSON  ->  validate_data()  ->  history list  ->  CSV / charts
"""

import csv
import math
import os
import time
from datetime import datetime, timedelta, timezone

import requests

# --------------------------------------------------------------------------
# Settings (variables / constants)
# --------------------------------------------------------------------------
API_URL = os.environ.get("ISS_API_URL",                       # override for testing
                         "https://api.wheretheiss.at/v1/satellites/25544")   # 25544 = ISS
SOURCE_NAME = "Where the ISS at? (wheretheiss.at)"
REQUEST_TIMEOUT = 10        # seconds to wait before giving up
LIVE_LIMIT_S = 30           # data older than this is shown as DELAYED
MAX_HISTORY = 300           # readings kept in memory

CSV_FIELDS = ["timestamp", "utc", "latitude", "longitude",
              "altitude_km", "velocity_kmh", "visibility"]

# Rough rectangle around India (not the exact border!)
INDIA_BOUNDS = {"lat_min": 6.5, "lat_max": 35.7,
                "lon_min": 68.1, "lon_max": 97.4}

PILANI = (28.37, 75.60)     # latitude, longitude of Pilani, Rajasthan
IST = timezone(timedelta(hours=5, minutes=30))

STATUS_LIVE = "LIVE"
STATUS_DELAYED = "DELAYED"
STATUS_OFFLINE = "OFFLINE DEMO"


class ISSDataError(Exception):
    """Raised when the data could not be fetched or fails validation."""


# --------------------------------------------------------------------------
# 1. Fetch  (HTTP request -> JSON -> Python dictionary)
# --------------------------------------------------------------------------
def fetch_raw(url=API_URL, timeout=REQUEST_TIMEOUT):
    """Ask the public API for the latest ISS position and return the JSON
    response as a dictionary.  Any network or JSON problem becomes an
    ISSDataError, so the rest of the program handles failure in one place."""
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError) as err:
        raise ISSDataError(f"Could not fetch data: {err}") from err


# --------------------------------------------------------------------------
# 2. Validate  (never trust a value just because it arrived)
# --------------------------------------------------------------------------
def _to_number(raw, key):
    """Read raw[key] as a finite float or raise ISSDataError."""
    if key not in raw:
        raise ISSDataError(f"Missing field: {key}")
    value = raw[key]
    if isinstance(value, bool):
        raise ISSDataError(f"Field {key} is not a number")
    try:
        number = float(value)
    except (TypeError, ValueError):
        raise ISSDataError(f"Field {key} is not a number: {value!r}")
    if math.isnan(number) or math.isinf(number):
        raise ISSDataError(f"Field {key} is not a finite number")
    return number


def validate_data(raw):
    """Check the API response and return a clean 'reading' dictionary."""
    if not isinstance(raw, dict):
        raise ISSDataError("Response is not a JSON object")

    latitude = _to_number(raw, "latitude")
    longitude = _to_number(raw, "longitude")
    altitude = _to_number(raw, "altitude")
    velocity = _to_number(raw, "velocity")
    timestamp = _to_number(raw, "timestamp")

    # Plausibility checks: are the numbers sensible for a real ISS?
    if not -90 <= latitude <= 90:
        raise ISSDataError(f"Latitude out of range: {latitude}")
    if not -180 <= longitude <= 180:
        raise ISSDataError(f"Longitude out of range: {longitude}")
    if not 150 <= altitude <= 1000:
        raise ISSDataError(f"Altitude not plausible: {altitude} km")
    if not 10000 <= velocity <= 40000:
        raise ISSDataError(f"Velocity not plausible: {velocity} km/h")
    if timestamp <= 0:
        raise ISSDataError("Timestamp is not valid")

    return {
        "timestamp": int(timestamp),
        "latitude": latitude,
        "longitude": longitude,
        "altitude_km": altitude,
        "velocity_kmh": velocity,
        "visibility": str(raw.get("visibility", "unknown")),
    }


def fetch_position(url=API_URL, timeout=REQUEST_TIMEOUT):
    """Fetch + validate in one step (used by tests and simple scripts)."""
    return validate_data(fetch_raw(url, timeout))


# --------------------------------------------------------------------------
# 3. Time, age and status
# --------------------------------------------------------------------------
def data_age_seconds(reading, now=None):
    """How many seconds old is this reading?  (never negative)"""
    if now is None:
        now = time.time()
    return max(0.0, now - reading["timestamp"])


def get_status(age_seconds):
    """LIVE if the reading is fresh, otherwise DELAYED."""
    if age_seconds <= LIVE_LIMIT_S:
        return STATUS_LIVE
    return STATUS_DELAYED


def format_age(seconds, units=("s", "min", "h")):
    """Turn 75 into '1 min 15 s' for display (units can be translated)."""
    sec_u, min_u, hour_u = units
    seconds = int(seconds)
    if seconds < 60:
        return f"{seconds} {sec_u}"
    minutes, secs = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes} {min_u} {secs} {sec_u}"
    hours, minutes = divmod(minutes, 60)
    return f"{hours} {hour_u} {minutes} {min_u}"


def utc_text(timestamp):
    return datetime.fromtimestamp(timestamp, timezone.utc).strftime("%d %b %Y, %H:%M:%S UTC")


def ist_text(timestamp):
    return datetime.fromtimestamp(timestamp, IST).strftime("%H:%M:%S IST")


# --------------------------------------------------------------------------
# 4. Simple calculations
# --------------------------------------------------------------------------
def kmh_to_kms(kmh):
    return kmh / 3600.0


def haversine_km(lat1, lon1, lat2, lon2):
    """Great-circle distance between two points on Earth, in km."""
    radius = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = p2 - p1
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def is_over_india(latitude, longitude):
    """True if the point lies inside India's rough bounding box.
    NOTE: this is a rectangle, not the border, and 'inside the map outline'
    is not the same as 'directly overhead'."""
    b = INDIA_BOUNDS
    return (b["lat_min"] <= latitude <= b["lat_max"]
            and b["lon_min"] <= longitude <= b["lon_max"])


def distance_from_pilani_km(reading):
    return haversine_km(reading["latitude"], reading["longitude"], *PILANI)


def parse_start_time(text):
    """Turn '2026-11-14 09:00' (India time) into a Unix timestamp, or None."""
    if not text:
        return None
    try:
        moment = datetime.fromisoformat(str(text).strip())
    except ValueError:
        return None
    if moment.tzinfo is None:
        moment = moment.replace(tzinfo=IST)
    return moment.timestamp()


def orbits_completed(elapsed_seconds, period_minutes=92.9):
    """Whole orbits an object with this period completes in the elapsed time."""
    if elapsed_seconds <= 0 or period_minutes <= 0:
        return 0
    return int(elapsed_seconds // (period_minutes * 60))


# --------------------------------------------------------------------------
# 5. History (list of readings) and ground track
# --------------------------------------------------------------------------
def add_reading(history, reading, max_len=MAX_HISTORY):
    """Append a reading unless it is a repeat of the last one; keep the list short."""
    if history and history[-1]["timestamp"] == reading["timestamp"]:
        return history
    history.append(reading)
    if len(history) > max_len:
        del history[: len(history) - max_len]
    return history


def split_track(readings):
    """Split readings into segments wherever the path wraps around the map edge.

    Longitude jumps from about +180 to -180 when the ISS crosses the
    date line.  If we joined those two points, a line would streak across
    the whole map, so we start a new segment instead."""
    segments = []
    current = []
    previous_lon = None
    for r in readings:                                   # loop over the list
        if previous_lon is not None and abs(r["longitude"] - previous_lon) > 180:
            segments.append(current)
            current = []
        current.append((r["latitude"], r["longitude"]))
        previous_lon = r["longitude"]
    if current:
        segments.append(current)
    return segments


def track_with_gaps(readings):
    """Return (lats, lons) lists with None between segments (Plotly leaves a gap)."""
    lats, lons = [], []
    for i, segment in enumerate(split_track(readings)):
        if i > 0:
            lats.append(None)
            lons.append(None)
        for lat, lon in segment:
            lats.append(lat)
            lons.append(lon)
    return lats, lons


# --------------------------------------------------------------------------
# 6. File handling (CSV)
# --------------------------------------------------------------------------
def reading_to_row(reading):
    return {
        "timestamp": reading["timestamp"],
        "utc": datetime.fromtimestamp(reading["timestamp"], timezone.utc).isoformat(),
        "latitude": round(reading["latitude"], 5),
        "longitude": round(reading["longitude"], 5),
        "altitude_km": round(reading["altitude_km"], 2),
        "velocity_kmh": round(reading["velocity_kmh"], 1),
        "visibility": reading["visibility"],
    }


def save_reading(path, reading):
    """Append one reading to a CSV file.  Returns False if the disk is not writable
    (cloud servers may use temporary or read-only storage)."""
    try:
        folder = os.path.dirname(path)
        if folder:
            os.makedirs(folder, exist_ok=True)
        new_file = not os.path.exists(path) or os.path.getsize(path) == 0
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            if new_file:
                writer.writeheader()
            writer.writerow(reading_to_row(reading))
        return True
    except OSError:
        return False


def load_readings(path):
    """Read a CSV file back into a list of reading dictionaries.
    Rows that cannot be understood are skipped."""
    readings = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                try:
                    readings.append({
                        "timestamp": int(float(row["timestamp"])),
                        "latitude": float(row["latitude"]),
                        "longitude": float(row["longitude"]),
                        "altitude_km": float(row["altitude_km"]),
                        "velocity_kmh": float(row["velocity_kmh"]),
                        "visibility": row.get("visibility", "unknown"),
                    })
                except (KeyError, ValueError, TypeError):
                    continue
    except OSError:
        return []
    return readings


def readings_to_csv_text(readings):
    """CSV text of a list of readings (for a download button)."""
    import io
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS)
    writer.writeheader()
    for r in readings:
        writer.writerow(reading_to_row(r))
    return buffer.getvalue()

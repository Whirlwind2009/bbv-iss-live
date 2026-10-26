"""Create data/sample_readings.csv - a SIMULATED ISS orbit used for the offline replay.

These are NOT real observations.  They come from a simple circular-orbit model
(51.6 degree inclination, 92.9 minute period, 1 reading per minute) so the
exhibit can show a clearly labelled replay if the internet fails.

Run:  python scripts/make_sample_data.py
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import iss_core as core

INCLINATION = math.radians(51.6)
PERIOD_S = 92.9 * 60
EARTH_ROTATION = 360.0 / 86164.0          # degrees of longitude per second
START = 1_767_225_600                    # fixed start time (1 Jan 2026, 00:00 UTC)
LON_START = 72.0                         # start over the Indian Ocean / India region

rows = []
for minute in range(0, 190):             # two orbits
    t = minute * 60
    u = 2 * math.pi * t / PERIOD_S       # angle along the orbit
    lat = math.degrees(math.asin(math.sin(INCLINATION) * math.sin(u)))
    lon_inertial = math.degrees(math.atan2(math.cos(INCLINATION) * math.sin(u), math.cos(u)))
    lon = (LON_START + lon_inertial - EARTH_ROTATION * t + 180) % 360 - 180
    rows.append({
        "timestamp": START + t,
        "latitude": lat, "longitude": lon,
        "altitude_km": 420 + 3 * math.sin(2 * u),
        "velocity_kmh": 27600 + 30 * math.cos(2 * u),
        "visibility": "simulated",
    })

path = os.path.join(os.path.dirname(__file__), "..", "data", "sample_readings.csv")
if os.path.exists(path):
    os.remove(path)
for r in rows:
    core.save_reading(path, r)
print(f"Wrote {len(rows)} simulated readings to {path}")

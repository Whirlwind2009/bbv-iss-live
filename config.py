"""config.py - the few settings a teacher may want to change.

Edit this file on GitHub (pencil icon -> Commit changes); the app redeploys by itself.
"""

# Public web address of the deployed app, e.g. "https://bbv-iss-live.streamlit.app".
# Leave "" to let the app work it out by itself (used for the QR code panel).
APP_URL = ""

# When did the exhibition open?  Used by the "orbit counter".
# Example: "2026-11-14 09:00"  (India time).  Leave None to count from the moment
# each screen was opened.
EXHIBITION_START = None

ORBIT_PERIOD_MIN = 92.9      # average minutes per ISS orbit (NASA quotes "about 90")
ATTRACT_SECONDS = 30         # how long each screen stays up in attract mode
FACT_SECONDS = 10            # how long each "Did you know?" fact stays up

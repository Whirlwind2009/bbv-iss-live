"""Make a QR code PNG for your deployed app.

Run:  python scripts/make_qr.py https://your-app-name.streamlit.app
(needs:  pip install -r requirements-dev.txt)
"""
import sys

import qrcode

if len(sys.argv) != 2:
    sys.exit("Usage: python scripts/make_qr.py <app-url>")
img = qrcode.make(sys.argv[1], box_size=14, border=3)
img.save("qr_code.png")
print("Saved qr_code.png")

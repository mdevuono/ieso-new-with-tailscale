"""
IESO LMP Proxy Server
Serves index.html and proxies CSV fetch requests to reports-public.ieso.ca,
bypassing browser CORS restrictions.

Usage:
    pip install flask requests
    python server.py

Access via Tailscale at: http://<tailscale-ip>:5000
"""

import requests
from flask import Flask, request, Response, send_from_directory
import os

app = Flask(__name__, static_folder=".")

ALLOWED_BASE_URLS = [
    "https://reports-public.ieso.ca/public/DAHourlyEnergyLMP/",
    "https://reports-public.ieso.ca/public/PredispHourlyEnergyLMP/",
]

@app.route("/")
def index():
    """Serve the main HTML file."""
    return send_from_directory(".", "index.html")

@app.route("/fetch-csv")
def fetch_csv():
    """
    Proxy endpoint for IESO CSV files.
    Query param: url=<full ieso csv url>
    Only whitelisted IESO base URLs are allowed.
    """
    url = request.args.get("url")

    if not url:
        return Response("Missing 'url' parameter.", status=400)

    # Whitelist check — only allow IESO report URLs
    if not any(url.startswith(base) for base in ALLOWED_BASE_URLS):
        return Response("URL not allowed.", status=403)

    try:
        ieso_response = requests.get(url, timeout=15)
        ieso_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        return Response(f"IESO returned error: {e}", status=502)
    except requests.exceptions.RequestException as e:
        return Response(f"Failed to fetch from IESO: {e}", status=502)

    return Response(
        ieso_response.content,
        status=200,
        mimetype="text/csv",
        headers={"Access-Control-Allow-Origin": "*"},
    )


if __name__ == "__main__":
    # Listen on all interfaces so Tailscale peers can reach it
    # Change port if 5000 is already in use
    app.run(host="0.0.0.0", port=5000, debug=False)

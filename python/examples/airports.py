"""
Airport lookup, search, and nearest to a coordinate.
GET /airport

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/airports.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# 1. Lookup by IATA or ICAO code.
dxb = fn.airport(code="DXB")
print("Lookup DXB:", dxb["name"], "(" + dxb["icao"] + ")", dxb["city"], dxb["countryName"])
print("  coordinates:", dxb["latitude"], dxb["longitude"], "timezone", dxb["timezone"])

# 2. Text search on name / city / code.
found = fn.airport(search="heathrow")
print("\nSearch heathrow:", [a["iata"] for a in found][:5])

# 3. Nearest airports to a coordinate (radius in km, default 100, max 500).
near = fn.airport(lat=51.47, lon=-0.45, radius=40)
print("\nNearest to 51.47, -0.45:")
for a in near[:5]:
    print(" ", a["iata"], a["name"], round(a["distanceKm"], 1), "km")

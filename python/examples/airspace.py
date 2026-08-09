"""
Live airspace: every aircraft airborne in an area, or inbound to an airport.
GET /airspace

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/airspace.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# Aircraft inbound to JFK, nearest first, with minutes to arrival.
result = fn.airspace(inbound="JFK")

airport = result["airport"]
aircraft = result["aircraft"]
print("Inbound to", airport["iata"], airport["name"], ":", len(aircraft), "aircraft")

for a in aircraft[:8]:
    print(" ", a["callsign"], "alt", a["altitude"], "ft",
          "speed", a["groundSpeed"], "kt",
          round(a["distanceKm"], 1), "km out,", a["etaMinutes"], "min")

# Other ways to query airspace:
#   fn.airspace(lat=40.6, lon=-73.8, radius=60)         within 60 km of a point
#   fn.airspace(bbox="40.4,-74.3,40.9,-73.5")           inside a bounding box
#   fn.airspace(airport="LHR", radius=80)               around an airport

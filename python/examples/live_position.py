"""
Live position of an airborne flight.
GET /track

Returns an empty list if the flight is not airborne right now.

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/live_position.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# Singapore Airlines SQ25.
positions = fn.live_position(name="SQ", num="25")

if not positions:
    print("SQ25 is not airborne right now (empty result, no credit charged).")
else:
    p = positions[0]
    print("SQ25", p["status"], "from", p["departure"]["airportCode"],
          "to", p["arrival"]["airportCode"])
    print("  position:", p["latitude"], p["longitude"], "altitude", p["altitude"], "ft")
    print("  speed:", p["groundSpeed"], "kt  heading", p["heading"], "deg")
    print("  phase:", p["phase"], "progress", round(p["progress"] * 100), "%",
          "source", p["source"])

"""
Tracked flights: a personal watchlist with three arrival anchors.
GET /watch to list, POST /watch to add or remove.

Each tracked flight returns the scheduled arrival, the FlightNerve estimated
arrival, and the live observed arrival, plus cancelled / diverted / arrived flags.

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/watchlist.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# Add a flight to the watchlist (date defaults to today).
fn.watch_add(flight="EK072")

# List tracked flights and their arrival anchors.
result = fn.watchlist()
for t in result.get("tracked", []):
    arrivals = t["arrivals"]
    print(t["flight"], t["day"], t["status"], "flags", t["flags"])
    print("  scheduled:", arrivals["scheduled_utc"])
    print("  fn estimate:", arrivals["fn_estimated_utc"])
    print("  live:", arrivals["live_utc"])

# Stop tracking:
#   fn.watch_remove(flight="EK072")

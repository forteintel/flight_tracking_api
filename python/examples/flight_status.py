"""
Flight status: schedule, route, aircraft and live status for one flight.
GET /airline

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/flight_status.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()   # reads FLIGHTNERVE_API_KEY

# Emirates EK72. Add date="YYYYMMDD" for a specific day, or dep_airport="DXB"
# to pick one leg of a multi leg flight number.
result = fn.flight_status(name="EK", num="72")

departure = result[0]["departure"]
arrival = result[1]["arrival"]
aircraft = result[2]["aircraft"]
status = result[3]["status"]

print("EK72  status:", status)
print("  from:", departure["airportCode"], departure["airportCity"],
      "at", departure["scheduledTime"], "terminal", departure.get("terminal"))
print("  to:  ", arrival["airportCode"], arrival["airportCity"],
      "at", arrival["scheduledTime"], "terminal", arrival.get("terminal"))
print("  aircraft:", aircraft["name"], "tail", aircraft.get("regNumber"))

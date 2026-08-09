"""
Projected timetable for a flight over the coming days.
GET /schedules

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/schedules.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# EK72 projected over 3 days from date (defaults to today when date is omitted).
result = fn.schedules(name="EK", num="72", days=3)

print(result["flight"], "confidence", result["confidence"],
      "from", result["sampleSize"], "observed days")

for day in result["schedules"]:
    if not day["operates"]:
        print(" ", day["date"], day["weekday"], "no service")
        continue
    for leg in day["legs"]:
        print(" ", day["date"], day["weekday"],
              leg["from"], "->", leg["to"],
              leg["departure"]["scheduledLocal"], "->", leg["arrival"]["scheduledLocal"],
              "(" + str(leg["blockMinutes"]) + " min,", leg["aircraft"] + ")")

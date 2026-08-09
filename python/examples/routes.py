"""
Routes: which flights fly a route, an airline network, or one flight's route.
GET /route

Usage:
    export FLIGHTNERVE_API_KEY="your_key_here"
    python examples/routes.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from flightnerve import FlightNerve

fn = FlightNerve()

# 1. Route detail: every flight observed operating DXB -> LHR.
route = fn.route(origin="DXB", destination="LHR")
print("DXB -> LHR:", route["distanceKm"], "km,",
      route["flightCount"], "flights,", route["operatorCount"], "operators")
for f in route["flights"][:6]:
    print(" ", f["flight"], f["airlineName"], "aircraft", f["aircraft"],
          "codeshares", f.get("codeshares"))

# 2. Airline network: every route an airline operates.
network = fn.route(airline="EK")
print("\n" + network["airlineName"], "operates", network["routeCount"], "routes")

# 3. A single flight's route.
one = fn.route(name="EK", num="1")
print("\nEK1 route:", one)

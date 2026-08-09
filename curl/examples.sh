#!/usr/bin/env bash
#
# FlightNerve flight tracking API: cURL examples for every endpoint.
#
# Docs:    https://flightnerve.com/doc/
# Get key: https://flightnerve.com/register/
#
# Usage:
#   export FLIGHTNERVE_API_KEY="your_key_here"
#   bash curl/examples.sh
#
set -euo pipefail

KEY="${FLIGHTNERVE_API_KEY:-YOUR_API_KEY}"
BASE="https://api.flightnerve.com"

echo "== Flight status (GET /airline): EK72 =="
curl -s "$BASE/airline/$KEY?num=72&name=EK"
echo; echo

echo "== Live position (GET /track): SQ25 =="
curl -s "$BASE/track/$KEY?num=25&name=SQ"
echo; echo

echo "== Schedules (GET /schedules): EK72 over 3 days =="
curl -s "$BASE/schedules/$KEY?num=72&name=EK&days=3"
echo; echo

echo "== Airport lookup (GET /airport): DXB =="
curl -s "$BASE/airport/$KEY?code=DXB"
echo; echo

echo "== Airport nearest to a coordinate =="
curl -s "$BASE/airport/$KEY?lat=51.47&lon=-0.45&radius=40"
echo; echo

echo "== Live airspace (GET /airspace): inbound to JFK =="
curl -s "$BASE/airspace/$KEY?inbound=JFK"
echo; echo

echo "== Route detail (GET /route): DXB -> LHR =="
curl -s "$BASE/route/$KEY?from=DXB&to=LHR"
echo; echo

echo "== Tracked flights (GET /watch) =="
curl -s "$BASE/watch/$KEY"
echo; echo

echo "== Add a tracked flight (POST /watch) =="
curl -s -X POST "$BASE/watch/$KEY" \
  -H "Content-Type: application/json" \
  -d '{"flight": "EK072"}'
echo

# How to track a flight with an API

A practical guide to real time flight tracking with the [FlightNerve](https://flightnerve.com) flight tracking API: track a flight by number, read its live position, compute an ETA, watch every aircraft inbound to an airport, and get notified when a flight changes. Every call returns clean JSON and takes one API key in the URL path.

New here? [Get a free key](https://flightnerve.com/register/) (no card) and skim the [endpoint reference](ENDPOINTS.md).

## Contents

* [What flight tracking means](#what-flight-tracking-means)
* [Track a flight by number](#track-a-flight-by-number)
* [Get the live aircraft position](#get-the-live-aircraft-position)
* [How often to poll](#how-often-to-poll)
* [Compute an ETA and progress](#compute-an-eta-and-progress)
* [Track every aircraft inbound to an airport](#track-every-aircraft-inbound-to-an-airport)
* [Build a live flight map](#build-a-live-flight-map)
* [Persistent tracking with a watchlist and webhooks](#persistent-tracking-with-a-watchlist-and-webhooks)
* [Which endpoint should I use?](#which-endpoint-should-i-use)
* [Best practices](#best-practices)

## What flight tracking means

"Tracking a flight" covers three different questions, and a good flight tracking API answers each with its own call:

1. **Is the flight on time, and where does it depart and arrive?** That is the flight status: scheduled and estimated times, gate, terminal, aircraft, and a live status such as `In Air`, `Delayed`, `Arrived`, `Cancelled` or `Diverted`. Use `/airline`.
2. **Where is the aircraft right now?** That is the live position: latitude, longitude, altitude, ground speed, heading, plus flight phase and route progress. Use `/track`.
3. **What is happening in the sky over an area or at an airport?** That is live airspace: every aircraft airborne near a point, inside a box, or inbound to an airport with a live ETA. Use `/airspace`.

The rest of this guide walks through each one.

## Track a flight by number

The most common task is: given a flight number, tell me its status. A flight number is an airline code plus digits. `EK72` is airline `EK` (IATA) or `UAE` (ICAO) with number `72`.

```bash
curl "https://api.flightnerve.com/airline/YOUR_API_KEY?num=72&name=EK"
```

```python
from flightnerve import FlightNerve

fn = FlightNerve()
result = fn.flight_status(name="EK", num="72")
status = result[3]["status"]          # In Air, Arrived, Delayed, Cancelled, Diverted, Scheduled
```

The response is an array: element 0 is the departure leg, element 1 the arrival leg, element 2 the aircraft, element 3 the status. Departure and arrival each carry the scheduled and estimated times (local to the airport), the ISO 8601 time with the airport UTC offset, gate, terminal, and, when the flight is under way, the actual gate out and wheels up times.

The same endpoint answers for past, present and future dates through the `date` parameter (`YYYYMMDD`). See [past, present and future dates](EDGE_CASES.md#past-present-and-future-dates) for how the data behind it changes with the date.

## Get the live aircraft position

To follow the aircraft on a map, ask for its position. `/track` returns a position only when the flight is airborne right now. If it has landed, has not departed, or you ask for another day, you get an empty array `[]` and are charged nothing.

```bash
curl "https://api.flightnerve.com/track/YOUR_API_KEY?num=25&name=SQ"
```

```python
positions = fn.live_position(name="SQ", num="25")
if positions:
    p = positions[0]
    lat, lon = p["latitude"], p["longitude"]
    altitude = p["altitude"]          # feet
    speed = p["groundSpeed"]          # knots
    heading = p["heading"]            # degrees true
    phase = p["phase"]                # climb, cruise, descent
    progress = p["progress"]          # 0..1 fraction of the route flown
```

The `source` field tells you the quality of the fix:

| `source` | Meaning |
|----------|---------|
| `live` | A real position fix. |
| `partner` | A derived fix filling a coverage gap. |
| `estimated` | A dead reckoned position, projected along the route by progress, when no fix is available. |

An airborne flight always returns a position. Over land and busy airspace that is a real `live` fix; over a remote ocean it may be `estimated` until the aircraft is back in coverage. Read the [coverage gaps edge case](EDGE_CASES.md#coverage-gaps-and-estimated-positions) for how to handle this in your UI.

## How often to poll

A position fix carries its own age so you never guess how fresh it is:

* `updatedUnix` is the epoch second of the fix. Subtract it from the current time for the age in seconds.
* `updatedAgo` is that age in words, for example `"2 min ago"`.
* `updatedAt` is the same fix as an ISO 8601 UTC timestamp.

A sensible polling interval for a moving aircraft is every 15 to 60 seconds. Faster than the underlying update rate just spends credits redrawing the same fix. Read `updatedUnix` and skip a redraw when it has not changed.

```python
import time

last = None
while True:
    pos = fn.live_position(name="SQ", num="25")
    if not pos:
        break                         # landed or not airborne, stop polling
    fix = pos[0]
    if fix["updatedUnix"] != last:
        last = fix["updatedUnix"]
        draw(fix["latitude"], fix["longitude"], fix["heading"])
    time.sleep(30)
```

## Compute an ETA and progress

For a flight you are tracking, there are two complementary signals:

* `progress` on `/track` is the fraction of the route already flown, `0` at departure and `1` at arrival. Multiply by the great circle distance for a rough distance flown, or use it to place a marker along the route line.
* The arrival leg on `/airline` carries `estimatedTime` and, en route, `timeRemaining`. For a continuously maintained arrival estimate across the whole flight, add the flight to your [watchlist](#persistent-tracking-with-a-watchlist-and-webhooks), which returns a scheduled, an estimated and a live arrival time side by side.

## Track every aircraft inbound to an airport

To power an arrivals board or an approach map, ask which aircraft are routed to an airport right now. Each carries its distance and estimated minutes out, nearest first.

```bash
curl "https://api.flightnerve.com/airspace/YOUR_API_KEY?inbound=JFK"
```

```python
result = fn.airspace(inbound="JFK")
for a in result["aircraft"]:
    print(a["callsign"], a["distanceKm"], "km", a["etaMinutes"], "min out")
```

## Build a live flight map

For a map, query airspace by area instead of by airport. Three shapes are supported:

```python
# within 100 km of a point (radius default 100, max 500)
fn.airspace(lat=40.64, lon=-73.78, radius=100)

# inside a bounding box: latMin, lonMin, latMax, lonMax
fn.airspace(bbox="40.4,-74.3,40.9,-73.5")

# around an airport
fn.airspace(airport="LHR", radius=80)
```

Each aircraft carries `latitude`, `longitude`, `altitude`, `groundSpeed`, `heading`, `onGround`, `originCountry`, and `updatedUnix`. Redraw on your own interval and use `updatedUnix` to fade markers whose fix is going stale.

## Persistent tracking with a watchlist and webhooks

The calls above are one shot lookups. To follow a flight from gate to gate without polling it yourself, add it to your watchlist. Each tracked flight is monitored continuously and returns three arrival anchors so you can show a schedule, an estimate and the live truth together:

```python
fn.watch_add(flight="EK072")          # date defaults to today

for t in fn.watchlist()["tracked"]:
    a = t["arrivals"]
    print(t["flight"], t["status"], t["flags"])   # flags: cancelled, diverted, arrived
    print("scheduled  ", a["scheduled_utc"])
    print("fn estimate", a["fn_estimated_utc"])
    print("live       ", a["live_utc"])
```

Pair a watchlist with a webhook so your system is pushed an update when a flight departs, is delayed, diverts or arrives, instead of polling. See the [monitoring and webhooks docs](https://flightnerve.com/doc/) for the notification payload.

## Which endpoint should I use?

| Your question | Endpoint |
|---------------|----------|
| Is `EK72` on time? Gate, terminal, times, status. | `/airline` |
| Where is `SQ25` right now on a map? | `/track` |
| What is inbound to `JFK`? Arrivals board. | `/airspace?inbound=JFK` |
| Every aircraft over this area for a live map. | `/airspace?bbox=` or `?lat=&lon=` |
| Will `EK72` fly next Tuesday, and at what time? | `/schedules` |
| What flights connect `DXB` and `LHR`, on what aircraft? | `/route?from=DXB&to=LHR` |
| Follow a flight to arrival without polling. | `/watch` plus a webhook |

## Best practices

* **Handle the empty position.** `/track` returns `[]` for a flight that is not airborne. That is normal and free, not an error. Stop polling when you see it.
* **Trust the fix age.** Use `updatedUnix` to decide whether to redraw and to fade stale markers. Do not assume every poll is a new fix.
* **Match your poll rate to the data.** Every 15 to 60 seconds is plenty for a moving aircraft. Faster only spends credits.
* **Cache completed flights.** A past flight is a final, unchanging record. Look it up once and store it.
* **Pick the right call.** Status, position and airspace answer different questions. Do not poll `/airline` to draw a map, or `/track` to read a gate.
* **Read the edge cases.** Multi leg flights, codeshares, cancellations, diversions, timezones and coverage gaps all have defined behaviour. They are covered in the [edge cases guide](EDGE_CASES.md).

## Related

* [Endpoint reference](ENDPOINTS.md)
* [Edge cases guide](EDGE_CASES.md)
* [FlightNerve API documentation](https://flightnerve.com/doc/)
* [Get a free API key](https://flightnerve.com/register/)

_Last reviewed: 2026-08-26._

# FlightNerve Flight Tracking API

A developer resource for the [FlightNerve](https://flightnerve.com) flight tracking API: real time **flight status**, **live aircraft position**, **flight schedules**, **airport data**, **live airspace**, and **routes**, all as clean JSON from one REST call. Guides, edge cases, a full endpoint reference, and ready to run code in Python, JavaScript and cURL.

[![Docs](https://img.shields.io/badge/docs-flightnerve.com%2Fdoc-0ea5a4)](https://flightnerve.com/doc/)
[![Get an API key](https://img.shields.io/badge/get%20a%20key-free-ff5a1f)](https://flightnerve.com/register/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

> Public, open resource for the FlightNerve REST API. It documents how to track flights with the API and how to handle real world edge cases, with runnable code. There is no server code and no API keys here. Bring your own key from [flightnerve.com](https://flightnerve.com/register/). The free tier needs no card.

## Guides

Start here. These are the core of this repository:

* **[How to track a flight with an API](docs/FLIGHT_TRACKING.md)**: track a flight by number, read its live position, compute an ETA, watch every aircraft inbound to an airport, build a live map, and follow a flight to arrival with a watchlist and webhooks.
* **[Flight tracking API edge cases](docs/EDGE_CASES.md)**: multi leg flights, codeshares, IATA vs ICAO codes, cancellations, diversions, delays, flights that cross midnight, coverage gaps, timezones, charter flights, and error handling. How the API behaves in each, so your integration does not guess.
* **[Endpoint reference](docs/ENDPOINTS.md)**: every endpoint, its parameters and an example response.

## What is FlightNerve?

FlightNerve is a real time flight data API. One request returns a flight's live status, position, schedule, route and aircraft, worldwide. It is a clean JSON REST API with:

* **Live flight status** by flight number: schedule, gate, terminal, times, aircraft, and live status (`In Air`, `Arrived`, `Delayed`, `Cancelled`, `Diverted`).
* **Live aircraft position**: latitude, longitude, altitude, speed, heading, flight phase and route progress.
* **Flight schedules**: a projected timetable for a flight over the coming days.
* **Airports**: lookup, search, and nearest to a coordinate across 85,000+ airports.
* **Live airspace**: every aircraft airborne in an area, or inbound to an airport with a live ETA.
* **Routes**: which flights fly a route, an airline's whole network, or one flight's route, with aircraft types and codeshares.
* **Tracked flights and webhooks**: keep a watchlist and get notified when a flight changes.

Base URL: `https://api.flightnerve.com`. Full reference: [flightnerve.com/doc](https://flightnerve.com/doc/).

## Quickstart

Get a free key at [flightnerve.com/register](https://flightnerve.com/register/), then track a flight in one call:

**cURL**

```bash
curl "https://api.flightnerve.com/airline/YOUR_API_KEY?num=72&name=EK"
```

**Python**

```python
from flightnerve import FlightNerve

fn = FlightNerve("YOUR_API_KEY")          # or set FLIGHTNERVE_API_KEY
status = fn.flight_status(name="EK", num="72")
print(status)
```

**JavaScript / Node (18+)**

```js
import { FlightNerve } from "./flightnerve.js";

const fn = new FlightNerve("YOUR_API_KEY"); // or set FLIGHTNERVE_API_KEY
const status = await fn.flight_status({ name: "EK", num: "72" });
console.log(status);
```

Every request takes your API key in the URL path (`/endpoint/<api_key>?...`). Each call costs one credit. The free tier starts with 100.

## Authentication

The API key goes in the path, not a header:

```
https://api.flightnerve.com/<endpoint>/<api_key>?param=value
```

Keep your key out of source control. The code here reads it from the `FLIGHTNERVE_API_KEY` environment variable. Copy [`.env.example`](.env.example) to `.env` and drop your key in.

```bash
export FLIGHTNERVE_API_KEY="your_key_here"
```

## Endpoints at a glance

| Endpoint | What it does | Key parameters |
|----------|--------------|----------------|
| [`GET /airline`](docs/ENDPOINTS.md#flight-status) | Flight status: schedule, route, aircraft, live status | `name`, `num`, `date?`, `depap?` |
| [`GET /track`](docs/ENDPOINTS.md#live-position) | Live position of an airborne flight | `name`, `num`, `date?` |
| [`GET /schedules`](docs/ENDPOINTS.md#flight-schedules) | Projected timetable over N days | `name`, `num`, `date?`, `days?` |
| [`GET /airport`](docs/ENDPOINTS.md#airports) | Airport lookup, search, or nearest | `code` or `search` or `lat`+`lon`+`radius?` |
| [`GET /airspace`](docs/ENDPOINTS.md#live-airspace) | Live airspace in an area or inbound | `lat`+`lon` or `bbox` or `airport` or `inbound` |
| [`GET /route`](docs/ENDPOINTS.md#routes) | Routes: route detail, network, destinations | `from`+`to` or `airline` or `from` or `to` or `name`+`num` |
| [`GET/POST /watch`](docs/ENDPOINTS.md#tracked-flights) | Tracked flights watchlist with arrival anchors | `flight`, `date?`, `leg?` |

Full request and response detail for each is in [docs/ENDPOINTS.md](docs/ENDPOINTS.md) and on [flightnerve.com/doc](https://flightnerve.com/doc/).

## Ready to run code

A thin client and one runnable script per endpoint, in three languages:

```
python/
  flightnerve.py            client (requests)
  examples/                 one script per endpoint
javascript/
  flightnerve.js            fetch based client (Node 18+)
  examples/
curl/
  examples.sh               cURL calls for every endpoint
docs/
  FLIGHT_TRACKING.md        guide: how to track a flight
  EDGE_CASES.md             guide: real world edge cases
  ENDPOINTS.md              endpoint reference
```

Run the Python scripts:

```bash
cd python
pip install -r requirements.txt
export FLIGHTNERVE_API_KEY="your_key_here"
python examples/flight_status.py
```

Run the JavaScript scripts:

```bash
cd javascript
export FLIGHTNERVE_API_KEY="your_key_here"
node examples/flight_status.js
```

## Common use cases

* **Flight status widget**: show a passenger the gate, terminal, and live status of `EK72` (`/airline`).
* **Live map**: plot every aircraft inbound to `JFK` with minutes to arrival (`/airspace?inbound=JFK`).
* **Trip planner**: project a flight's timetable for the next week (`/schedules`).
* **Airport picker**: find the nearest airports to a set of coordinates (`/airport?lat=..&lon=..`).
* **Route explorer**: list every flight and aircraft type between two cities (`/route?from=DXB&to=LHR`).
* **Delay alerts**: track a flight and get a webhook when it departs, diverts, or arrives (`/watch`).

## FAQ

**Do I need a credit card?** No. Create an account, generate a key, and you get free call credits immediately.

**What flight number format?** Airline code plus digits. For example `EK72` is `name=EK` (IATA) or `name=UAE` (ICAO) with `num=72`. Leading zeros do not matter (`EK072` is `EK72`).

**Which dates work?** `/airline` and `/schedules` answer for past, present and future dates (`YYYYMMDD`). `/track` only returns a position for a flight that is airborne right now. See the [edge cases guide](docs/EDGE_CASES.md#past-present-and-future-dates).

**A flight returned a 400. Why?** The flight does not operate on that date, or the airline code or number is wrong. See [flights that do not operate](docs/EDGE_CASES.md#flights-that-do-not-operate-on-a-date).

**What does a call cost?** One credit per call (per leg for multi leg flights, per operating day for `/schedules`). A `/track` for a flight that is not airborne returns `[]` and costs nothing.

## Links

* Website: https://flightnerve.com
* API documentation: https://flightnerve.com/doc/
* Get an API key (free): https://flightnerve.com/register/
* Pricing: https://flightnerve.com/pricing/

## License

[MIT](LICENSE). Use this freely. FlightNerve and the FlightNerve API are property of FlightNerve. Your use of the API is governed by the [FlightNerve terms](https://flightnerve.com/terms/).

_Last reviewed: 2026-08-25._

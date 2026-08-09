# FlightNerve API endpoint reference

Base URL: `https://api.flightnerve.com`

Every request takes your API key in the path: `/<endpoint>/<api_key>?param=value`. Get a free key at [flightnerve.com/register](https://flightnerve.com/register/). The full interactive reference lives at [flightnerve.com/doc](https://flightnerve.com/doc/); this page mirrors it for quick reference.

Note: the JSON field names below (for example `departureDateTime`, `groundSpeed`) are returned by the API exactly as shown.

## Flight status

Full schedule, route, aircraft and status for a single flight on a given date.

`GET /airline/<api_key>`

| Param | Required | Description |
|-------|----------|-------------|
| `num` | required | Flight number, digits only (for example `72` for EK72). |
| `name` | required | Airline code, IATA (`EK`) or ICAO (`UAE`). |
| `date` | optional | Target date, `YYYYMMDD`. Defaults to the active or next instance. |
| `depap` | optional | Departure airport IATA. Picks one leg of a multi leg flight (the leg departing this airport). |

Some flight numbers cover more than one leg. For example `EK205` flies DXB, MXP, JFK. Called without `depap`, a multi leg flight returns all legs as an array and is billed one credit per leg.

```bash
curl "https://api.flightnerve.com/airline/YOUR_API_KEY?num=72&name=EK&date=20260720"
```

Example response:

```json
[
  { "departure": {
      "departureDateTime": "2026-07-20T11:30:00+02:00",
      "airport": "Charles de Gaulle", "airportCity": "Paris",
      "airportCode": "CDG", "airportCountryCode": "FR",
      "scheduledTime": "11:20, Jul 20", "estimatedTime": "11:30, Jul 20",
      "terminal": "2C", "gate": null, "duration": "7 hr"
  }},
  { "arrival": {
      "arrivalDateTime": "2026-07-20T20:20:00+04:00",
      "airport": "Dubai Int'l", "airportCity": "Dubai",
      "airportCode": "DXB", "airportCountryCode": "AE",
      "scheduledTime": "20:20, Jul 20", "estimatedTime": "20:20, Jul 20",
      "terminal": "3", "gate": null, "baggage": null
  }},
  { "aircraft": { "code": "388", "name": "Airbus A380-800", "regNumber": "A6-EOA" } },
  { "status": "In Air" }
]
```

Status values: `Scheduled`, `In Air`, `Arrived`, `Delayed`, `Cancelled`, `Diverted`. The same endpoint answers for past, present and future dates. If a flight does not operate on the requested day, a `400` is returned.

## Live position

Where the aircraft is right now: latitude, longitude, altitude, ground speed, heading, plus `phase` and `progress`. Returns an empty array `[]` if the flight is not airborne (a completed flight, one not yet departed, or a future date). Billed one credit per position returned, so a flight that is not in the air costs nothing.

`GET /track/<api_key>`

| Param | Required | Description |
|-------|----------|-------------|
| `num` | required | Flight number, digits only (for example `25` for SQ25). |
| `name` | required | Airline code, IATA (`SQ`) or ICAO (`SIA`). |
| `date` | optional | Target date, `YYYYMMDD`. Only today can be airborne. |

```bash
curl "https://api.flightnerve.com/track/YOUR_API_KEY?num=25&name=SQ"
```

Example response (airborne):

```json
[
  {
    "flight": "SQ25", "callsign": "SIA25", "status": "In Air",
    "regNumber": "9V-SMR",
    "latitude": 59.8835, "longitude": 36.571,
    "altitude": 33000, "groundSpeed": 560, "heading": 120,
    "onGround": false, "phase": "cruise", "progress": 0.62,
    "source": "live",
    "departure": { "airportCode": "FRA", "airport": "Frankfurt Int'l" },
    "arrival":   { "airportCode": "SIN", "airport": "Singapore Changi" },
    "updatedUnix": 1784646407
  }
]
```

`source` is `live` (a real fix), `partner` (a derived fix filling a coverage gap), or `estimated` (dead reckoned along the route when no fix is available).

## Flight schedules

The projected timetable for a flight over the coming days, built from FlightNerve's own accumulated operating history for that flight. One entry per day: route, scheduled departure and arrival (local and UTC), block time and typical aircraft, and whether the flight is expected to operate that weekday.

`GET /schedules/<api_key>`

| Param | Required | Description |
|-------|----------|-------------|
| `num` | required | Flight number, digits only. |
| `name` | required | Airline code, IATA or ICAO. |
| `date` | optional | Start date, `YYYYMMDD`. Defaults to today. |
| `days` | optional | Days to project, `1` to `7`. Defaults to `1`. |

```bash
curl "https://api.flightnerve.com/schedules/YOUR_API_KEY?num=72&name=EK&date=20260725&days=3"
```

Example response:

```json
{
  "flight": "EK72", "callsign": "UAE72",
  "basis": "historical-pattern",
  "sampleSize": 17, "confidence": "high", "days": 3,
  "schedules": [
    {
      "date": "2026-07-25", "weekday": "Sat", "operates": true,
      "legs": [
        { "from": "CDG", "to": "DXB", "fromCity": "Paris", "toCity": "Dubai",
          "departure": { "scheduledLocal": "11:20", "scheduledUTC": "2026-07-25T09:20:00Z" },
          "arrival":   { "scheduledLocal": "20:55", "scheduledUTC": "2026-07-25T16:55:00Z" },
          "blockMinutes": 455, "aircraft": "A388" }
      ]
    },
    { "date": "2026-07-27", "weekday": "Mon", "operates": false }
  ]
}
```

`confidence` is `high`, `medium`, or `low`. Billed one credit per operating day returned; days with no service are free.

## Airports

Look up an airport, search by name or city, or find airports near a coordinate, from a reference of 85,000+ airports worldwide with coordinates and timezone.

`GET /airport/<api_key>` (use one of):

| Param | Description |
|-------|-------------|
| `code` | IATA or ICAO code; returns one airport (for example `code=DXB` or `code=OMDB`). |
| `search` | Text match on name, city or code; returns a list (for example `search=heathrow`). |
| `lat` and `lon` | Airports within `radius` km of a point, nearest first. `radius` optional (default 100, max 500). |

```bash
curl "https://api.flightnerve.com/airport/YOUR_API_KEY?code=DXB"
```

```json
{
  "iata": "DXB", "icao": "OMDB", "name": "Dubai International Airport",
  "city": "Dubai", "country": "AE", "countryName": "United Arab Emirates",
  "latitude": 25.2528, "longitude": 55.3644, "timezone": "Asia/Dubai"
}
```

## Live airspace

Every aircraft in the air right now in an area: near a point, inside a bounding box, around an airport, or inbound to an airport with a live ETA.

`GET /airspace/<api_key>` (use one of):

| Param | Description |
|-------|-------------|
| `lat` and `lon` | Aircraft within `radius` km of a point (default 100, max 500), nearest first. |
| `bbox` | Aircraft inside `latMin,lonMin,latMax,lonMax`. |
| `airport` | Aircraft within `radius` km of an airport (IATA or ICAO). |
| `inbound` | Airborne aircraft routed to this airport, with distance and estimated minutes out. |

```bash
curl "https://api.flightnerve.com/airspace/YOUR_API_KEY?inbound=JFK"
```

```json
{ "airport": { "iata": "JFK", "icao": "KJFK", "name": "John F. Kennedy International Airport" },
  "aircraft": [
    { "callsign": "AAL1185", "latitude": 40.7, "longitude": -73.9,
      "altitude": 4000, "groundSpeed": 210, "heading": 31, "onGround": false,
      "originCountry": "United States", "distanceKm": 9.6, "etaMinutes": 2 }
  ] }
```

## Routes

Answers four route questions from FlightNerve's own accumulated operating history, each enriched with the aircraft types actually seen and any codeshare flight numbers.

`GET /route/<api_key>` (use one of):

| Param | Returns |
|-------|---------|
| `from` and `to` | Route detail: every flight observed operating A to B, with airline, flight number, aircraft, codeshares, days observed, and the route distance. |
| `airline` | Airline network: every route the airline operates (IATA or ICAO). |
| `from` | Destinations served from an airport. |
| `to` | Origins that reach an airport. |
| `num` and `name` | A single flight: origin, destination, stops, aircraft and codeshares. |

```bash
curl "https://api.flightnerve.com/route/YOUR_API_KEY?from=DXB&to=LHR"
```

```json
{ "from": { "iata": "DXB", "city": "Dubai" },
  "to":   { "iata": "LHR", "city": "London" },
  "distanceKm": 5498,
  "airlines": ["EK"], "operatorCount": 1, "flightCount": 3,
  "flights": [
    { "flight": "EK1", "airline": "EK", "airlineName": "Emirates",
      "aircraft": ["A388", "B38M"], "codeshares": ["GA8887"],
      "daysObserved": 14, "lastSeen": "2026-07-25" }
  ] }
```

## Tracked flights

Keep a personal watchlist of flights. Each is monitored continuously and returns three arrival anchors: the scheduled time, the FlightNerve estimated arrival, and the live observed arrival, plus `cancelled`, `diverted` and `arrived` flags.

List tracked flights:

`GET /watch/<api_key>`

```bash
curl "https://api.flightnerve.com/watch/YOUR_API_KEY"
```

```json
{ "success": true, "tracked": [
  { "flight": "EK072", "day": "20260722", "leg": null,
    "route": { "from": "OMDB", "to": "VTBS" },
    "status": "active", "flags": [],
    "arrivals": {
      "scheduled_utc":    "2026-07-22T20:43:00Z",
      "fn_estimated_utc": "2026-07-22T20:41:12Z",
      "live_utc":         "2026-07-22T20:42:00Z" },
    "fn_source": "blend",
    "live": { "phase": "cruise", "progress": 0.41, "dist_rem_km": 3074 } }
] }
```

Add or remove a flight:

`POST /watch/<api_key>`

| Body field | Description |
|------------|-------------|
| `flight` | Flight number, for example `EK072`. Required to add. |
| `date` | `YYYYMMDD`, the day to track. Defaults to today. |
| `leg` | Optional `DEP-ARR` (ICAO) to pin one leg of a multi leg flight. |
| `action` | Set to `remove` to stop tracking (with `id` or `flight`). |

```bash
curl -X POST "https://api.flightnerve.com/watch/YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"flight": "EK072", "date": "20260722"}'
```

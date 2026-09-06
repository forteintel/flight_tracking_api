# Flight tracking API edge cases

Real flights are messy. They have multiple legs, codeshares, cancellations, diversions, delays, timezones and coverage gaps, and airline codes are not always unique. This guide documents how the [FlightNerve](https://flightnerve.com) flight tracking API behaves in each of these cases, so your integration handles them correctly instead of guessing.

Every example takes one API key in the URL path. [Get a free key](https://flightnerve.com/register/) and see the [endpoint reference](ENDPOINTS.md) for the full parameter list.

## Contents

* [Multi leg flights](#multi-leg-flights)
* [Codeshares: operating vs marketing flight numbers](#codeshares-operating-vs-marketing-flight-numbers)
* [IATA vs ICAO airline codes](#iata-vs-icao-airline-codes)
* [Zero padded flight numbers](#zero-padded-flight-numbers)
* [Shared and ambiguous airline codes](#shared-and-ambiguous-airline-codes)
* [Flights that do not operate on a date](#flights-that-do-not-operate-on-a-date)
* [Cancelled flights](#cancelled-flights)
* [Diverted flights](#diverted-flights)
* [Delayed flights](#delayed-flights)
* [Flights that cross midnight](#flights-that-cross-midnight)
* [Past, present and future dates](#past-present-and-future-dates)
* [A flight that is not airborne](#a-flight-that-is-not-airborne)
* [The aircraft registration is null](#the-aircraft-registration-is-null)
* [Coverage gaps and estimated positions](#coverage-gaps-and-estimated-positions)
* [Timezones and local vs UTC time](#timezones-and-local-vs-utc-time)
* [Charter and low frequency flights](#charter-and-low-frequency-flights)
* [Airport code ambiguity](#airport-code-ambiguity)
* [Errors, status codes and credits](#errors-status-codes-and-credits)

## Multi leg flights

A single flight number can cover more than one leg. For example `EK205` flies DXB, then MXP, then JFK. That one number is two legs: DXB to MXP and MXP to JFK.

Call `/airline` **without** `depap` and a multi leg flight returns **every leg**, as an array of leg objects in order, billed one credit per leg:

```bash
curl "https://api.flightnerve.com/airline/YOUR_API_KEY?num=205&name=EK"
```

Pin a single leg by its **departure airport** with `depap`:

```python
fn.flight_status(name="EK", num="205", dep_airport="DXB")   # DXB to MXP
fn.flight_status(name="EK", num="205", dep_airport="MXP")   # MXP to JFK
```

If your app only ever wants one leg, always send `depap`. It removes ambiguity and bills a single credit.

## Codeshares: operating vs marketing flight numbers

The same physical flight is often sold under several flight numbers. One airline **operates** the aircraft; others **market** seats on it under their own code. `SQ25` operated by Singapore Airlines may also be sold as a Lufthansa or Air New Zealand number.

Track the **operating** number for the truest live data. When you look up a route, the `/route` response lists the operating flight and its `codeshares` so you can map a marketing number back to the metal:

```json
{ "flight": "EK1", "airline": "EK", "airlineName": "Emirates",
  "aircraft": ["A388", "B38M"], "codeshares": ["GA8887"] }
```

If a user gives you a marketing number, resolve it to the operating flight (via the route, or your own mapping) before tracking the position.

## IATA vs ICAO airline codes

Airlines have a two character IATA code and a three character ICAO code. The `name` parameter accepts either:

| Airline | IATA | ICAO |
|---------|------|------|
| Emirates | `EK` | `UAE` |
| Singapore Airlines | `SQ` | `SIA` |
| American Airlines | `AA` | `AAL` |

`name=EK` and `name=UAE` resolve to the same airline. ICAO is unambiguous; IATA is shorter and more common in consumer contexts. If you ever hit an [ambiguous IATA code](#shared-and-ambiguous-airline-codes), switch to ICAO.

## Zero padded flight numbers

Flight numbers are often written with leading zeros: `EK072` on a boarding pass is flight `72`. The `num` parameter is the numeric part, so `num=72` and `num=072` are the same flight. Strip or keep the zeros as you like. When you build a full flight code for display, `EK72` and `EK072` refer to the same flight.

## Shared and ambiguous airline codes

A few IATA codes are shared by more than one airline, usually one active and one defunct or regional. For example `E4` has been assigned to both Enter Air (ICAO `ENT`) and, historically, Abaeté Linhas Aereas (ICAO `ABJ`).

When you query a shared IATA code, the API resolves it to the airline that actually has data for the flight you asked for, so real flights resolve correctly. But if a flight number genuinely does not exist under any interpretation (for example a low number on a charter carrier whose flights are numbered in the thousands), you will get a [does not operate](#flights-that-do-not-operate-on-a-date) response.

To remove all doubt, pass the **ICAO** code in `name` (for example `name=ENT`). ICAO codes are unique per airline.

## Flights that do not operate on a date

If you ask `/airline` for a flight on a day it does not fly, the API returns a `400` with a JSON body:

```json
{ "success": false,
  "message": "Either your date is wrong or airline code is wrong. Please verify the flight number and date." }
```

This is the expected answer for a flight number that does not run that weekday, a made up number, or a wrong airline code. Treat a `400` here as "no such flight on that day", not as a server error. Before assuming a flight is missing, double check the airline code and that the number really operates on the requested date.

## Cancelled flights

A cancelled flight returns normally with `status` set to `Cancelled`. The schedule fields are still present (the flight that would have run), but there are no actual departure or arrival times. Check `status` before showing a passenger an ETA.

```python
result = fn.flight_status(name="EK", num="72", date="20260722")
if result[3]["status"] == "Cancelled":
    show_cancelled()
```

## Diverted flights

A diverted flight lands somewhere other than its planned destination. Its `status` is `Diverted`. The live position from `/track` follows the aircraft to where it actually goes, so the arrival airport in a position fix can differ from the originally scheduled destination. Do not assume the arrival airport is fixed once a flight is `Diverted`.

## Delayed flights

Delay is the gap between the scheduled and estimated departure. A flight reads `Delayed` when its estimated departure is 15 or more minutes behind schedule, before it leaves. Compare the departure leg fields yourself for the exact minutes:

```python
dep = fn.flight_status(name="EK", num="72")[0]["departure"]
scheduled = dep["scheduledTime"]      # local, "HH:MM, Mon DD"
estimated = dep["estimatedTime"]      # local
# or parse the ISO fields departureDateTime / estimatedTime for exact math
```

Once airborne, a flight is `In Air` rather than `Delayed`, and the arrival leg carries the running estimate.

## Flights that cross midnight

Long haul and eastbound flights often depart on one calendar day and arrive on the next, and the departure and arrival are in different timezones. The API pins each flight to its **local operating date** and returns each time both as a local string and as an ISO 8601 value with the airport UTC offset, so you never have to guess which day a time belongs to.

When you request a `date`, it refers to the local **departure** date. A flight that departs late and lands after midnight is still that one flight on its departure date. Use the ISO `departureDateTime` and `arrivalDateTime` (or the UTC fields on `/schedules`) for correct duration math across the date boundary.

## Past, present and future dates

The same `/airline` endpoint answers for any date, and the data behind it adapts:

| When | What you get |
|------|--------------|
| Today or near term | Live status and times: actual gate out and wheels up, estimates, gate and terminal. |
| Past | The final record: actual departure and arrival times and the terminal status (`Arrived`, `Cancelled`, `Diverted`). Completed flights are cached, so repeat lookups are instant. |
| Upcoming | The scheduled times. Beyond the published window, the recurring schedule is projected from recent history and returned as `Scheduled`. |

For a future date, projected times estimate the recurring schedule and may differ by a few minutes from a later timetable change; the route, aircraft and weekday pattern are accurate. For a firm future timetable across several days, use [`/schedules`](ENDPOINTS.md#flight-schedules).

## A flight that is not airborne

`/track` returns a position only for a flight that is airborne right now. For a completed flight, one that has not departed, or any other day, it returns an **empty array** `[]` and charges nothing:

```python
positions = fn.live_position(name="EK", num="72")
if not positions:
    # not airborne: landed, not departed yet, or a past or future date
    use_schedule_instead()
```

This is not an error. It is how you know the aircraft is not currently in the air. For gate, terminal, times and status before, during or after the flight, use `/airline`.

## The aircraft registration is null

`regNumber` is the tail number of the specific aircraft flying, identified live while it is airborne. Before departure, and for a completed past flight, it can be `null` because there is no live aircraft to identify. Expect `null` and fall back to the aircraft type (`aircraft.code`, `aircraft.name`) for display when it is missing.

## Coverage gaps and estimated positions

Live position coverage follows signal reception: excellent over land and busy airspace, with gaps over remote oceans and some remote regions. An airborne flight **always** returns a position, but in a gap the position is dead reckoned along the route and the `source` field is `estimated` (or `partner` for a derived fix). The `updated*` fix time fields are null for an `estimated` position.

Handle it in your UI: show a solid marker for a `live` fix and a dimmed or dashed marker for an `estimated` one, and lean on `progress` to place the aircraft along the route line until a real fix returns.

```python
p = fn.live_position(name="SQ", num="25")[0]
if p["source"] == "estimated":
    marker.set_style("dashed")     # projected, not a real fix
```

## Timezones and local vs UTC time

Departure and arrival times are **local to their airport**. `scheduledTime` and `estimatedTime` are human strings in local time (`"HH:MM, Mon DD"`). Alongside them, `departureDateTime` and `arrivalDateTime` are ISO 8601 with the airport UTC offset, and `/schedules` gives both `scheduledLocal` and `scheduledUTC`. Position fix times (`updatedAt`, `updatedUnix`) are UTC.

For any cross airport math (duration, delay across a boundary), use the ISO or UTC fields, not the local display strings. The airport reference on `/airport` includes the IANA `timezone` if you need to localise further.

## Charter and low frequency flights

Data is richest on scheduled, well trafficked flights. Charter carriers and low frequency routes fly irregularly, so their history is sparse. On `/schedules` this shows up as a lower `confidence` (`low`) and a smaller `sampleSize`; treat a `low` projection as indicative. On `/route`, coverage grows over time and is thinnest on rarely flown city pairs. A charter flight number that has never been observed operating may return [does not operate](#flights-that-do-not-operate-on-a-date).

## Airport code ambiguity

Airports also have IATA (three letter) and ICAO (four letter) codes: `DXB` and `OMDB` are the same airport. `/airport?code=` accepts either. A **search** (`/airport?search=heathrow`) returns a **list**, since a name or city can match several airports, so handle an array and let the user pick. A **coordinate** query (`lat` and `lon`) returns airports nearest first, each with `distanceKm`.

## Errors, status codes and credits

Non success responses come back as JSON with `success: false` and a human `message`. Common cases:

| Status | Meaning | What to do |
|--------|---------|------------|
| `400` | The flight does not operate on that date, or the airline or number is wrong. | Verify the airline code, number and date. Not a server fault. |
| `401` | Missing or invalid API key. | Check the key in the URL path. |
| `429` | Too many requests in a short window. | Back off and retry after a short pause. |

Billing is one credit per call, with defined exceptions: a multi leg `/airline` bills per leg, `/schedules` bills per operating day returned (days with no service are free), and `/track` for a flight that is not airborne returns `[]` and costs nothing. Wrap calls in error handling and read `message` for the reason.

```python
from flightnerve import FlightNerve, FlightNerveError

try:
    result = fn.flight_status(name="E4", num="6")
except FlightNerveError as e:
    if e.status == 400:
        print("No such flight on that date:", e.message)
    else:
        raise
```

## Related

* [How to track a flight with an API](FLIGHT_TRACKING.md)
* [Endpoint reference](ENDPOINTS.md)
* [FlightNerve API documentation](https://flightnerve.com/doc/)
* [Get a free API key](https://flightnerve.com/register/)

_Last reviewed: 2026-09-06._

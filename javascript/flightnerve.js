// Minimal JavaScript client for the FlightNerve flight tracking API.
//
// Docs:    https://flightnerve.com/doc/
// Get key: https://flightnerve.com/register/
//
// Node 18+ (uses the built in fetch). No dependencies. The API key goes in the
// URL path. Set it with FLIGHTNERVE_API_KEY, or pass it to new FlightNerve(...).

const BASE_URL = "https://api.flightnerve.com";

export class FlightNerveError extends Error {
  constructor(status, message) {
    super(`[${status}] ${message}`);
    this.name = "FlightNerveError";
    this.status = status;
  }
}

function clean(params) {
  const out = {};
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null) out[k] = String(v);
  }
  return out;
}

export class FlightNerve {
  constructor(api_key, base_url = BASE_URL) {
    this.api_key = api_key || process.env.FLIGHTNERVE_API_KEY;
    if (!this.api_key) {
      throw new Error(
        "No API key. Set FLIGHTNERVE_API_KEY or pass it to new FlightNerve(key). " +
        "Get one free at https://flightnerve.com/register/"
      );
    }
    this.base_url = base_url.replace(/\/+$/, "");
  }

  async _get(endpoint, params = {}) {
    const qs = new URLSearchParams(clean(params)).toString();
    const url = `${this.base_url}/${endpoint}/${this.api_key}` + (qs ? `?${qs}` : "");
    return this._handle(await fetch(url));
  }

  async _post(endpoint, body = {}) {
    const url = `${this.base_url}/${endpoint}/${this.api_key}`;
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(clean(body)),
    });
    return this._handle(res);
  }

  async _handle(res) {
    let data;
    try {
      data = await res.json();
    } catch (e) {
      throw new FlightNerveError(res.status, "invalid JSON response");
    }
    if (!res.ok) {
      const message = (data && data.message) || "request failed";
      throw new FlightNerveError(res.status, message);
    }
    return data;
  }

  // ----- endpoints -----

  // GET /airline. Schedule, route, aircraft and live status for one flight.
  flight_status({ name, num, date, depap } = {}) {
    return this._get("airline", { name, num, date, depap });
  }

  // GET /track. Live position of an airborne flight. Empty array if not airborne.
  live_position({ name, num, date } = {}) {
    return this._get("track", { name, num, date });
  }

  // GET /schedules. Projected timetable for a flight over the coming days.
  schedules({ name, num, date, days } = {}) {
    return this._get("schedules", { name, num, date, days });
  }

  // GET /airport. Lookup by code, text search, or nearest to a coordinate.
  airport({ code, search, lat, lon, radius } = {}) {
    return this._get("airport", { code, search, lat, lon, radius });
  }

  // GET /airspace. Aircraft airborne in an area, or inbound to an airport.
  airspace({ lat, lon, radius, bbox, airport, inbound } = {}) {
    return this._get("airspace", { lat, lon, radius, bbox, airport, inbound });
  }

  // GET /route. Route detail, airline network, airport destinations, or one flight.
  route({ from, to, airline, name, num } = {}) {
    return this._get("route", { from, to, airline, name, num });
  }

  // GET /watch. Your tracked flights with scheduled, FN estimated and live arrivals.
  watchlist() {
    return this._get("watch", {});
  }

  // POST /watch. Add a flight to your watchlist.
  watch_add({ flight, date, leg } = {}) {
    return this._post("watch", { flight, date, leg });
  }

  // POST /watch with action remove. Stop tracking a flight.
  watch_remove({ flight, id } = {}) {
    return this._post("watch", { action: "remove", flight, id });
  }
}

"""
Minimal Python client for the FlightNerve flight tracking API.

Docs:    https://flightnerve.com/doc/
Get key: https://flightnerve.com/register/

The only dependency is `requests`. Your API key goes in the URL path. Set it
with the FLIGHTNERVE_API_KEY environment variable, or pass it to FlightNerve(...).
"""
import os
import requests

BASE_URL = "https://api.flightnerve.com"


class FlightNerveError(RuntimeError):
    """Raised when the API returns a non 2xx response."""
    def __init__(self, status, message):
        super().__init__("[%s] %s" % (status, message))
        self.status = status
        self.message = message


class FlightNerve:
    def __init__(self, api_key=None, base_url=BASE_URL, timeout=30):
        self.api_key = api_key or os.environ.get("FLIGHTNERVE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "No API key. Set FLIGHTNERVE_API_KEY or pass api_key=... "
                "(get one free at https://flightnerve.com/register/)."
            )
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint, **params):
        params = {k: v for k, v in params.items() if v is not None}
        url = "%s/%s/%s" % (self.base_url, endpoint, self.api_key)
        return self._handle(self.session.get(url, params=params, timeout=self.timeout))

    def _post(self, endpoint, body):
        body = {k: v for k, v in body.items() if v is not None}
        url = "%s/%s/%s" % (self.base_url, endpoint, self.api_key)
        return self._handle(self.session.post(url, json=body, timeout=self.timeout))

    @staticmethod
    def _handle(resp):
        try:
            data = resp.json()
        except ValueError:
            raise FlightNerveError(resp.status_code, resp.text[:200])
        if not resp.ok:
            message = data.get("message") if isinstance(data, dict) else str(data)
            raise FlightNerveError(resp.status_code, message or "request failed")
        return data

    # ----- endpoints -----

    def flight_status(self, name, num, date=None, dep_airport=None, arr_airport=None):
        """GET /airline. Full schedule, route, aircraft and live status for one flight.
        dep_airport (depap) pins the leg leaving that airport; arr_airport (arrap) pins the leg arriving there."""
        return self._get("airline", name=name, num=num, date=date, depap=dep_airport, arrap=arr_airport)

    def live_position(self, name, num, date=None):
        """GET /track. Live position of an airborne flight. Empty list if not airborne."""
        return self._get("track", name=name, num=num, date=date)

    def schedules(self, name, num, date=None, days=None):
        """GET /schedules. Projected timetable for a flight over the coming days."""
        return self._get("schedules", name=name, num=num, date=date, days=days)

    def airport(self, code=None, search=None, lat=None, lon=None, radius=None):
        """GET /airport. Lookup by code, text search, or nearest to a coordinate."""
        return self._get("airport", code=code, search=search, lat=lat, lon=lon, radius=radius)

    def airspace(self, lat=None, lon=None, radius=None, bbox=None, airport=None, inbound=None):
        """GET /airspace. Every aircraft airborne in an area, or inbound to an airport."""
        return self._get("airspace", lat=lat, lon=lon, radius=radius,
                         bbox=bbox, airport=airport, inbound=inbound)

    def route(self, origin=None, destination=None, airline=None, name=None, num=None):
        """GET /route. Route detail, an airline network, an airport's destinations, or one flight's route."""
        return self._get("route", **{"from": origin, "to": destination,
                                     "airline": airline, "name": name, "num": num})

    def watchlist(self):
        """GET /watch. Your tracked flights, each with scheduled, FN estimated and live arrival anchors."""
        return self._get("watch")

    def watch_add(self, flight, date=None, leg=None):
        """POST /watch. Add a flight to your watchlist."""
        return self._post("watch", {"flight": flight, "date": date, "leg": leg})

    def watch_remove(self, flight=None, watch_id=None):
        """POST /watch with action remove. Stop tracking a flight."""
        return self._post("watch", {"action": "remove", "flight": flight, "id": watch_id})

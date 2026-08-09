// Live airspace: aircraft inbound to an airport with a live ETA.
// GET /airspace
//
// Usage:
//   export FLIGHTNERVE_API_KEY="your_key_here"
//   node examples/airspace.js

import { FlightNerve } from "../flightnerve.js";

const fn = new FlightNerve();

const result = await fn.airspace({ inbound: "JFK" });

console.log(`Inbound to ${result.airport.iata} ${result.airport.name}: ${result.aircraft.length} aircraft`);

for (const a of result.aircraft.slice(0, 8)) {
  console.log(`  ${a.callsign}  alt ${a.altitude} ft  speed ${a.groundSpeed} kt  ${a.distanceKm.toFixed(1)} km out, ${a.etaMinutes} min`);
}

// Other ways to query airspace:
//   fn.airspace({ lat: 40.6, lon: -73.8, radius: 60 })   within 60 km of a point
//   fn.airspace({ bbox: "40.4,-74.3,40.9,-73.5" })       inside a bounding box
//   fn.airspace({ airport: "LHR", radius: 80 })          around an airport

// Live position of an airborne flight.
// GET /track  (empty array if the flight is not airborne right now)
//
// Usage:
//   export FLIGHTNERVE_API_KEY="your_key_here"
//   node examples/live_position.js

import { FlightNerve } from "../flightnerve.js";

const fn = new FlightNerve();

const positions = await fn.live_position({ name: "SQ", num: "25" });

if (positions.length === 0) {
  console.log("SQ25 is not airborne right now (empty result, no credit charged).");
} else {
  const p = positions[0];
  console.log(`SQ25 ${p.status} from ${p.departure.airportCode} to ${p.arrival.airportCode}`);
  console.log(`  position: ${p.latitude}, ${p.longitude}  altitude ${p.altitude} ft`);
  console.log(`  speed: ${p.groundSpeed} kt  heading ${p.heading} deg`);
  console.log(`  phase: ${p.phase}  progress ${Math.round(p.progress * 100)}%  source ${p.source}`);
}

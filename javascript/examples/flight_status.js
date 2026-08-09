// Flight status: schedule, route, aircraft and live status for one flight.
// GET /airline
//
// Usage:
//   export FLIGHTNERVE_API_KEY="your_key_here"
//   node examples/flight_status.js

import { FlightNerve } from "../flightnerve.js";

const fn = new FlightNerve(); // reads FLIGHTNERVE_API_KEY

// Emirates EK72. Add date "YYYYMMDD" for a specific day, or depap "DXB"
// to pick one leg of a multi leg flight number.
const result = await fn.flight_status({ name: "EK", num: "72" });

const departure = result[0].departure;
const arrival = result[1].arrival;
const aircraft = result[2].aircraft;
const status = result[3].status;

console.log("EK72  status:", status);
console.log(`  from: ${departure.airportCode} ${departure.airportCity} at ${departure.scheduledTime} terminal ${departure.terminal}`);
console.log(`  to:   ${arrival.airportCode} ${arrival.airportCity} at ${arrival.scheduledTime} terminal ${arrival.terminal}`);
console.log(`  aircraft: ${aircraft.name} tail ${aircraft.regNumber}`);

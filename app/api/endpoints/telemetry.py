from fastapi import APIRouter
from fastapi.responses import JSONResponse
from datetime import datetime
from app.schemas.telemetry import Telemetry
from app.services.satellite_simulator import telemetry_data, satellite_positions  # Import satellite_positions
from app.services.telemetry_manager import voltage_history
from app.services.shared_state import satellite_states  # Import satellite_states

router = APIRouter()

CRITICAL_VOLTAGE = 11.5  # V

@router.post("/")
async def submit_telemetry(telemetry: Telemetry):
    telemetry_data.append(telemetry)
    voltage = telemetry.data.get("battery_voltage")
    if voltage is not None:
        voltage_history[telemetry.satellite_id].append(
            (telemetry.timestamp, voltage)
        )
    return {"status": "received"}

@router.get("/api/telemetry/graph")
async def get_telemetry_graph():
    result = {
        "SAT-001": [],
        "SAT-002": [],
        "SAT-003": []
    }

    for t in telemetry_data:
        entry = {
            "timestamp": t["timestamp"],  # Ensure timestamp is ISO string
            "battery_voltage": t["data"].get("battery_voltage")  # Extract battery voltage
        }
        result[t["satellite_id"]].append(entry)

    return result

@router.get("/health")
async def get_telemetry_health():
    health = {}

    for sat_id, history in voltage_history.items():
        if not history:
            health[sat_id] = {
                "battery_voltage": None,
                "projected_minutes_to_critical": None
            }
            continue

        latest_voltage = history[-1][1]

        # Predict time to drop to 10.0 V if we have enough data
        if len(history) >= 2:
            (t1, v1), (t2, v2) = history[-2], history[-1]
            time_diff = (t2 - t1).total_seconds() / 60  # minutes
            voltage_drop = v1 - v2

            if voltage_drop > 0:
                rate = voltage_drop / time_diff
                projected_minutes = (latest_voltage - 10.0) / rate
            else:
                projected_minutes = None
        else:
            projected_minutes = None

        health[sat_id] = {
            "battery_voltage": latest_voltage,
            "projected_minutes_to_critical": round(projected_minutes, 2) if projected_minutes else None
        }

    return health

@router.get("/locations")
async def get_satellite_locations():
    locations = {}
    seen = set()

    # Iterate in reverse order to get most recent first
    for telemetry in reversed(telemetry_data):
        if isinstance(telemetry, dict):
            sat_id = telemetry.get("satellite_id")
            if sat_id and sat_id not in seen:
                if telemetry.get("latitude") is not None and telemetry.get("longitude") is not None:
                    locations[sat_id] = {
                        "latitude": telemetry["latitude"],
                        "longitude": telemetry["longitude"],
                        "altitude": telemetry["altitude"]
                    }
                    seen.add(sat_id)
        if len(seen) == len(satellite_states):  # Already found all satellites
            break

    return JSONResponse(content=locations)
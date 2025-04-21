from fastapi import APIRouter
from app.schemas.telemetry import Telemetry
from app.services.satellite_simulator import telemetry_data

router = APIRouter()

@router.post("/")
async def submit_telemetry(telemetry: Telemetry):
    telemetry_data.append(telemetry)
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
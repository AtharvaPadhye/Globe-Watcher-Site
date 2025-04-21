from app.services.telemetry_storage import telemetry_data
from datetime import datetime

async def post_telemetry(satellite_id: str, battery_voltage: float, temperature: float, timestamp: datetime):
    telemetry_data.append({
        "satellite_id": satellite_id,
        "timestamp": timestamp,
        "data": {
            "battery_voltage": battery_voltage,
            "temperature": temperature
        }
    })

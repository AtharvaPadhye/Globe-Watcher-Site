from collections import defaultdict
from app.services.telemetry_storage import telemetry_data
from datetime import datetime

voltage_history = defaultdict(list)

async def post_telemetry(satellite_id: str, battery_voltage: float, temperature: float, timestamp: datetime):
    telemetry_data.append({
        "satellite_id": satellite_id,
        "timestamp": timestamp,
        "data": {
            "battery_voltage": battery_voltage,
            "temperature": temperature
        }
    })
    # Update voltage history
    voltage_history[satellite_id].append((timestamp, battery_voltage))
    # Trim to last 100 entries
    if len(voltage_history[satellite_id]) > 100:
        voltage_history[satellite_id].pop(0)

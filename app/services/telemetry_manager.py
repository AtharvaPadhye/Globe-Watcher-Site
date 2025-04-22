from app.services.shared_state import satellite_states, voltage_history
from app.services.telemetry_storage import telemetry_data
from datetime import datetime
from app.services.queue_manager import move_commands

async def post_telemetry(
    satellite_id: str,
    battery_voltage: float,
    temperature: float,
    timestamp: datetime,
    traffic: int,
    latitude: float,
    longitude: float,
    altitude: float
):
    telemetry_point = {
        "satellite_id": satellite_id,
        "timestamp": timestamp,
        "data": {
            "battery_voltage": battery_voltage,
            "temperature": temperature,
            "traffic": traffic
        },
        "latitude": latitude,
        "longitude": longitude,
        "altitude": altitude
    }
    telemetry_data.append(telemetry_point)

    # Update voltage history
    if satellite_id not in voltage_history:
        voltage_history[satellite_id] = []
    voltage_history[satellite_id].append((timestamp, battery_voltage))

    # Trim to last 100 entries
    if len(voltage_history[satellite_id]) > 100:
        voltage_history[satellite_id].pop(0)

    # Check if the satellite is offline
    if not satellite_states[satellite_id]["online"]:
        # Find a healthy satellite to reassign traffic
        healthy_sat = None
        for other_sat, state in satellite_states.items():
            if other_sat != satellite_id and state["online"]:
                healthy_sat = other_sat
                break

        if healthy_sat:
            move_commands(satellite_id, healthy_sat)
            print(f"[TRAFFIC REASSIGNMENT] Traffic from {satellite_id} reassigned to {healthy_sat} due to offline status.")
        else:
            print(f"[TRAFFIC REASSIGNMENT] No healthy satellite available to take over traffic from {satellite_id}.")

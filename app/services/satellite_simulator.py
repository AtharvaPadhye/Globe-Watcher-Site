import asyncio
import random
from datetime import datetime, timedelta, timezone
import pytz
from app.models.telemetry import Telemetry  # Import the Telemetry class
from random import uniform

from app.services.queue_manager import pop_due_commands, move_commands
from app.services.telemetry_storage import telemetry_data
from app.services.telemetry_manager import post_telemetry
from app.services.shared_state import satellite_states, voltage_history

async def simulate_satellite_connections():
    while True:
        now = datetime.utcnow()
        for sat_id in satellite_states.keys():
            # Check if the satellite has sent telemetry in the last 5 minutes
            if sat_id in voltage_history and voltage_history[sat_id]:
                last_telemetry_time = voltage_history[sat_id][-1][0]
                if now - last_telemetry_time > timedelta(minutes=5):
                    satellite_states[sat_id]["online"] = False
                    satellite_states[sat_id]["reason"] = "No telemetry received in the last 5 minutes."
                else:
                    satellite_states[sat_id]["online"] = True
                    satellite_states[sat_id]["reason"] = ""
            else:
                satellite_states[sat_id]["online"] = False
                satellite_states[sat_id]["reason"] = "No telemetry data available."

            # If traffic has been reassigned, mark as offline
            # Ensure traffic_move_log is defined as an empty list if not imported
            traffic_move_log = traffic_move_log if 'traffic_move_log' in globals() else []
            if sat_id in [move["from"] for move in traffic_move_log]:
                satellite_states[sat_id]["online"] = False
                satellite_states[sat_id]["reason"] = "Traffic reassigned to another satellite."

        await asyncio.sleep(10)  # Check every 10 seconds


# Define Pacific Timezone
pacific = pytz.timezone('America/Los_Angeles')

async def simulate_telemetry():
    while True:
        for sat_id, position in satellite_positions.items():
            if satellite_states[sat_id]["online"]:
                voltage = round(random.uniform(12.5, 14.0), 2)
                temperature = round(random.uniform(25.0, 35.0), 1)
                traffic = random.randint(10, 100)

                # Special behavior for SAT-004
                if sat_id == "SAT-004":
                    voltage = max(10.0, voltage - random.uniform(0.1, 0.5))
                    if random.random() < 0.4:
                        satellite_states[sat_id]["online"] = False
                        satellite_states[sat_id]["reason"] = "Temporary outage."
                        continue

                await post_telemetry(
                    satellite_id=sat_id,
                    battery_voltage=voltage,
                    temperature=temperature,
                    timestamp=datetime.utcnow(),
                    traffic=traffic,
                    latitude=position["lat"],
                    longitude=position["lon"],
                    altitude=random.uniform(300, 600)
                )

                print(f"[TELEMETRY] {sat_id}: Voltage={voltage}, Temp={temperature}, Lat={position['lat']}, Lon={position['lon']}")
        await asyncio.sleep(5)

satellite_positions = {
    "SAT-001": {"lat": 0, "lon": 0},
    "SAT-002": {"lat": 10, "lon": 20},
    "SAT-003": {"lat": -10, "lon": -20},
    "SAT-004": {"lat": 20, "lon": 40},
}

async def simulate_satellites():
    while True:
        for satellite_id, position in satellite_positions.items():
            if satellite_states[satellite_id]:
                # Simulate simple eastward orbit
                position["lon"] += 1
                if position["lon"] > 180:
                    position["lon"] = -180

                # Generate telemetry with position data
                telemetry_point = Telemetry(
                    satellite_id=satellite_id,
                    data={
                        "battery_voltage": uniform(12.0, 13.0),
                        "solar_panel_output": uniform(0.5, 1.5),
                    },
                    timestamp=datetime.utcnow(),
                    latitude=uniform(-90.0, 90.0),  # Random latitude
                    longitude=uniform(-180.0, 180.0),  # Random longitude
                    altitude=uniform(300, 600)  # Altitude in km (LEO range)
                )
                telemetry_data.append(telemetry_point.dict())  # Store as dict for compatibility
        
        await asyncio.sleep(5)  # Wait 5 seconds before next telemetry burst


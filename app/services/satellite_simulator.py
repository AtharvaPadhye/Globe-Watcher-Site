import asyncio
import random
from datetime import datetime, timedelta, timezone
import pytz

from app.services.queue_manager import pop_due_commands
from app.services.telemetry_storage import telemetry_data
from app.services.telemetry_manager import voltage_history
from app.services.telemetry_manager import post_telemetry

satellite_states = {
    "SAT-001": True,
    "SAT-002": True,
    "SAT-003": True
}

async def simulate_satellite_connections():
    while True:
        for sat_id in satellite_states.keys():
            prev_state = satellite_states[sat_id]
            # Randomly toggle online/offline
            satellite_states[sat_id] = random.choice([True, False])
            current_state = satellite_states[sat_id]

            # If satellite just came online, send queued commands
            if not prev_state and current_state:
                due_commands = pop_due_commands(sat_id)
                for cmd in due_commands:
                    print(f"[AUTO] Sending queued command to {sat_id}: {cmd.command_type}")

        await asyncio.sleep(10)  # Change every 10 seconds


# Define Pacific Timezone
pacific = pytz.timezone('America/Los_Angeles')

async def simulate_telemetry():
    while True:
        now_pacific = datetime.now(pacific)
        timestamp = now_pacific.isoformat()

        for sat_id in satellite_states.keys():
            if satellite_states[sat_id]:
                voltage = round(random.uniform(12.5, 14.0), 2)
                temperature = round(random.uniform(25.0, 35.0), 1)

                # Use post_telemetry to update telemetry_data and voltage_history
                await post_telemetry(satellite_id=sat_id, battery_voltage=voltage, temperature=temperature, timestamp=datetime.utcnow())

                print(f"[TELEMETRY] {sat_id} @ {timestamp}: Voltage={voltage}, Temperature={temperature}")

        await asyncio.sleep(5)


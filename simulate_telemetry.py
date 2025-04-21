import requests
import random
import time
from datetime import datetime

satellite_ids = ["SAT-001", "SAT-002", "SAT-003"]

while True:
    for sat_id in satellite_ids:
        voltage = round(random.uniform(12.5, 14.0), 2)
        temperature = round(random.uniform(25.0, 35.0), 1)
        now = datetime.utcnow().isoformat()
        payload = {
            "satellite_id": sat_id,
            "data": {
                "battery_voltage": voltage,
                "temperature": temperature
            },
            "timestamp": now
        }
        response = requests.post("http://localhost:8000/api/telemetry/", json=payload)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent telemetry for {sat_id}: V={voltage} T={temperature}")
    time.sleep(5)

import requests
import random
import time
from datetime import datetime

satellite_ids = ["SAT-001", "SAT-002", "SAT-003", "SAT-004"]  # Ensure SAT-004 is included

while True:
    for sat_id in satellite_ids:
        if sat_id == "SAT-004":
            # Volatile nature logic for SAT-004
            voltage = max(10.0, round(random.uniform(11.0, 13.0) - random.uniform(0.1, 0.5), 2))
            temperature = round(random.uniform(30.0, 40.0), 1)
            if random.random() < 0.4:  # 40% chance of outage
                print(f"[{datetime.now().strftime('%H:%M:%S')}] {sat_id} is offline temporarily.")
                continue  # Skip sending telemetry for this cycle
        else:
            # Regular logic for other satellites
            voltage = round(random.uniform(12.5, 14.0), 2)
            temperature = round(random.uniform(25.0, 35.0), 1)

        # Simulate traffic data
        traffic = {
            "packets_received": random.randint(100, 1000),
            "bits_received": random.randint(1000, 10000)
        }

        now = datetime.utcnow().isoformat()
        payload = {
            "satellite_id": sat_id,
            "data": {
                "battery_voltage": voltage,
                "temperature": temperature,
                "traffic": traffic  # Include traffic data
            },
            "timestamp": now
        }
        response = requests.post("http://localhost:8000/api/telemetry/", json=payload)
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Sent telemetry for {sat_id}: V={voltage} T={temperature} Traffic={traffic}")
    time.sleep(5)

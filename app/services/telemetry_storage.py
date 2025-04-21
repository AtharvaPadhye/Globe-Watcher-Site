from datetime import datetime
import pytz

# Global telemetry data storage
telemetry_data = [
    {
        "satellite_id": "SAT-001",
        "timestamp": datetime.now(pytz.utc),
        "data": {
            "battery_voltage": 13.5,
            "temperature": 28.7
        }
    },
    {
        "satellite_id": "SAT-002",
        "timestamp": datetime.now(pytz.utc),
        "data": {
            "battery_voltage": 12.8,
            "temperature": 30.1
        }
    },
    {
        "satellite_id": "SAT-003",
        "timestamp": datetime.now(pytz.utc),
        "data": {
            "battery_voltage": 14.0,
            "temperature": 27.5
        }
    }
]

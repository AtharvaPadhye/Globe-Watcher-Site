
# Satellite Constellation Operation Dashboard (SCOD) - Version 1.0

## Overview

The Satellite Constellation Operation Dashboard (SCOD) is a FastAPI-based application that provides real-time monitoring, command management, and health status visualization for a simulated (and future real) satellite constellation. 

Version 1.0 represents the first stable release, featuring:

- Live telemetry visualization using Chart.js
- Satellite status monitoring (online/offline, outage reasons)
- Dynamic command queueing and execution
- Dynamic traffic reassignments on satellite issues
- GPS satellite plotting on a live map using Leaflet.js
- Health predictions based on voltage readings
- Auto-refresh dashboard with user-friendly UX

---

## Project Structure

```
fastapi-app
├── app
│   ├── main.py                # Entry point of the FastAPI application
│   ├── api
│   │   ├── endpoints           # API endpoints (commands, telemetry)
│   ├── core
│   │   └── config.py           # Configuration settings
│   ├── models
│   │   └── telemetry.py        # Data models for telemetry points
│   ├── services
│   │   ├── queue_manager.py    # Command queue management
│   │   ├── satellite_simulator.py # Simulates telemetry and satellite movement
│   │   ├── telemetry_manager.py   # Health and telemetry utilities
│   │   ├── telemetry_storage.py   # Stores telemetry history
│   ├── templates
│   │   └── dashboard.html      # Main dashboard UI
│   ├── static
│   │   └── style.css           # Dashboard styling
├── tests
│   ├── test_main.py            # Unit tests
├── requirements.txt            # Project dependencies
├── README.md                   # Project documentation
└── uvicorn_config.py           # Uvicorn optional configs
```

---

## Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd fastapi-app
```

2. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

---

## Usage

To run the application locally:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Access the dashboard at [http://localhost:8000/](http://localhost:8000/).

Interactive API docs available at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## Testing

Run tests using:

```bash
pytest tests/
```

---

## Future Plans

- Integrate with a public satellite tracking API (e.g., NORAD TLE feeds)
- Replace simulation engine with live orbital data
- Add command execution confirmations
- Enhance security for multi-user access
- Enable WebSocket real-time updates
- Expand to non-LEO constellations (MEO, GEO)

---

## License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.

---

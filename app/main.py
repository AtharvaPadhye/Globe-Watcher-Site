from fastapi import FastAPI, Request, Form, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse, HTMLResponse, FileResponse
import os
from app.api.endpoints import commands, telemetry
from app.services.queue_manager import get_all_queues, move_commands
from app.services.satellite_simulator import satellite_states, telemetry_data, simulate_telemetry, simulate_satellite_connections
from app.services.telemetry_manager import voltage_history
from app.schemas.command import Command
import json
from datetime import datetime, timedelta
import asyncio

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(commands.router, prefix="/api/commands", tags=["commands"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])

traffic_move_log = []  # Log for traffic moves

async def monitor_satellite_health():
    """Background task to monitor satellites and dynamically redistribute load."""
    reassigned_satellites = set()  # Track satellites with reassigned traffic

    while True:
        await asyncio.sleep(5)  # Check every 5 seconds

        # Clear stale traffic reassignments
        now = datetime.utcnow()
        traffic_move_log[:] = [
            move for move in traffic_move_log
            if now - move["timestamp"] <= timedelta(minutes=5) and len(traffic_move_log) <= 10
        ]

        for sat_id, voltages in voltage_history.items():
            if not voltages:
                continue  # Skip if no voltage data

            # Check if any voltage point is below the critical level (12.2V)
            if any(voltage[1] < 12.2 for voltage in voltages):
                if sat_id not in reassigned_satellites:
                    print(f"[MONITOR] Satellite {sat_id} has critical voltage levels!")

                    # Find a healthy satellite to move traffic to
                    healthy_sat = None
                    for other_sat, other_voltages in voltage_history.items():
                        if other_sat == sat_id or not other_voltages:
                            continue
                        if other_voltages[-1][1] > 12.5:  # Healthy voltage threshold
                            healthy_sat = other_sat
                            break

                    if healthy_sat:
                        move_commands(sat_id, healthy_sat)
                        reassigned_satellites.add(sat_id)
                        traffic_move_log.append({
                            "from": sat_id,
                            "to": healthy_sat,
                            "timestamp": now,
                            "reason": "Critical voltage (below 12.2V)",
                            "verbage": f"Traffic reassigned from {sat_id} to {healthy_sat} due to critical voltage levels."
                        })
                    else:
                        print(f"[MONITOR] No healthy satellite found to take over traffic from {sat_id}.")
            else:
                # Check if voltage has resumed above 12.2 for two consecutive points
                if len(voltages) >= 2 and voltages[-1][1] > 12.2 and voltages[-2][1] > 12.2:
                    if sat_id in reassigned_satellites:
                        print(f"[MONITOR] Satellite {sat_id} voltage has stabilized. Moving traffic back.")

                        # Move traffic back to the original satellite
                        move_commands(sat_id, sat_id)  # Reassign traffic back to itself
                        reassigned_satellites.remove(sat_id)
                        traffic_move_log.append({
                            "from": "N/A",
                            "to": sat_id,
                            "timestamp": now,
                            "reason": "Voltage stabilized (above 12.2V for two consecutive points)",
                            "verbage": f"Traffic moved back to {sat_id} as voltage stabilized."
                        })

@app.on_event("startup")
async def start_health_monitor():
    asyncio.create_task(monitor_satellite_health())

@app.on_event("startup")
async def start_simulator():
    import asyncio
    asyncio.create_task(simulate_telemetry())
    asyncio.create_task(simulate_satellite_connections())

# Web dashboard route
@app.get("/dashboard")
async def dashboard(request: Request, success: int = 0):
    queues = get_all_queues()

    telemetry_plot_data = []
    for telemetry in telemetry_data[-10:]:
        # Safely handle Telemetry objects and raw dicts
        if isinstance(telemetry, dict):
            timestamp = telemetry["timestamp"]
            data = telemetry["data"]
        else:
            timestamp = telemetry.timestamp
            data = telemetry.data

        timestamp_str = timestamp.strftime("%H:%M:%S")
        voltage = data.get("battery_voltage")
        telemetry_plot_data.append((timestamp_str, voltage))

    # Fetch health data for all satellites, including SAT-004
    from app.api.endpoints.telemetry import get_telemetry_health
    health_data = await get_telemetry_health()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "queues": queues,
        "sat_states": satellite_states,
        "telemetry_data": telemetry_data[-10:],  # Include SAT-004 data
        "telemetry_plot_data": telemetry_plot_data,
        "success": success,
        "traffic_moves": traffic_move_log,  # Pass move history with reasons
        "health_data": health_data  # Pass health data to the template
    })

@app.post("/submit_command_form")
async def submit_command_form(
    satellite_id: str = Form(...),
    command_type: str = Form(...),
    parameters: str = Form(...),
    priority: int = Form(...),
    expiry_time: str = Form("")
):
    try:
        params = json.loads(parameters)
    except json.JSONDecodeError:
        params = {}

    expiry = None
    if expiry_time:
        try:
            expiry = datetime.fromisoformat(expiry_time)
        except ValueError:
            pass  # Ignore bad expiry format

    new_command = Command(
        satellite_id=satellite_id,
        command_type=command_type,
        parameters=params,
        priority=priority,
        expiry_time=expiry
    )

    # Send to backend logic
    from app.services.queue_manager import queue_command
    from app.services.satellite_simulator import satellite_states

    if satellite_states.get(satellite_id, False):
        print(f"[FORM] Sending command immediately to {satellite_id}: {command_type}")
    else:
        queue_command(satellite_id, new_command)
        print(f"[FORM] Queued command for {satellite_id}: {command_type}")

    # Redirect to dashboard with ?success=1
    return RedirectResponse(url="/dashboard?success=1", status_code=303)

@app.get("/api/telemetry/graph")
def get_telemetry_graph_data():
    series = {
        "SAT-001": [],
        "SAT-002": [],
        "SAT-003": [],
        "SAT-004": []  # Predefined satellites
    }

    for entry in telemetry_data[-100:]:  # Process the last 100 telemetry points
        # Safely handle Telemetry objects and raw dicts
        if isinstance(entry, dict):
            timestamp = entry["timestamp"]
            data = entry["data"]
            satellite_id = entry["satellite_id"]
        else:
            timestamp = entry.timestamp
            data = entry.data
            satellite_id = entry.satellite_id

        ts = timestamp.isoformat()
        voltage = data.get("battery_voltage")
        if voltage is not None:
            # Dynamically add unknown satellites to the series
            if satellite_id not in series:
                series[satellite_id] = []
            series[satellite_id].append({
                "timestamp": ts,
                "battery_voltage": voltage
            })

    return JSONResponse(series)

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})
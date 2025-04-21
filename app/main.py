from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from app.api.endpoints import commands, telemetry
from app.services.queue_manager import get_all_queues
from app.services.satellite_simulator import satellite_states, telemetry_data
from app.schemas.command import Command
import json
from datetime import datetime

app = FastAPI()

# Mount static files and templates
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# Include API routers
app.include_router(commands.router, prefix="/api/commands", tags=["commands"])
app.include_router(telemetry.router, prefix="/api/telemetry", tags=["telemetry"])

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

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "queues": queues,
        "sat_states": satellite_states,
        "telemetry_data": telemetry_data[-10:],  # Send original
        "telemetry_plot_data": telemetry_plot_data,
        "success": success
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
        "SAT-003": []
    }

    for entry in telemetry_data[-100:]:  # last 100 points
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
            series[satellite_id].append({
                "timestamp": ts,
                "battery_voltage": voltage
            })

    return JSONResponse(series)
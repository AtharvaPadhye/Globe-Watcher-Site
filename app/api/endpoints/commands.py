from fastapi import APIRouter
from app.schemas.command import Command
from app.services.queue_manager import queue_command
from app.services.satellite_simulator import satellite_states

router = APIRouter()

@router.post("/")
async def submit_command(command: Command):
    if satellite_states.get(command.satellite_id, False):
        # Satellite is online: send immediately (simulate)
        print(f"Command sent immediately to {command.satellite_id}: {command.command_type}")
    else:
        # Satellite offline: queue it
        queue_command(command.satellite_id, command)
    return {"status": "submitted"}
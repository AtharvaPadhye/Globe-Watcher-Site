from fastapi import APIRouter, HTTPException
from app.schemas.command import Command
from app.services.queue_manager import queue_command, move_commands
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

@router.post("/reassign")
async def reassign_traffic(satellite_id: str):
    if satellite_id not in satellite_states:
        raise HTTPException(status_code=404, detail=f"Satellite {satellite_id} not found")

    # Find a healthy satellite to reassign traffic to
    healthy_sat = None
    for other_sat, state in satellite_states.items():
        if other_sat != satellite_id and state:  # Check if the satellite is online
            healthy_sat = other_sat
            break

    if not healthy_sat:
        raise HTTPException(status_code=400, detail="No healthy satellite available for reassignment")

    # Perform the reassignment
    move_commands(satellite_id, healthy_sat)
    return {"status": "success", "from": satellite_id, "to": healthy_sat}
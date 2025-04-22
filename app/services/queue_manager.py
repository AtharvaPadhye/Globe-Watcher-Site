from queue import Queue
from collections import defaultdict
from datetime import datetime
from typing import List
from app.schemas.command import Command

class QueueManager:
    def __init__(self):
        self.command_queue = Queue()

    def add_command(self, command):
        self.command_queue.put(command)

    def get_next_command(self):
        if not self.command_queue.empty():
            return self.command_queue.get()
        return None

# Queues per satellite
command_queues = defaultdict(list)

def queue_command(satellite_id: str, command):
    command_queues[satellite_id].append(command)
    prioritize_queue(satellite_id)

def prioritize_queue(satellite_id: str):
    command_queues[satellite_id].sort(
        key=lambda cmd: (cmd.priority, cmd.expiry_time or datetime.max)
    )

def get_commands_for_satellite(satellite_id: str):
    return command_queues[satellite_id]

def get_all_queues():
    return dict(command_queues)

def pop_due_commands(satellite_id: str):
    due = command_queues[satellite_id]
    command_queues[satellite_id] = []
    return due

def move_commands(source_satellite_id: str, target_satellite_id: str) -> List[Command]:
    """Move all queued commands from one satellite to another."""
    if source_satellite_id not in command_queues:
        print(f"[MOVE] No commands to move from {source_satellite_id}")
        return []
    
    # Get all commands
    commands_to_move = command_queues.pop(source_satellite_id, [])

    # Reassign them to new satellite
    for cmd in commands_to_move:
        cmd.satellite_id = target_satellite_id

    # Append to target satellite's queue
    if target_satellite_id not in command_queues:
        command_queues[target_satellite_id] = []
    command_queues[target_satellite_id].extend(commands_to_move)

    print(f"[MOVE] Moved {len(commands_to_move)} commands from {source_satellite_id} to {target_satellite_id}")
    return commands_to_move

from queue import Queue
from collections import defaultdict
from datetime import datetime

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

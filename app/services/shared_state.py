from collections import defaultdict

# Global state for satellite statuses
satellite_states = {
    "SAT-001": {"online": True, "reason": ""},
    "SAT-002": {"online": True, "reason": ""},
    "SAT-003": {"online": True, "reason": ""},
    "SAT-004": {"online": True, "reason": ""}  # Ensure SAT-004 is included
}

# Global state for voltage history
voltage_history = defaultdict(list)

from __future__ import annotations

from typing import Any


def get_config() -> dict[str, Any]:
    return {
        "name": "scenario_4",
        "description": "Speed variation scenario",
        "num_agents": 50,
        "grid_size": 30,
        "num_exits": 2,
        "has_obstacles": False,
        "social_behavior": False,
        "speed_variation": True,
        "seed": 42,
    }

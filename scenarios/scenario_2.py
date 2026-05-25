from __future__ import annotations

from typing import Any


def get_config() -> dict[str, Any]:
    return {
        "name": "scenario_2",
        "description": "50 agents, 2 exits, moderate obstacles",
        "num_agents": 50,
        "grid_size": 30,
        "num_exits": 2,
        "has_obstacles": True,
        "social_behavior": False,
        "seed": 42,
    }

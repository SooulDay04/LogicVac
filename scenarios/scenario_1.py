from __future__ import annotations

from typing import Any


def get_config() -> dict[str, Any]:
    return {
        "name": "scenario_1",
        "description": "25 agents, 1 exit, no obstacles",
        "num_agents": 25,
        "grid_size": 30,
        "num_exits": 1,
        "has_obstacles": False,
        "social_behavior": False,
        "seed": 42,
    }

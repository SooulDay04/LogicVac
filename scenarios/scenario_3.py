from __future__ import annotations

from typing import Any


def get_config() -> dict[str, Any]:
    return {
        "name": "scenario_3",
        "description": "100 agents, high density",
        "num_agents": 100,
        "grid_size": 30,
        "num_exits": 2,
        "has_obstacles": True,
        "social_behavior": False,
        "seed": 42,
    }

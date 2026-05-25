from __future__ import annotations

from typing import Any


def get_config() -> dict[str, Any]:
    return {
        "name": "scenario_5",
        "description": "Social behavior enabled",
        "num_agents": 75,
        "grid_size": 30,
        "num_exits": 2,
        "has_obstacles": True,
        "social_behavior": True,
        "seed": 42,
    }

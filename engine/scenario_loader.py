from __future__ import annotations

import importlib
from typing import Any, Optional


class ScenarioLoader:
    def __init__(self) -> None:
        self.scenarios: dict[str, dict[str, Any]] = {}

    def load_scenario(self, scenario_name: str) -> dict[str, Any]:
        if scenario_name in self.scenarios:
            return self.scenarios[scenario_name]

        module_name = f"evacsim.scenarios.{scenario_name}"
        try:
            module = importlib.import_module(module_name)
            config = getattr(module, "get_config", None)
            if config is not None:
                scenario_config = config()
                self.scenarios[scenario_name] = scenario_config
                return scenario_config
        except ImportError:
            pass

        return self._get_default_scenario(scenario_name)

    def _get_default_scenario(self, name: str) -> dict[str, Any]:
        defaults = {
            "scenario_1": {
                "num_agents": 25,
                "grid_size": 30,
                "num_exits": 1,
                "has_obstacles": False,
                "social_behavior": False,
            },
            "scenario_2": {
                "num_agents": 50,
                "grid_size": 30,
                "num_exits": 2,
                "has_obstacles": True,
                "social_behavior": False,
            },
            "scenario_3": {
                "num_agents": 100,
                "grid_size": 30,
                "num_exits": 2,
                "has_obstacles": True,
                "social_behavior": False,
            },
            "scenario_4": {
                "num_agents": 50,
                "grid_size": 30,
                "num_exits": 2,
                "has_obstacles": False,
                "social_behavior": False,
                "speed_variation": True,
            },
            "scenario_5": {
                "num_agents": 75,
                "grid_size": 30,
                "num_exits": 2,
                "has_obstacles": True,
                "social_behavior": True,
            },
        }
        return defaults.get(name, defaults["scenario_1"])

    def list_scenarios(self) -> list[str]:
        return [
            "scenario_1",
            "scenario_2",
            "scenario_3",
            "scenario_4",
            "scenario_5",
        ]

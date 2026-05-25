from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from evacsim.config import GRID_SIZE
from evacsim.data.exporter import DataExporter
from evacsim.engine.scenario_loader import ScenarioLoader
from evacsim.engine.simulation import EvacuationModel


class SimulationController:
    def __init__(self) -> None:
        self.loader = ScenarioLoader()
        self.exporter = DataExporter(
            output_dir=str(Path(__file__).resolve().parents[1] / "data" / "output")
        )
        self.default_scenario = "scenario_1"
        self.default_algorithm = "astar"
        self.default_stress_level = 1.0

    def list_scenarios(self) -> list[str]:
        return self.loader.list_scenarios()

    def create_model(
        self,
        scenario_name: str,
        agent_count: int | None = None,
        route_algorithm: str = "astar",
        stress_level: float = 1.0,
    ) -> EvacuationModel:
        scenario = self.loader.load_scenario(scenario_name)
        num_agents = agent_count if agent_count is not None else int(scenario.get("num_agents", 25))
        grid_size = int(scenario.get("grid_size", GRID_SIZE))
        seed = scenario.get("seed", 42)

        model = EvacuationModel(
            num_agents=num_agents,
            grid_size=grid_size,
            seed=seed,
            stress_level=stress_level,
        )
        model.setup()
        model.route_manager.set_algorithm(route_algorithm)
        self._apply_scenario_layout(model, scenario)
        return model

    def export_metrics(self, model: EvacuationModel) -> tuple[list[str], int]:
        data = model.metrics_collector.get_data() if model.metrics_collector is not None else []
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{model.scenario_name}_metrics_{stamp}"
        paths = self.exporter.export_all(data, base_name, formats=["csv", "json"])
        return paths, len(data)

    def _apply_scenario_layout(self, model: EvacuationModel, scenario: dict[str, Any]) -> None:
        building = model.environment.building
        grid = model.environment.grid

        building.walls.clear()
        building.obstacles.clear()
        building.exits.clear()
        grid.fill_floor()

        exit_count = max(1, int(scenario.get("num_exits", 1)))
        for idx in range(exit_count):
            y = int((idx + 1) * (grid.size / (exit_count + 1)))
            building.add_exit(grid.size - 1, y)

        if scenario.get("has_obstacles", False) and grid.size >= 12:
            left = int(grid.size * 0.35)
            top = int(grid.size * 0.25)
            building.add_rectangular_obstacle(left, top, left + 2, top + 4)

            right = int(grid.size * 0.62)
            bottom = int(grid.size * 0.58)
            building.add_rectangular_obstacle(right, bottom, right + 2, bottom + 4)

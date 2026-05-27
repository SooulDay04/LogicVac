from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

from evacsim.config import GRID_SIZE
from evacsim.config import CellType
from evacsim.data.exporter import DataExporter
from evacsim.engine.scenario_loader import ScenarioLoader
from evacsim.engine.simulation import EvacuationModel
from evacsim.heatmaps.exports import HeatmapExporter
from evacsim.metrics.reporter import MetricsReporter


class SimulationController:
    def __init__(self) -> None:
        self.loader = ScenarioLoader()
        self.exporter = DataExporter(
            output_dir=str(Path(__file__).resolve().parents[1] / "data" / "output")
        )
        self.heatmap_exporter = HeatmapExporter(
            Path(__file__).resolve().parents[1] / "data" / "output"
        )
        self.default_scenario = "scenario_1"
        self.default_algorithm = "astar"
        self.default_stress_level = 1.0
        self.metrics_reporter = MetricsReporter()

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
        evacuation_times = (
            model.metrics_collector.get_evacuation_times()
            if model.metrics_collector is not None
            else {}
        )
        cell_transits = (
            model.metrics_collector.get_cell_transits()
            if model.metrics_collector is not None
            else {}
        )
        route_usage = (
            model.metrics_collector.get_route_usage()
            if model.metrics_collector is not None
            else {}
        )
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{model.scenario_name}_metrics_{stamp}"
        report = self.metrics_reporter.generate_report(
            data,
            scenario_name=model.scenario_name,
            evacuation_times=evacuation_times,
            cell_transits=cell_transits,
            route_usage=route_usage,
        )
        paths = self.exporter.export_all(data, base_name, formats=["csv", "json"])
        paths.append(
            self.exporter.export_csv(
                [
                    {"agent_id": agent_id, "evacuation_time": tick}
                    for agent_id, tick in evacuation_times.items()
                ],
                f"{base_name}_individual.csv",
            )
        )
        paths.append(
            self.exporter.export_csv(
                report.get("evacuated_per_tick", []),
                f"{base_name}_per_tick.csv",
            )
        )
        paths.append(
            self.exporter.export_csv(
                [
                    {"cell_x": cell[0], "cell_y": cell[1], "transits": count}
                    for cell, count in cell_transits.items()
                ],
                f"{base_name}_cells.csv",
            )
        )
        top_route = report.get("most_used_route", {})
        route_cells = top_route.get("route", [])
        paths.append(
            self.exporter.export_csv(
                [
                    {"order": idx, "cell_x": cell[0], "cell_y": cell[1]}
                    for idx, cell in enumerate(route_cells)
                ],
                f"{base_name}_top_route.csv",
            )
        )
        paths.append(
            self.exporter.export_csv(
                [
                    {
                        "scenario": model.scenario_name,
                        "total_evacuation_time": report.get("total_evacuation_time", 0),
                        "average_evacuation_time": report.get("average_evacuation_time", 0),
                        "std_evacuation_time": report.get("std_evacuation_time", 0),
                        "max_congestion": report.get("max_congestion", 0),
                        "scenario_efficiency": report.get("scenario_efficiency", 0),
                    }
                ],
                f"{base_name}_summary.csv",
            )
        )
        return paths, len(data)

    def build_metrics_report(self, model: EvacuationModel) -> dict[str, Any]:
        data = model.metrics_collector.get_data() if model.metrics_collector is not None else []
        evacuation_times = (
            model.metrics_collector.get_evacuation_times()
            if model.metrics_collector is not None
            else {}
        )
        cell_transits = (
            model.metrics_collector.get_cell_transits()
            if model.metrics_collector is not None
            else {}
        )
        route_usage = (
            model.metrics_collector.get_route_usage()
            if model.metrics_collector is not None
            else {}
        )
        return self.metrics_reporter.generate_report(
            data,
            scenario_name=model.scenario_name,
            evacuation_times=evacuation_times,
            cell_transits=cell_transits,
            route_usage=route_usage,
        )

    def export_heatmap_csv(self, model: EvacuationModel) -> list[str]:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"{model.scenario_name}_heatmap_{stamp}"
        return self.heatmap_exporter.export_csv(model.heatmap_tracker, base_name)

    def export_heatmap_image(self, model: EvacuationModel) -> str:
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model.scenario_name}_heatmap_{stamp}.png"
        return self.heatmap_exporter.export_image(model.heatmap_tracker, filename)

    def _apply_scenario_layout(self, model: EvacuationModel, scenario: dict[str, Any]) -> None:
        building = model.environment.building
        grid = model.environment.grid

        building.walls.clear()
        building.obstacles.clear()
        building.exits.clear()
        grid.fill_floor()

        layout = scenario.get("layout")
        if layout is not None:
            self._apply_matrix_layout(model, layout)
            self._relocate_agents_to_walkable_cells(model, scenario.get("spawn_cells"))
            return

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

    def _apply_matrix_layout(
        self,
        model: EvacuationModel,
        layout: list[str],
    ) -> None:
        building = model.environment.building
        grid = model.environment.grid

        for y, row in enumerate(layout[: grid.size]):
            for x, marker in enumerate(row[: grid.size]):
                if marker == "#":
                    building.add_wall(x, y)
                elif marker.upper() == "E":
                    building.add_exit(x, y)
                elif marker.upper() == "O":
                    building.add_obstacle(x, y)
                elif marker == "_":
                    grid.set_cell(x, y, CellType.EMPTY)
                else:
                    grid.set_cell(x, y, CellType.FLOOR)

    def _relocate_agents_to_walkable_cells(
        self,
        model: EvacuationModel,
        spawn_cells: list[tuple[int, int]] | None,
    ) -> None:
        if model.schedule is None:
            return

        if spawn_cells:
            candidates = list(spawn_cells)
        else:
            candidates = [
                (x, y)
                for y in range(model.grid_size)
                for x in range(model.grid_size)
                if model.environment.grid.is_walkable(x, y)
                and model.environment.grid.get_cell(x, y) != CellType.EXIT
            ]

        model.random.shuffle(candidates)
        used: set[tuple[int, int]] = set()
        for agent in model.schedule.agents:
            if agent.pos is not None:
                model.grid.remove_agent(agent)
                agent.pos = None

        for agent in model.schedule.agents:
            next_pos = next(
                (
                    cell
                    for cell in candidates
                    if cell not in used
                    and model.environment.grid.is_walkable(*cell)
                    and model.environment.grid.get_cell(*cell) != CellType.EXIT
                ),
                None,
            )
            if next_pos is None:
                break

            used.add(next_pos)
            model.grid.place_agent(agent, next_pos)
            agent.pos = next_pos
            agent.path.clear()
            agent.optimal_path.clear()
            agent.path_history.clear()
            agent.path_index = 0
            agent._record_position(next_pos)

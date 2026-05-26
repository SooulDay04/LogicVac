from __future__ import annotations

from collections import Counter
from typing import Iterable

import numpy as np

from evacsim.crowd.density import DensityCalculator

Cell = tuple[int, int]
RouteSegment = tuple[Cell, Cell]


class HeatmapTracker:
    def __init__(self, grid_size: int, density_window: int = 3) -> None:
        self.grid_size = grid_size
        self.occupancy_counts = np.zeros((grid_size, grid_size), dtype=int)
        self.cumulative_density = np.zeros((grid_size, grid_size), dtype=float)
        self.route_frequency: Counter[RouteSegment] = Counter()
        self.steps_recorded = 0
        self._density_calculator = DensityCalculator(grid_size, density_window)
        self._agent_history_lengths: dict[int, int] = {}

    def record_step(self, agents: Iterable[object]) -> None:
        agent_list = list(agents)
        positions = [
            agent.pos
            for agent in agent_list
            if getattr(agent, "pos", None) is not None
            and not agent.attributes.is_evacuated()
        ]

        for x, y in positions:
            if self._inside_grid(x, y):
                self.occupancy_counts[y, x] += 1

        density = self._density_calculator.calculate_density(positions)
        self.cumulative_density += np.array(density, dtype=float)
        self.steps_recorded += 1
        self._record_new_route_segments(agent_list)

    def congestion_zones(self, limit: int = 10) -> list[dict[str, int | float]]:
        cells = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                density = float(self.cumulative_density[y, x])
                if density <= 0:
                    continue
                cells.append(
                    {
                        "x": x,
                        "y": y,
                        "cumulative_density": density,
                        "occupancy_count": int(self.occupancy_counts[y, x]),
                    }
                )
        return sorted(
            cells,
            key=lambda cell: (
                cell["cumulative_density"],
                cell["occupancy_count"],
            ),
            reverse=True,
        )[:limit]

    def cell_rows(self) -> list[dict[str, int | float]]:
        zones = {
            (int(zone["x"]), int(zone["y"])): rank
            for rank, zone in enumerate(self.congestion_zones(self.grid_size**2), start=1)
        }
        rows = []
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                rows.append(
                    {
                        "x": x,
                        "y": y,
                        "occupancy_count": int(self.occupancy_counts[y, x]),
                        "cumulative_density": float(self.cumulative_density[y, x]),
                        "congestion_rank": zones.get((x, y), 0),
                    }
                )
        return rows

    def route_rows(self) -> list[dict[str, int]]:
        return [
            {
                "from_x": start[0],
                "from_y": start[1],
                "to_x": end[0],
                "to_y": end[1],
                "frequency": frequency,
            }
            for (start, end), frequency in sorted(
                self.route_frequency.items(),
                key=lambda item: (-item[1], item[0]),
            )
        ]

    def max_density(self) -> float:
        return float(np.max(self.cumulative_density)) if self.steps_recorded else 0.0

    def _record_new_route_segments(self, agents: Iterable[object]) -> None:
        for agent in agents:
            agent_id = int(agent.unique_id)
            history = list(getattr(agent, "path_history", []))
            previous_length = self._agent_history_lengths.get(agent_id, 1)
            if len(history) < 2:
                self._agent_history_lengths[agent_id] = len(history)
                continue

            start_index = max(1, previous_length)
            for index in range(start_index, len(history)):
                start = history[index - 1]
                end = history[index]
                if start != end:
                    self.route_frequency[(start, end)] += 1
            self._agent_history_lengths[agent_id] = len(history)

    def _inside_grid(self, x: int, y: int) -> bool:
        return 0 <= x < self.grid_size and 0 <= y < self.grid_size

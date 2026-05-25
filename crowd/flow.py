from __future__ import annotations

from typing import Optional


class FlowCalculator:
    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size
        self.previous_positions: list[tuple[int, int]] = []

    def calculate_flow(
        self,
        current_positions: list[tuple[int, int]],
        exits: list[tuple[int, int]],
    ) -> dict[str, float]:
        flow_rate = 0.0
        bottleneck_score = 0.0

        for pos in current_positions:
            for exit_pos in exits:
                dist = abs(pos[0] - exit_pos[0]) + abs(pos[1] - exit_pos[1])
                if dist <= 2:
                    flow_rate += 1.0

        if self.previous_positions:
            moved = sum(
                1
                for curr in current_positions
                if curr not in self.previous_positions
            )
            flow_rate += moved * 0.5

        if current_positions:
            density = len(current_positions) / (self.grid_size**2)
            if density > 0.3:
                bottleneck_score = min(density * 2, 1.0)

        self.previous_positions = current_positions.copy()

        return {
            "flow_rate": flow_rate,
            "bottleneck_score": bottleneck_score,
        }

    def detect_bottlenecks(
        self,
        positions: list[tuple[int, int]],
        threshold: float = 5.0,
    ) -> list[tuple[int, int]]:
        cell_counts: dict[tuple[int, int], int] = {}
        for pos in positions:
            cell_counts[pos] = cell_counts.get(pos, 0) + 1

        bottlenecks = []
        for pos, count in cell_counts.items():
            if count >= threshold:
                bottlenecks.append(pos)

        return bottlenecks

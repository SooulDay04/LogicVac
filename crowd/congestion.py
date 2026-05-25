from __future__ import annotations

from evacsim.config import CONGESTION_THRESHOLD


class CongestionDetector:
    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size

    def detect_congestion(
        self, positions: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        cell_counts: dict[tuple[int, int], int] = {}
        for x, y in positions:
            for dy in range(-1, 2):
                for dx in range(-1, 2):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        cell = (nx, ny)
                        cell_counts[cell] = cell_counts.get(cell, 0) + 1

        congested = [
            pos
            for pos, count in cell_counts.items()
            if count >= CONGESTION_THRESHOLD
        ]
        return congested

    def get_congestion_level(
        self, positions: list[tuple[int, int]]
    ) -> float:
        if not positions:
            return 0.0

        congested = self.detect_congestion(positions)
        return len(congested) / (self.grid_size * self.grid_size)

    def is_cell_congested(
        self,
        pos: tuple[int, int],
        positions: list[tuple[int, int]],
    ) -> bool:
        count = 0
        px, py = pos
        for x, y in positions:
            if abs(x - px) <= 1 and abs(y - py) <= 1:
                count += 1
        return count >= CONGESTION_THRESHOLD

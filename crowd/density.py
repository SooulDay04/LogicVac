from __future__ import annotations

from typing import Optional


class DensityCalculator:
    def __init__(self, grid_size: int, window_size: int = 3) -> None:
        self.grid_size = grid_size
        self.window_size = window_size

    def calculate_density(
        self, positions: list[tuple[int, int]]
    ) -> list[list[float]]:
        density = [[0.0] * self.grid_size for _ in range(self.grid_size)]
        half = self.window_size // 2

        for x, y in positions:
            for dy in range(-half, half + 1):
                for dx in range(-half, half + 1):
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.grid_size and 0 <= ny < self.grid_size:
                        density[ny][nx] += 1.0

        area = self.window_size * self.window_size
        for y in range(self.grid_size):
            for x in range(self.grid_size):
                density[y][x] /= area

        return density

    def get_density_at(
        self, density_grid: list[list[float]], x: int, y: int
    ) -> float:
        if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
            return density_grid[y][x]
        return 0.0

    def get_max_density(self, density_grid: list[list[float]]) -> float:
        max_d = 0.0
        for row in density_grid:
            for val in row:
                if val > max_d:
                    max_d = val
        return max_d

    def get_average_density(self, density_grid: list[list[float]]) -> float:
        total = sum(sum(row) for row in density_grid)
        return total / (self.grid_size * self.grid_size)

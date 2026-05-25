from __future__ import annotations

from typing import Optional

from evacsim.config import CellType


class Grid:
    def __init__(self, size: int) -> None:
        self.size = size
        self.cells: list[list[CellType]] = [
            [CellType.EMPTY for _ in range(size)] for _ in range(size)
        ]

    def set_cell(self, x: int, y: int, cell_type: CellType) -> None:
        if 0 <= x < self.size and 0 <= y < self.size:
            self.cells[y][x] = cell_type

    def get_cell(self, x: int, y: int) -> CellType:
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.cells[y][x]
        return CellType.WALL

    def is_walkable(self, x: int, y: int) -> bool:
        cell = self.get_cell(x, y)
        return cell in (CellType.FLOOR, CellType.EXIT)

    def get_exits(self) -> list[tuple[int, int]]:
        exits = []
        for y in range(self.size):
            for x in range(self.size):
                if self.cells[y][x] == CellType.EXIT:
                    exits.append((x, y))
        return exits

    def fill_floor(self) -> None:
        for y in range(self.size):
            for x in range(self.size):
                if self.cells[y][x] == CellType.EMPTY:
                    self.cells[y][x] = CellType.FLOOR

    def get_neighbors(self, x: int, y: int) -> list[tuple[int, int]]:
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def get_occupancy(self, agent_positions: set[tuple[int, int]]) -> list[list[int]]:
        occupancy = [[0] * self.size for _ in range(self.size)]
        for x, y in agent_positions:
            if 0 <= x < self.size and 0 <= y < self.size:
                occupancy[y][x] += 1
        return occupancy

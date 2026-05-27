from __future__ import annotations

from collections import deque

from evacsim.config import CellType
from evacsim.environment.grid import Grid


class Building:
    def __init__(self, grid: Grid) -> None:
        self.grid = grid
        self.walls: list[tuple[int, int]] = []
        self.obstacles: list[tuple[int, int]] = []
        self.exits: list[tuple[int, int]] = []

    def add_wall(self, x: int, y: int) -> None:
        self.grid.set_cell(x, y, CellType.WALL)
        self.walls.append((x, y))

    def add_wall_line(self, x1: int, y1: int, x2: int, y2: int) -> None:
        if x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                self.add_wall(x1, y)
        elif y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                self.add_wall(x, y1)

    def add_obstacle(self, x: int, y: int) -> None:
        self.grid.set_cell(x, y, CellType.OBSTACLE)
        self.obstacles.append((x, y))

    def add_exit(self, x: int, y: int) -> None:
        self.grid.set_cell(x, y, CellType.EXIT)
        self.exits.append((x, y))

    def add_rectangular_obstacle(
        self, x1: int, y1: int, x2: int, y2: int
    ) -> None:
        for y in range(y1, y2 + 1):
            for x in range(x1, x2 + 1):
                self.add_obstacle(x, y)

    def get_nearest_exit(self, x: int, y: int) -> tuple[int, int] | None:
        if not self.exits:
            return None

        start = (x, y)
        exits = set(self.exits)
        queue: deque[tuple[int, int]] = deque([start])
        visited = {start}

        while queue:
            current = queue.popleft()
            if current in exits:
                return current

            for neighbor in self.grid.get_neighbors(*current):
                if neighbor in visited:
                    continue
                if not self.grid.is_walkable(*neighbor):
                    continue

                visited.add(neighbor)
                queue.append(neighbor)

        return min(self.exits, key=lambda e: abs(e[0] - x) + abs(e[1] - y))

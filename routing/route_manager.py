from __future__ import annotations

from typing import Optional

from evacsim.routing.astar import astar_search
from evacsim.routing.bfs import bfs_search
from evacsim.routing.dijkstra import dijkstra_search


class RouteManager:
    def __init__(self, grid, algorithm: str = "astar") -> None:
        self.grid = grid
        self.algorithm = algorithm
        self.cache: dict[
            tuple[tuple[int, int], tuple[int, int]], list[tuple[int, int]]
        ] = {}

    def find_path(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        occupancy: Optional[list[list[int]]] = None,
    ) -> list[tuple[int, int]]:
        cache_key = (start, goal)
        if occupancy is None and cache_key in self.cache:
            return self.cache[cache_key]

        if self.algorithm == "astar":
            path = astar_search(self.grid, start, goal, occupancy)
        elif self.algorithm == "bfs":
            path = bfs_search(self.grid, start, goal, occupancy)
        elif self.algorithm == "dijkstra":
            path = dijkstra_search(self.grid, start, goal, occupancy)
        else:
            path = astar_search(self.grid, start, goal, occupancy)

        if path and occupancy is None:
            self.cache[cache_key] = path
        return path

    def replan(
        self,
        start: tuple[int, int],
        goal: tuple[int, int],
        occupancy: Optional[list[list[int]]] = None,
    ) -> list[tuple[int, int]]:
        self.cache.clear()
        return self.find_path(start, goal, occupancy)

    def set_algorithm(self, algorithm: str) -> None:
        self.algorithm = algorithm
        self.cache.clear()

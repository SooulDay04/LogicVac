from __future__ import annotations

import heapq
from typing import Optional


def heuristic(a: tuple[int, int], b: tuple[int, int]) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def astar_search(
    grid,
    start: tuple[int, int],
    goal: tuple[int, int],
    occupancy: Optional[list[list[int]]] = None,
) -> list[tuple[int, int]]:
    open_set: list[tuple[int, tuple[int, int]]] = [(0, start)]
    came_from: dict[tuple[int, int], tuple[int, int]] = {}
    g_score: dict[tuple[int, int], float] = {start: 0}
    closed_set: set[tuple[int, int]] = set()

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path[1:]

        if current in closed_set:
            continue
        closed_set.add(current)

        cx, cy = current
        for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
            neighbor = (nx, ny)
            if neighbor in closed_set:
                continue
            if not grid.is_walkable(nx, ny):
                continue
            if occupancy and occupancy[ny][nx] > 0:
                continue

            tentative_g = g_score[current] + 1
            if tentative_g < g_score.get(neighbor, float("inf")):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return []

from __future__ import annotations

from collections import deque
from typing import Optional


def bfs_search(
    grid,
    start: tuple[int, int],
    goal: tuple[int, int],
    occupancy: Optional[list[list[int]]] = None,
) -> list[tuple[int, int]]:
    queue: deque[tuple[tuple[int, int], list[tuple[int, int]]]] = deque()
    queue.append((start, []))
    visited: set[tuple[int, int]] = {start}

    while queue:
        current, path = queue.popleft()

        if current == goal:
            return path

        cx, cy = current
        for nx, ny in [(cx - 1, cy), (cx + 1, cy), (cx, cy - 1), (cx, cy + 1)]:
            neighbor = (nx, ny)
            if neighbor in visited:
                continue
            if not grid.is_walkable(nx, ny):
                continue
            if occupancy and occupancy[ny][nx] > 0:
                continue

            visited.add(neighbor)
            queue.append((neighbor, path + [neighbor]))

    return []

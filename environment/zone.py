from __future__ import annotations

from enum import Enum
from typing import Optional


class ZoneType(Enum):
    TRANSITABLE = "transitable"
    BLOCKED = "blocked"
    CRITICAL = "critical"


class Zone:
    def __init__(
        self,
        name: str,
        zone_type: ZoneType,
        x_start: int,
        y_start: int,
        x_end: int,
        y_end: int,
    ) -> None:
        self.name = name
        self.zone_type = zone_type
        self.x_start = x_start
        self.y_start = y_start
        self.x_end = x_end
        self.y_end = y_end

    def contains(self, x: int, y: int) -> bool:
        return (
            self.x_start <= x <= self.x_end
            and self.y_start <= y <= self.y_end
        )

    def is_blocked(self) -> bool:
        return self.zone_type == ZoneType.BLOCKED

    def is_critical(self) -> bool:
        return self.zone_type == ZoneType.CRITICAL

    def get_cells(self) -> list[tuple[int, int]]:
        cells = []
        for y in range(self.y_start, self.y_end + 1):
            for x in range(self.x_start, self.x_end + 1):
                cells.append((x, y))
        return cells

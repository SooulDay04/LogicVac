from enum import IntEnum


GRID_SIZE = 30
DEFAULT_SPEED = 1.0
MAX_STRESS = 100.0
STRESS_INCREMENT_RATE = 0.5
CONGESTION_THRESHOLD = 5
PANIC_THRESHOLD = 80.0
REPLANIFICATION_INTERVAL = 10


class CellType(IntEnum):
    EMPTY = 0
    WALL = 1
    OBSTACLE = 2
    EXIT = 3
    FLOOR = 4


CELL_COLORS = {
    CellType.EMPTY: (1.0, 1.0, 1.0),
    CellType.WALL: (0.0, 0.0, 0.0),
    CellType.OBSTACLE: (0.5, 0.5, 0.5),
    CellType.EXIT: (0.0, 1.0, 0.0),
    CellType.FLOOR: (0.8, 0.8, 0.8),
}


AGENT_STATES = ["IDLE", "MOVING", "EVACUATED", "BLOCKED", "PANIC"]

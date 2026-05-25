from enum import Enum


class AgentState(Enum):
    IDLE = "idle"
    MOVING = "moving"
    EVACUATED = "evacuated"
    BLOCKED = "blocked"
    PANIC = "panic"

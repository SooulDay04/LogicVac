from __future__ import annotations

from evacsim.agents.states import AgentState
from evacsim.config import DEFAULT_SPEED, MAX_STRESS


class AgentAttributes:
    def __init__(
        self,
        agent_id: int,
        speed: float = DEFAULT_SPEED,
        max_stress: float = MAX_STRESS,
    ) -> None:
        self.agent_id = agent_id
        self.speed = speed
        self.stress = 0.0
        self.max_stress = max_stress
        self.state = AgentState.IDLE

    def increase_stress(self, amount: float) -> None:
        self.stress = min(self.stress + amount, self.max_stress)

    def decrease_stress(self, amount: float) -> None:
        self.stress = max(self.stress - amount, 0.0)

    def set_state(self, state: AgentState) -> None:
        self.state = state

    def is_panic(self) -> bool:
        return self.state == AgentState.PANIC

    def is_evacuated(self) -> bool:
        return self.state == AgentState.EVACUATED

from __future__ import annotations

from typing import TYPE_CHECKING

from evacsim.agents.states import AgentState
from evacsim.config import PANIC_THRESHOLD

if TYPE_CHECKING:
    from evacsim.agents.person_agent import PersonAgent


class DecisionEngine:
    def __init__(self, agent: PersonAgent) -> None:
        self.agent = agent

    def decide(self) -> None:
        if self.agent.attributes.is_evacuated():
            return

        if self.agent.attributes.stress >= PANIC_THRESHOLD:
            self.agent.attributes.set_state(AgentState.PANIC)

        if self.agent.attributes.state in (
            AgentState.IDLE,
            AgentState.BLOCKED,
        ):
            self._find_path()

    def _find_path(self) -> None:
        target = self.agent.model.environment.building.get_nearest_exit(
            *self.agent.pos
        )
        if target is None:
            return

        route_manager = self.agent.model.route_manager
        path = route_manager.find_path(self.agent.pos, target)
        if path:
            self.agent.set_path(path)
        else:
            self.agent.attributes.set_state(AgentState.BLOCKED)

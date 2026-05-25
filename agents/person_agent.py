from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from mesa import Agent

from evacsim.agents.attributes import AgentAttributes
from evacsim.agents.states import AgentState
from evacsim.behavior.decision_engine import DecisionEngine
from evacsim.config import PANIC_THRESHOLD

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class PersonAgent(Agent):
    def __init__(
        self,
        unique_id: int,
        model: EvacuationModel,
        pos: tuple[int, int],
        speed: float = 1.0,
    ) -> None:
        self.model = model
        self.unique_id = unique_id
        
        # CAMBIO CLAVE: Inicializamos en None para cumplir las reglas de Mesa 2.x
        self.pos = None 

        self.attributes = AgentAttributes(unique_id, speed=speed)
        self.decision_engine = DecisionEngine(self)
        self.path: list[tuple[int, int]] = []
        self.path_index = 0
        self.steps_blocked = 0

    def step(self) -> None:
        if self.attributes.is_evacuated():
            return

        self.decision_engine.decide()

        if self.attributes.state == AgentState.MOVING:
            self._move()
        elif self.attributes.state == AgentState.BLOCKED:
            self.steps_blocked += 1
            if self.steps_blocked > 5:
                self.attributes.increase_stress(2.0)
                if self.attributes.stress >= PANIC_THRESHOLD:
                    self.attributes.set_state(AgentState.PANIC)

    def _move(self) -> None:
        if not self.path or self.path_index >= len(self.path):
            self.attributes.set_state(AgentState.IDLE)
            return

        next_pos = self.path[self.path_index]
        if self.model.grid.is_cell_empty(next_pos):
            self.model.grid.move_agent(self, next_pos)
            self.pos = next_pos
            self.path_index += 1
            self.steps_blocked = 0

            if self.model.environment.grid.get_cell(*next_pos) == 3:
                self.attributes.set_state(AgentState.EVACUATED)
                self.model.evacuated_count += 1
        else:
            self.steps_blocked += 1
            if self.steps_blocked > 3:
                self.attributes.set_state(AgentState.BLOCKED)

    def set_path(self, path: list[tuple[int, int]]) -> None:
        self.path = path
        self.path_index = 0
        if path:
            self.attributes.set_state(AgentState.MOVING)

    def get_position(self) -> tuple[int, int]:
        return self.pos

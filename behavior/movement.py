from __future__ import annotations

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from evacsim.agents.person_agent import PersonAgent


class MovementController:
    def __init__(self, agent: PersonAgent) -> None:
        self.agent = agent

    def can_move_to(self, pos: tuple[int, int]) -> bool:
        if not self.agent.model.grid.is_cell_empty(pos):
            return False
        neighbors = self.agent.model.grid.get_neighbors(pos)
        for neighbor in neighbors:
            if neighbor != self.agent.pos:
                agent_at = self._get_agent_at(neighbor)
                if agent_at is not None:
                    return False
        return True

    def get_valid_moves(self) -> list[tuple[int, int]]:
        x, y = self.agent.pos
        candidates = [(x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)]
        return [pos for pos in candidates if self.can_move_to(pos)]

    def move_toward(self, target: tuple[int, int]) -> Optional[tuple[int, int]]:
        valid_moves = self.get_valid_moves()
        if not valid_moves:
            return None

        best_move = min(
            valid_moves,
            key=lambda m: abs(m[0] - target[0]) + abs(m[1] - target[1]),
        )
        return best_move

    def _get_agent_at(self, pos: tuple[int, int]):
        for agent in self.agent.model.schedule.agents:
            if agent.pos == pos and agent != self.agent:
                return agent
        return None

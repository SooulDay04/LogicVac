from __future__ import annotations

from typing import TYPE_CHECKING

from evacsim.config import CONGESTION_THRESHOLD, STRESS_INCREMENT_RATE

if TYPE_CHECKING:
    from evacsim.agents.person_agent import PersonAgent


class StressModel:
    def __init__(self, agent: PersonAgent) -> None:
        self.agent = agent

    def calculate_local_density(self) -> int:
        count = 0
        x, y = self.agent.pos
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                nx, ny = x + dx, y + dy
                for other in self.agent.model.schedule.agents:
                    if other.pos == (nx, ny) and other != self.agent:
                        count += 1
        return count

    def update_stress(self) -> None:
        density = self.calculate_local_density()
        if density >= CONGESTION_THRESHOLD:
            self.agent.attributes.increase_stress(
                STRESS_INCREMENT_RATE * density
            )
        else:
            self.agent.attributes.decrease_stress(STRESS_INCREMENT_RATE * 0.1)

    def get_stress_level(self) -> str:
        stress = self.agent.attributes.stress
        if stress < 25:
            return "low"
        elif stress < 50:
            return "medium"
        elif stress < 80:
            return "high"
        return "critical"

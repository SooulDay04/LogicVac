from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from evacsim.agents.person_agent import PersonAgent


class SocialBehavior:
    def __init__(self, agent: PersonAgent, influence_radius: int = 5) -> None:
        self.agent = agent
        self.influence_radius = influence_radius

    def get_nearby_agents(self) -> list:
        nearby = []
        for other in self.agent.model.schedule.agents:
            if other == self.agent:
                continue
            dist = abs(other.pos[0] - self.agent.pos[0]) + abs(
                other.pos[1] - self.agent.pos[1]
            )
            if dist <= self.influence_radius:
                nearby.append(other)
        return nearby

    def get_crowd_direction(self) -> tuple[float, float]:
        nearby = self.get_nearby_agents()
        if not nearby:
            return 0.0, 0.0

        dx = sum(a.pos[0] - self.agent.pos[0] for a in nearby)
        dy = sum(a.pos[1] - self.agent.pos[1] for a in nearby)
        count = len(nearby)
        return dx / count, dy / count

    def should_follow_crowd(self) -> bool:
        nearby = self.get_nearby_agents()
        moving_count = sum(
            1 for a in nearby if a.attributes.state.value == "moving"
        )
        return moving_count > len(nearby) * 0.5

    def apply_social_influence(self) -> None:
        if not self.should_follow_crowd():
            return

        dx, dy = self.get_crowd_direction()
        if abs(dx) > 0.5 or abs(dy) > 0.5:
            self.agent.attributes.increase_stress(0.3)

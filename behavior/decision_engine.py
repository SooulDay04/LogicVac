from __future__ import annotations

from typing import TYPE_CHECKING

from evacsim.agents.personality import PersonalityType
from evacsim.agents.states import AgentState
from evacsim.config import CONGESTION_THRESHOLD, PANIC_THRESHOLD

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

        self._react_to_congestion()

        if self.agent.attributes.state == AgentState.IDLE:
            self._find_path()
        elif self.agent.attributes.state == AgentState.BLOCKED:
            self._find_path(force_replan=True, avoid_agents=True)
        elif self.agent.attributes.state == AgentState.PANIC and self._needs_path():
            self._find_path(force_replan=True, avoid_agents=True)
        elif self.agent.attributes.state in (AgentState.MOVING, AgentState.PANIC) and self._should_change_route():
            self._find_path(force_replan=True, avoid_agents=True)

    def _react_to_congestion(self) -> None:
        density = self._local_density()
        if density < CONGESTION_THRESHOLD:
            return

        model_stress = getattr(self.agent.model, "stress_level", 1.0)
        profile = self.agent.attributes.personality_profile
        self.agent.attributes.increase_stress(
            0.5 * density * model_stress * profile.congestion_stress_multiplier
        )

    def _should_change_route(self) -> bool:
        profile = self.agent.attributes.personality_profile
        if self._path_ahead_is_congested():
            return self.agent.model.random.random() < profile.route_change_probability
        return False

    def _find_path(
        self,
        force_replan: bool = False,
        avoid_agents: bool = False,
    ) -> None:
        target = self._choose_target()
        if target is None:
            return

        route_manager = self.agent.model.route_manager
        occupancy = self._occupancy_grid(target) if avoid_agents else None
        if force_replan:
            path = route_manager.replan(self.agent.pos, target, occupancy)
        else:
            path = route_manager.find_path(self.agent.pos, target, occupancy)
        if path:
            self.agent.set_path(path)
        else:
            self.agent.attributes.set_state(AgentState.BLOCKED)

    def _choose_target(self) -> tuple[int, int] | None:
        followed = self._get_followed_agent()
        if followed is not None and followed.path:
            return followed.path[-1]

        return self.agent.model.environment.building.get_nearest_exit(
            *self.agent.pos
        )

    def _get_followed_agent(self):
        profile = self.agent.attributes.personality_profile
        if self.agent.model.random.random() >= profile.follow_tendency:
            return None

        previous_target_id = getattr(self.agent, "follow_target_id", None)
        if self.agent.attributes.personality == PersonalityType.SEGUIDOR and previous_target_id is not None:
            for other in self.agent.model.schedule.agents:
                if (
                    other.unique_id == previous_target_id
                    and other.pos is not None
                    and other.path
                    and other.attributes.state == AgentState.MOVING
                ):
                    return other

        nearby = []
        for other in self.agent.model.schedule.agents:
            if other == self.agent or other.pos is None or not other.path:
                continue
            distance = abs(other.pos[0] - self.agent.pos[0]) + abs(
                other.pos[1] - self.agent.pos[1]
            )
            if distance <= 5 and other.attributes.state == AgentState.MOVING:
                nearby.append((distance, other))

        if not nearby:
            return None

        if self.agent.attributes.personality == PersonalityType.SEGUIDOR:
            nearby.sort(key=lambda item: (item[0], item[1].unique_id))
        else:
            nearby.sort(key=lambda item: item[0])

        followed = nearby[0][1]
        self.agent.follow_target_id = followed.unique_id
        return followed

    def _path_ahead_is_congested(self) -> bool:
        if not self.agent.path or self.agent.path_index >= len(self.agent.path):
            return False
        return self._is_position_congested(self.agent.path[self.agent.path_index])

    def _needs_path(self) -> bool:
        return not self.agent.path or self.agent.path_index >= len(self.agent.path)

    def _local_density(self) -> int:
        if self.agent.pos is None:
            return 0
        return self._density_at(self.agent.pos)

    def _is_position_congested(self, pos: tuple[int, int]) -> bool:
        return self._density_at(pos) >= CONGESTION_THRESHOLD

    def _density_at(self, pos: tuple[int, int]) -> int:
        px, py = pos
        count = 0
        for other in self.agent.model.schedule.agents:
            if other == self.agent or other.pos is None:
                continue
            if abs(other.pos[0] - px) <= 1 and abs(other.pos[1] - py) <= 1:
                count += 1
        return count

    def _occupancy_grid(self, target: tuple[int, int]) -> list[list[int]]:
        occupancy = [[0] * self.agent.model.grid_size for _ in range(self.agent.model.grid_size)]
        for other in self.agent.model.schedule.agents:
            if other == self.agent or other.pos is None:
                continue
            if other.pos == target:
                continue
            x, y = other.pos
            occupancy[y][x] = 1
        return occupancy

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

from evacsim.agents.attributes import AgentAttributes
from evacsim.agents.personality import PersonalityType
from evacsim.agents.states import AgentState
from evacsim.behavior.decision_engine import DecisionEngine
from evacsim.config import CellType, PANIC_THRESHOLD

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class PersonAgent(Agent):
    def __init__(
        self,
        unique_id: int,
        model: EvacuationModel,
        pos: tuple[int, int],
        speed: float = 1.0,
        personality: PersonalityType | str | None = None,
    ) -> None:
        self.model = model
        self.unique_id = unique_id
        
        # CAMBIO CLAVE: Inicializamos en None para cumplir las reglas de Mesa 2.x
        self.pos = None 

        self.attributes = AgentAttributes(unique_id, speed=speed, personality=personality)
        self.decision_engine = DecisionEngine(self)
        self.path: list[tuple[int, int]] = []
        self.path_index = 0
        self.steps_blocked = 0
        self.follow_target_id: int | None = None
        self.yielding_steps = 0

    def step(self) -> None:
        if self.attributes.is_evacuated():
            return
        if self._evacuate_if_on_exit():
            return

        self.decision_engine.decide()

        if self.attributes.state in (AgentState.MOVING, AgentState.PANIC):
            self._move()
        elif self.attributes.state == AgentState.BLOCKED:
            self.steps_blocked += 1
            blocked_threshold = self.attributes.personality_profile.blocked_step_threshold + 2
            if self.steps_blocked > blocked_threshold:
                model_stress = getattr(self.model, "stress_level", 1.0)
                stress_multiplier = self.attributes.personality_profile.congestion_stress_multiplier
                self.attributes.increase_stress(2.0 * model_stress * stress_multiplier)
                if self.attributes.stress >= PANIC_THRESHOLD:
                    self.attributes.set_state(AgentState.PANIC)

    def _move(self) -> None:
        attempts = self._movement_attempts()
        if attempts == 0:
            return

        for _ in range(attempts):
            if self.attributes.state not in (AgentState.MOVING, AgentState.PANIC):
                return
            self._move_one_cell()

    def _movement_attempts(self) -> int:
        speed = max(0.0, self.attributes.speed)
        attempts = int(speed)
        fractional_speed = speed - attempts
        if self.model.random.random() < fractional_speed:
            attempts += 1
        return attempts

    def _move_one_cell(self) -> None:
        if not self.path or self.path_index >= len(self.path):
            self.attributes.set_state(AgentState.IDLE)
            return

        if self._leader_should_yield():
            if self._yield_to_followers():
                return

        next_pos = self.path[self.path_index]
        if self._should_wait_for_leader_turn(next_pos):
            self.steps_blocked += 1
            self.attributes.set_state(AgentState.BLOCKED)
            return

        if self._can_enter(next_pos):
            self.model.grid.move_agent(self, next_pos)
            self.pos = next_pos
            self.path_index += 1
            self.steps_blocked = 0
            self.yielding_steps = 0
            self._evacuate_if_on_exit()
        elif self._try_push_into(next_pos):
            self.model.grid.move_agent(self, next_pos)
            self.pos = next_pos
            self.path_index += 1
            self.steps_blocked = 0
            self.yielding_steps = 0
            self._evacuate_if_on_exit()
        else:
            self.steps_blocked += 1
            blocked_threshold = self.attributes.personality_profile.blocked_step_threshold
            if self.steps_blocked > blocked_threshold:
                self.attributes.set_state(AgentState.BLOCKED)

    def _can_enter(self, pos: tuple[int, int]) -> bool:
        if not self.model.grid.is_cell_empty(pos):
            return False

        min_distance = self.attributes.personality_profile.min_distance
        if min_distance <= 0:
            return True
        if self.steps_blocked > 0 or self._is_near_exit(pos):
            return True

        px, py = pos
        for other in self.model.schedule.agents:
            if other == self or other.pos is None:
                continue
            distance = abs(other.pos[0] - px) + abs(other.pos[1] - py)
            if distance <= min_distance:
                return self.model.random.random() > 0.45
        return True

    def _try_push_into(self, pos: tuple[int, int]) -> bool:
        profile = self.attributes.personality_profile
        if profile.push_tendency <= 0:
            return False
        if self.model.random.random() > profile.push_tendency:
            return False

        pushed_agent = self._get_agent_at(pos)
        if pushed_agent is None or pushed_agent.attributes.is_evacuated():
            return False

        push_destination = self._find_push_destination(pushed_agent)
        if push_destination is None:
            return False

        self.model.grid.move_agent(pushed_agent, push_destination)
        pushed_agent.pos = push_destination
        pushed_agent.steps_blocked += 1
        pushed_agent.attributes.set_state(AgentState.BLOCKED)
        pushed_agent._evacuate_if_on_exit()
        return True

    def _find_push_destination(self, pushed_agent) -> tuple[int, int] | None:
        if self.pos is None or pushed_agent.pos is None:
            return None

        px, py = pushed_agent.pos
        sx, sy = self.pos
        dx = px - sx
        dy = py - sy
        candidates = [
            (px + dx, py + dy),
            (px + dy, py + dx),
            (px - dy, py - dx),
            (px - dx, py - dy),
        ]
        for candidate in candidates:
            x, y = candidate
            if not (0 <= x < self.model.grid_size and 0 <= y < self.model.grid_size):
                continue
            if not self.model.environment.grid.is_walkable(x, y):
                continue
            if self.model.grid.is_cell_empty(candidate):
                return candidate
        return None

    def _leader_should_yield(self) -> bool:
        profile = self.attributes.personality_profile
        return (
            profile.yield_near_exit
            and self.yielding_steps < 2
            and self.path
            and self.path_index >= max(0, len(self.path) - 3)
            and self._has_followers_behind()
        )

    def _yield_to_followers(self) -> bool:
        side_step = self._find_side_step()
        if side_step is None:
            return False
        self.model.grid.move_agent(self, side_step)
        self.pos = side_step
        self.steps_blocked = 0
        self.yielding_steps += 1
        self.attributes.set_state(AgentState.BLOCKED)
        self._evacuate_if_on_exit()
        return True

    def _find_side_step(self) -> tuple[int, int] | None:
        if self.pos is None:
            return None

        x, y = self.pos
        if self.path_index < len(self.path):
            nx, ny = self.path[self.path_index]
            forward = (nx - x, ny - y)
        else:
            forward = (1, 0)

        candidates = [
            (x + forward[1], y + forward[0]),
            (x - forward[1], y - forward[0]),
            (x - forward[0], y - forward[1]),
        ]
        for candidate in candidates:
            cx, cy = candidate
            if not (0 <= cx < self.model.grid_size and 0 <= cy < self.model.grid_size):
                continue
            if not self.model.environment.grid.is_walkable(cx, cy):
                continue
            if self.model.grid.is_cell_empty(candidate):
                return candidate
        return None

    def _has_followers_behind(self) -> bool:
        if self.pos is None:
            return False
        x, y = self.pos
        for other in self.model.schedule.agents:
            if other == self or other.pos is None:
                continue
            distance = abs(other.pos[0] - x) + abs(other.pos[1] - y)
            if distance <= 3:
                return True
        return False

    def _is_near_exit(self, pos: tuple[int, int]) -> bool:
        exits = self.model.environment.grid.get_exits()
        return any(abs(ex - pos[0]) + abs(ey - pos[1]) <= 2 for ex, ey in exits)

    def _get_agent_at(self, pos: tuple[int, int]):
        for other in self.model.schedule.agents:
            if other != self and other.pos == pos:
                return other
        return None

    def _evacuate_if_on_exit(self) -> bool:
        if self.pos is None:
            return False
        if self.model.environment.grid.get_cell(*self.pos) != CellType.EXIT:
            return False
        if self.attributes.personality == PersonalityType.LIDER:
            if self.model.leader_exit_lock:
                self.attributes.set_state(AgentState.BLOCKED)
                return False
            self.model.leader_exit_lock = True

        self.attributes.set_state(AgentState.EVACUATED)
        self.model.evacuated_count += 1
        self.model.grid.remove_agent(self)
        self.pos = None
        return True

    def force_evacuate(self) -> bool:
        if self.attributes.is_evacuated():
            return False
        if self.pos is not None:
            self.model.grid.remove_agent(self)
        self.attributes.set_state(AgentState.EVACUATED)
        self.model.evacuated_count += 1
        self.pos = None
        return True

    def _should_wait_for_leader_turn(self, next_pos: tuple[int, int]) -> bool:
        if self.attributes.personality != PersonalityType.LIDER:
            return False
        if self.model.environment.grid.get_cell(*next_pos) != CellType.EXIT:
            return False
        return self.model.leader_exit_lock

    def set_path(self, path: list[tuple[int, int]]) -> None:
        self.path = path
        self.path_index = 0
        if path:
            if self.attributes.state != AgentState.PANIC:
                self.attributes.set_state(AgentState.MOVING)

    def get_position(self) -> tuple[int, int]:
        return self.pos

from __future__ import annotations

import random
from typing import Optional

from evacsim.config import GRID_SIZE
from evacsim.environment.building import Building
from evacsim.environment.grid import Grid
from evacsim.engine.simulation_history import SimulationHistory


class EvacuationModel:
    def __init__(
        self,
        num_agents: int = 25,
        grid_size: int = GRID_SIZE,
        seed: Optional[int] = None,
        stress_level: float = 1.0,
    ) -> None:
        if seed is not None:
            random.seed(seed)

        # SOLUCIÓN AL ERROR DE 'random': Creamos una instancia local de Random para el modelo
        self.random = random.Random(seed)

        self.num_agents = num_agents
        self.grid_size = grid_size
        self.stress_level = max(0.1, float(stress_level))
        self.running = True
        self.schedule: Optional[EvacuationScheduler] = None
        self.environment: Optional[Environment] = None
        self.route_manager: Optional[RouteManager] = None
        self.evacuated_count = 0
        self.current_step = 0
        self.metrics_collector: Optional[MetricsCollector] = None
        self.heatmap_tracker = None
        self.simulation_history = SimulationHistory()
        self.scenario_name = "scenario_1"
        self.leader_exit_lock = False

    def setup(self) -> None:
        from evacsim.engine.scheduler import EvacuationScheduler
        from evacsim.heatmaps.tracker import HeatmapTracker
        from evacsim.metrics.collector import MetricsCollector
        from evacsim.routing.route_manager import RouteManager

        grid = Grid(self.grid_size)
        grid.fill_floor()
        building = Building(grid)
        building.add_exit(self.grid_size - 1, self.grid_size // 2)
        self.environment = Environment(grid, building)

        self.route_manager = RouteManager(grid)
        self.schedule = EvacuationScheduler(self)
        self.metrics_collector = MetricsCollector()
        self.heatmap_tracker = HeatmapTracker(self.grid_size)
        self.leader_exit_lock = False

        start_cells = [
            (x, y)
            for x in range(self.grid_size // 3 + 1)
            for y in range(self.grid_size)
        ]
        self.random.shuffle(start_cells)

        for i in range(self.num_agents):
            from evacsim.agents.personality import PersonalityType
            from evacsim.agents.person_agent import PersonAgent

            if i < len(start_cells):
                x, y = start_cells[i]
            else:
                x = self.random.randint(0, self.grid_size // 3)
                y = self.random.randint(0, self.grid_size - 1)

            personalities = list(PersonalityType)
            personality = personalities[i % len(personalities)]
            agent = PersonAgent(i, self, (x, y), personality=personality)
            
            self.schedule.add_agent(agent)
            
            self.grid.place_agent(agent, (x, y))
            agent._record_position((x, y))

        self.clear_timeline_cache(record_initial=True)

    def step(self) -> None:
        # One leader can complete exit per simulation tick.
        self.leader_exit_lock = False
        if self.schedule is not None:
            self.schedule.step()
        self._resolve_two_leader_endgame()
        self.current_step += 1

        if self.metrics_collector is not None:
            self.metrics_collector.collect_step(self)
        if self.heatmap_tracker is not None and self.schedule is not None:
            self.heatmap_tracker.record_step(self.schedule.agents)

        if self.evacuated_count >= self.num_agents:
            self.running = False
        self.simulation_history.capture(self)

    def _resolve_two_leader_endgame(self) -> None:
        from evacsim.agents.personality import PersonalityType

        if self.schedule is None or self.environment is None:
            return

        remaining = [
            agent
            for agent in self.schedule.agents
            if not agent.attributes.is_evacuated() and agent.pos is not None
        ]
        leaders = [
            agent
            for agent in remaining
            if agent.attributes.personality == PersonalityType.LIDER
        ]

        if len(leaders) != 2:
            return

        is_endgame = len(remaining) <= 6
        blocked_deadlock = all(agent.steps_blocked >= 4 for agent in leaders)
        if not (is_endgame or blocked_deadlock):
            return

        exits = self.environment.grid.get_exits()
        if not exits:
            return

        def leader_rank(agent) -> tuple[int, int, int]:
            distance = min(
                abs(agent.pos[0] - ex) + abs(agent.pos[1] - ey)
                for ex, ey in exits
            )
            return (distance, -agent.steps_blocked, agent.unique_id)

        chosen = min(leaders, key=leader_rank)
        chosen.force_evacuate()

    def run(self, max_steps: int = 500) -> None:
        self.running = True
        for _ in range(max_steps):
            if not self.running:
                break
            self.step()

    def reset(self) -> None:
        self.running = False
        self.evacuated_count = 0
        self.current_step = 0
        self.setup()

    def clear_timeline_cache(self, record_initial: bool = True) -> None:
        from evacsim.heatmaps.tracker import HeatmapTracker

        if self.metrics_collector is not None:
            self.metrics_collector.clear()
        self.heatmap_tracker = HeatmapTracker(self.grid_size)
        self.simulation_history.clear()

        if record_initial and self.schedule is not None:
            self.heatmap_tracker.record_step(self.schedule.agents)
            self.simulation_history.capture(self)

    @property
    def grid(self):
        from mesa.space import SingleGrid

        if not hasattr(self, "_grid"):
            self._grid = SingleGrid(self.grid_size, self.grid_size, False)
        return self._grid


class Environment:
    def __init__(self, grid: Grid, building: Building) -> None:
        self.grid = grid
        self.building = building

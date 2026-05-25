from __future__ import annotations

import random
from typing import Optional

from evacsim.config import GRID_SIZE
from evacsim.environment.building import Building
from evacsim.environment.grid import Grid


class EvacuationModel:
    def __init__(
        self,
        num_agents: int = 25,
        grid_size: int = GRID_SIZE,
        seed: Optional[int] = None,
    ) -> None:
        if seed is not None:
            random.seed(seed)

        # SOLUCIÓN AL ERROR DE 'random': Creamos una instancia local de Random para el modelo
        self.random = random.Random(seed)

        self.num_agents = num_agents
        self.grid_size = grid_size
        self.running = True
        self.schedule: Optional[EvacuationScheduler] = None
        self.environment: Optional[Environment] = None
        self.route_manager: Optional[RouteManager] = None
        self.evacuated_count = 0
        self.current_step = 0
        self.metrics_collector: Optional[MetricsCollector] = None

    def setup(self) -> None:
        from evacsim.engine.scheduler import EvacuationScheduler
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

        for i in range(self.num_agents):
            from evacsim.agents.person_agent import PersonAgent

            x = random.randint(0, self.grid_size // 3)
            y = random.randint(0, self.grid_size - 1)
            
            agent = PersonAgent(i, self, (x, y))
            
            self.schedule.add_agent(agent)
            
            self.grid.place_agent(agent, (x, y))

    def step(self) -> None:
        if self.schedule is not None:
            self.schedule.step()
        self.current_step += 1

        if self.metrics_collector is not None:
            self.metrics_collector.collect_step(self)

        if self.evacuated_count >= self.num_agents:
            self.running = False

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
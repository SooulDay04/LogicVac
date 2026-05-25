from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent, Model

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class EvacuationScheduler:
    def __init__(self, model: EvacuationModel) -> None:
        self.model = model
        self._agents: list[Agent] = []
        self.steps = 0
        self.time = 0

    def step(self) -> None:
        agent_list = list(self._agents)
        self.model.random.shuffle(agent_list)
        for agent in agent_list:
            agent.step()
        self.steps += 1
        self.time += 1

    def add(self, agent: Agent) -> None:
        self._agents.append(agent)

    def add_agent(self, agent: Agent) -> None:
        self.add(agent)

    @property
    def agents(self) -> list[Agent]:
        return list(self._agents)

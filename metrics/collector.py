from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class MetricsCollector:
    def __init__(self) -> None:
        self.data: list[dict[str, Any]] = []
        self.evacuation_times: dict[int, int] = {}
        self.cell_transits: dict[tuple[int, int], int] = {}
        self.route_usage: dict[tuple[tuple[int, int], ...], int] = {}
        self._last_path_lengths: dict[int, int] = {}

    def collect_step(self, model: EvacuationModel) -> None:
        agents = (
            list(model.schedule.agents) if model.schedule is not None else []
        )
        total_agents = len(agents)
        evacuated = sum(
            1 for a in agents if a.attributes.is_evacuated()
        )
        moving = sum(
            1
            for a in agents
            if a.attributes.state.value == "moving"
        )
        blocked = sum(
            1
            for a in agents
            if a.attributes.state.value == "blocked"
        )
        panic = sum(
            1
            for a in agents
            if a.attributes.state.value == "panic"
        )
        avg_stress = (
            sum(a.attributes.stress for a in agents) / total_agents
            if total_agents > 0
            else 0.0
        )

        self.data.append(
            {
                "step": model.current_step,
                "total_agents": total_agents,
                "evacuated": evacuated,
                "moving": moving,
                "blocked": blocked,
                "panic": panic,
                "avg_stress": avg_stress,
                "evacuation_rate": evacuated / total_agents
                if total_agents > 0
                else 0.0,
            }
        )
        self._update_agent_metrics(agents, model.current_step)

    def _update_agent_metrics(self, agents: list[Any], step: int) -> None:
        for agent in agents:
            agent_id = int(agent.unique_id)
            if (
                agent.attributes.is_evacuated()
                and agent_id not in self.evacuation_times
            ):
                self.evacuation_times[agent_id] = step

            path_history = getattr(agent, "path_history", [])
            last_len = self._last_path_lengths.get(agent_id, 0)
            for pos in path_history[last_len:]:
                self.cell_transits[pos] = self.cell_transits.get(pos, 0) + 1
            self._last_path_lengths[agent_id] = len(path_history)

            if path_history:
                route = tuple(path_history)
                self.route_usage[route] = self.route_usage.get(route, 0) + 1

    def get_data(self) -> list[dict[str, Any]]:
        return self.data

    def get_evacuation_times(self) -> dict[int, int]:
        return self.evacuation_times

    def get_cell_transits(self) -> dict[tuple[int, int], int]:
        return self.cell_transits

    def get_route_usage(self) -> dict[tuple[tuple[int, int], ...], int]:
        return self.route_usage

    def clear(self) -> None:
        self.data.clear()
        self.evacuation_times.clear()
        self.cell_transits.clear()
        self.route_usage.clear()
        self._last_path_lengths.clear()

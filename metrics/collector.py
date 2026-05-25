from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class MetricsCollector:
    def __init__(self) -> None:
        self.data: list[dict[str, Any]] = []

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

    def get_data(self) -> list[dict[str, Any]]:
        return self.data

    def clear(self) -> None:
        self.data.clear()

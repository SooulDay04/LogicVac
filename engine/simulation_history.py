from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class SimulationHistory:
    def __init__(self) -> None:
        self.snapshots: list[dict[str, Any]] = []

    def clear(self) -> None:
        self.snapshots.clear()

    def capture(self, model: EvacuationModel) -> dict[str, Any]:
        snapshot = self._build_snapshot(model)
        if self.snapshots and self.snapshots[-1]["tick"] == snapshot["tick"]:
            self.snapshots[-1] = snapshot
        else:
            self.snapshots.append(snapshot)
        return snapshot

    def get(self, tick: int | None) -> dict[str, Any] | None:
        if not self.snapshots:
            return None
        if tick is None:
            return self.snapshots[-1]
        tick = max(0, min(int(tick), self.latest_tick))
        for snapshot in self.snapshots:
            if snapshot["tick"] == tick:
                return snapshot
        return self.snapshots[-1]

    @property
    def latest_tick(self) -> int:
        if not self.snapshots:
            return 0
        return int(self.snapshots[-1]["tick"])

    def _build_snapshot(self, model: EvacuationModel) -> dict[str, Any]:
        agents = list(model.schedule.agents) if model.schedule is not None else []
        metrics_data = (
            deepcopy(model.metrics_collector.get_data())
            if model.metrics_collector is not None
            else []
        )
        evacuation_times = (
            dict(model.metrics_collector.get_evacuation_times())
            if model.metrics_collector is not None
            else {}
        )
        cell_transits = (
            dict(model.metrics_collector.get_cell_transits())
            if model.metrics_collector is not None
            else {}
        )
        route_usage = (
            dict(model.metrics_collector.get_route_usage())
            if model.metrics_collector is not None
            else {}
        )

        heatmap = {"cumulative_density": [], "occupancy_counts": [], "max_density": 0.0}
        if model.heatmap_tracker is not None:
            heatmap = {
                "cumulative_density": model.heatmap_tracker.cumulative_density.tolist(),
                "occupancy_counts": model.heatmap_tracker.occupancy_counts.tolist(),
                "max_density": model.heatmap_tracker.max_density(),
                "steps_recorded": model.heatmap_tracker.steps_recorded,
            }

        return {
            "tick": int(model.current_step),
            "elapsed_time": int(model.current_step),
            "running": bool(model.running),
            "evacuated_count": int(model.evacuated_count),
            "total_agents": int(model.num_agents),
            "agents": [self._agent_snapshot(agent) for agent in agents],
            "metrics": {
                "current": deepcopy(metrics_data[-1]) if metrics_data else {},
                "series": metrics_data,
                "evacuation_times": evacuation_times,
                "cell_transits": cell_transits,
                "route_usage": route_usage,
            },
            "heatmap": heatmap,
        }

    def _agent_snapshot(self, agent: object) -> dict[str, Any]:
        attributes = agent.attributes
        return {
            "id": int(agent.unique_id),
            "position": tuple(agent.pos) if agent.pos is not None else None,
            "state": attributes.state.value,
            "evacuated": attributes.is_evacuated(),
            "personality": attributes.personality.value,
            "stress": float(attributes.stress),
            "speed": float(attributes.speed),
            "path": list(getattr(agent, "path", [])),
            "path_index": int(getattr(agent, "path_index", 0)),
            "path_history": list(getattr(agent, "path_history", [])),
            "optimal_path": list(getattr(agent, "optimal_path", [])),
            "steps_blocked": int(getattr(agent, "steps_blocked", 0)),
        }

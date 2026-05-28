from __future__ import annotations

from typing import TYPE_CHECKING, Any

import plotly.graph_objects as go

from evacsim.agents.personality import PERSONALITY_PROFILES, PersonalityType
from evacsim.config import CellType

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


CELL_COLOR_SCALE = [
    [0.00, "#ffffff"],  # EMPTY
    [0.25, "#1f2933"],  # WALL
    [0.50, "#7f8c8d"],  # OBSTACLE
    [0.75, "#16a34a"],  # EXIT
    [1.00, "#f3f4f6"],  # FLOOR
]


class PlotlyGridRenderer:
    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size

    def render(
        self,
        model: EvacuationModel,
        view_revision: int = 0,
        visible_personalities: list[str] | None = None,
        show_trajectories: bool = False,
        trajectory_mode: str = "all",
        selected_agent_id: int | None = None,
        show_heatmap: bool = False,
    ) -> go.Figure:
        return self._render(
            model,
            self._agents_from_model(model),
            self._heatmap_from_model(model),
            view_revision,
            visible_personalities,
            show_trajectories,
            trajectory_mode,
            selected_agent_id,
            show_heatmap,
        )

    def render_snapshot(
        self,
        model: EvacuationModel,
        snapshot: dict[str, Any],
        view_revision: int = 0,
        visible_personalities: list[str] | None = None,
        show_trajectories: bool = False,
        trajectory_mode: str = "all",
        selected_agent_id: int | None = None,
        show_heatmap: bool = False,
    ) -> go.Figure:
        return self._render(
            model,
            list(snapshot.get("agents", [])),
            snapshot.get("heatmap", {}),
            view_revision,
            visible_personalities,
            show_trajectories,
            trajectory_mode,
            selected_agent_id,
            show_heatmap,
        )

    def _render(
        self,
        model: EvacuationModel,
        agent_rows: list[dict[str, Any]],
        heatmap: dict[str, Any],
        view_revision: int = 0,
        visible_personalities: list[str] | None = None,
        show_trajectories: bool = False,
        trajectory_mode: str = "all",
        selected_agent_id: int | None = None,
        show_heatmap: bool = False,
    ) -> go.Figure:
        env_grid = model.environment.grid
        grid_size = model.grid_size
        z = [
            [int(env_grid.get_cell(x, y)) for x in range(grid_size)]
            for y in range(grid_size)
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Heatmap(
                z=z,
                colorscale=CELL_COLOR_SCALE,
                zmin=int(CellType.EMPTY),
                zmax=int(CellType.FLOOR),
                showscale=False,
                hoverinfo="skip",
            )
        )
        if show_heatmap:
            self._add_heatmap_trace(fig, heatmap)

        visible_set = set(visible_personalities or [p.value for p in PersonalityType])
        visible_agents = [
            agent
            for agent in agent_rows
            if agent.get("personality") in visible_set
        ]
        if show_trajectories:
            self._add_trajectory_traces(
                fig,
                visible_agents,
                trajectory_mode,
                selected_agent_id,
            )

        agents = [
            agent
            for agent in visible_agents
            if not agent.get("evacuated") and agent.get("position") is not None
        ]
        for personality in PersonalityType:
            group_agents = [
                agent
                for agent in agents
                if agent.get("personality") == personality.value
            ]
            if not group_agents:
                continue

            profile = PERSONALITY_PROFILES[personality]
            fig.add_trace(
                go.Scatter(
                    x=[agent["position"][0] for agent in group_agents],
                    y=[agent["position"][1] for agent in group_agents],
                    mode="markers",
                    marker={
                        "size": 11,
                        "color": profile.color,
                        "line": {"width": 1.5, "color": "#ffffff"},
                    },
                    hovertemplate="%{text}<extra></extra>",
                    text=[
                        f"Agente {agent['id']} | {profile.label}"
                        for agent in group_agents
                    ],
                    name=profile.label,
                )
            )

        fig.update_layout(
            margin={"l": 16, "r": 16, "t": 16, "b": 16},
            paper_bgcolor="#f8fafc",
            plot_bgcolor="#f8fafc",
            xaxis={
                "range": [-0.5, grid_size - 0.5],
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
                "scaleanchor": "y",
                "constrain": "domain",
            },
            yaxis={
                "range": [grid_size - 0.5, -0.5],
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
                "constrain": "domain",
            },
            showlegend=False,
            width=720,
            height=720,
            transition={"duration": 120, "easing": "linear"},
            uirevision=f"evacsim-grid-{view_revision}",
        )
        return fig

    def _agents_from_model(self, model: EvacuationModel) -> list[dict[str, Any]]:
        agents = list(model.schedule.agents) if model.schedule is not None else []
        return [
            {
                "id": int(agent.unique_id),
                "position": tuple(agent.pos) if agent.pos is not None else None,
                "evacuated": agent.attributes.is_evacuated(),
                "personality": agent.attributes.personality.value,
                "path_history": list(getattr(agent, "path_history", [])),
                "optimal_path": list(getattr(agent, "optimal_path", [])),
            }
            for agent in agents
        ]

    def _heatmap_from_model(self, model: EvacuationModel) -> dict[str, Any]:
        tracker = getattr(model, "heatmap_tracker", None)
        if tracker is None:
            return {"cumulative_density": [], "max_density": 0.0}
        return {
            "cumulative_density": tracker.cumulative_density.tolist(),
            "max_density": tracker.max_density(),
        }

    def _add_heatmap_trace(self, fig: go.Figure, heatmap: dict[str, Any]) -> None:
        max_density = float(heatmap.get("max_density", 0.0) or 0.0)
        if max_density <= 0:
            return

        fig.add_trace(
            go.Heatmap(
                z=heatmap.get("cumulative_density", []),
                colorscale="YlOrRd",
                zmin=0,
                zmax=max_density,
                opacity=0.62,
                colorbar={"title": "Densidad"},
                hovertemplate=(
                    "Celda (%{x}, %{y})<br>"
                    "Densidad acumulada: %{z:.2f}<extra></extra>"
                ),
                name="Mapa de calor",
            )
        )

    def _add_trajectory_traces(
        self,
        fig: go.Figure,
        agents,
        trajectory_mode: str,
        selected_agent_id: int | None,
    ) -> None:
        selected_agent = next(
            (agent for agent in agents if agent.get("id") == selected_agent_id),
            agents[0] if agents else None,
        )

        if trajectory_mode in ("all", "both"):
            for agent in agents:
                self._add_real_path_trace(
                    fig,
                    agent,
                    "#64748b",
                    1.5,
                    0.28,
                    showlegend=False,
                    name=f"Ruta real agente {agent['id']}",
                )

        if selected_agent is None:
            return

        if trajectory_mode in ("individual", "both", "comparison"):
            self._add_real_path_trace(
                fig,
                selected_agent,
                "#e11d48",
                3,
                0.95,
                showlegend=False,
                name=f"Ruta real agente {selected_agent['id']}",
            )

        if trajectory_mode == "comparison":
            self._add_optimal_path_trace(fig, selected_agent)

    def _add_real_path_trace(
        self,
        fig: go.Figure,
        agent,
        color: str,
        width: float,
        opacity: float,
        showlegend: bool,
        name: str,
    ) -> None:
        history = agent.get("path_history", [])
        if len(history) < 2:
            return

        fig.add_trace(
            go.Scatter(
                x=[pos[0] for pos in history],
                y=[pos[1] for pos in history],
                mode="lines",
                line={"color": color, "width": width},
                opacity=opacity,
                hovertemplate=(
                    f"Agente {agent['id']}<br>"
                    f"Camino recorrido: {self._walked_path_length(history)} celdas"
                    "<extra></extra>"
                ),
                name=name,
                showlegend=showlegend,
            )
        )

    def _add_optimal_path_trace(self, fig: go.Figure, agent) -> None:
        optimal_path = agent.get("optimal_path", [])
        if len(optimal_path) < 2:
            return

        fig.add_trace(
            go.Scatter(
                x=[pos[0] for pos in optimal_path],
                y=[pos[1] for pos in optimal_path],
                mode="lines",
                line={"color": "#0f766e", "width": 3, "dash": "dash"},
                opacity=0.9,
                hovertemplate=(
                    f"Ruta optima agente {agent['id']}<br>"
                    f"Longitud optima: {len(optimal_path) - 1} celdas"
                    "<extra></extra>"
                ),
                name=f"Ruta optima agente {agent['id']}",
                showlegend=False,
            )
        )

    def _walked_path_length(self, history: list[tuple[int, int]]) -> int:
        if len(history) < 2:
            return 0
        return sum(
            abs(current[0] - previous[0]) + abs(current[1] - previous[1])
            for previous, current in zip(history, history[1:])
        )

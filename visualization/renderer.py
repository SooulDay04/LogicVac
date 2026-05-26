from __future__ import annotations

from typing import TYPE_CHECKING

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
    ) -> go.Figure:
        env_grid = model.environment.grid
        z = [
            [int(env_grid.get_cell(x, y)) for x in range(self.grid_size)]
            for y in range(self.grid_size)
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

        visible_set = set(visible_personalities or [p.value for p in PersonalityType])
        agents = [
            agent
            for agent in model.schedule.agents
            if not agent.attributes.is_evacuated() and agent.pos is not None
            and agent.attributes.personality.value in visible_set
        ]
        for personality in PersonalityType:
            group_agents = [
                agent
                for agent in agents
                if agent.attributes.personality == personality
            ]
            if not group_agents:
                continue

            profile = PERSONALITY_PROFILES[personality]
            fig.add_trace(
                go.Scatter(
                    x=[agent.pos[0] for agent in group_agents],
                    y=[agent.pos[1] for agent in group_agents],
                    mode="markers",
                    marker={
                        "size": 11,
                        "color": profile.color,
                        "line": {"width": 1.5, "color": "#ffffff"},
                    },
                    hovertemplate="%{text}<extra></extra>",
                    text=[
                        f"Agente {agent.unique_id} | {profile.label}"
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
                "range": [-0.5, self.grid_size - 0.5],
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
                "scaleanchor": "y",
                "constrain": "domain",
            },
            yaxis={
                "range": [self.grid_size - 0.5, -0.5],
                "showgrid": False,
                "zeroline": False,
                "showticklabels": False,
                "constrain": "domain",
            },
            showlegend=True,
            width=720,
            height=720,
            transition={"duration": 120, "easing": "linear"},
            uirevision=f"evacsim-grid-{view_revision}",
        )
        return fig

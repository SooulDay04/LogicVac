from __future__ import annotations

from typing import TYPE_CHECKING

import plotly.graph_objects as go

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

    def render(self, model: EvacuationModel, view_revision: int = 0) -> go.Figure:
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

        agents = [
            agent
            for agent in model.schedule.agents
            if not agent.attributes.is_evacuated() and agent.pos is not None
        ]
        if agents:
            fig.add_trace(
                go.Scatter(
                    x=[agent.pos[0] for agent in agents],
                    y=[agent.pos[1] for agent in agents],
                    mode="markers",
                    marker={
                        "size": 11,
                        "color": "#2563eb",
                        "line": {"width": 1.5, "color": "#ffffff"},
                    },
                    hovertemplate="Agente %{text}<extra></extra>",
                    text=[str(agent.unique_id) for agent in agents],
                    name="Agentes",
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
            showlegend=False,
            width=720,
            height=720,
            transition={"duration": 120, "easing": "linear"},
            uirevision=f"evacsim-grid-{view_revision}",
        )
        return fig

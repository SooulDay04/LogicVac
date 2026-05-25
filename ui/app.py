from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = PACKAGE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dash import Dash, Input, Output, State, callback_context, dcc, html

from evacsim.config import GRID_SIZE
from evacsim.engine.simulation import EvacuationModel
from evacsim.visualization.renderer import PlotlyGridRenderer


DEFAULT_AGENT_COUNT = 25
MAX_SIMULATION_SPEED = 10

model = None
renderer = PlotlyGridRenderer(GRID_SIZE)


def create_model(agent_count: int) -> EvacuationModel:
    simulation = EvacuationModel(num_agents=agent_count, grid_size=GRID_SIZE, seed=42)
    simulation.setup()
    apply_basic_visual_layout(simulation)
    return simulation


def apply_basic_visual_layout(simulation: EvacuationModel) -> None:
    grid = simulation.environment.grid
    building = simulation.environment.building

    if not building.walls and grid.size >= 12:
        wall_x = grid.size // 2
        gap_y = grid.size // 2
        for y in range(2, grid.size - 2):
            if y != gap_y:
                building.add_wall(wall_x, y)

    if not building.obstacles and grid.size >= 18:
        x1 = int(grid.size * 0.68)
        y1 = int(grid.size * 0.28)
        building.add_rectangular_obstacle(x1, y1, x1 + 2, y1 + 4)


def get_model() -> EvacuationModel:
    global model
    if model is None:
        model = create_model(DEFAULT_AGENT_COUNT)
    return model


def legend_item(color: str, label: str) -> html.Div:
    return html.Div(
        [
            html.Span(className="legend-swatch", style={"backgroundColor": color}),
            html.Span(label),
        ],
        className="legend-item",
    )


app = Dash(__name__, title="EvacSim")
server = app.server

app.layout = html.Div(
    [
        dcc.Store(id="is-running", data=False),
        dcc.Interval(id="simulation-clock", interval=500, n_intervals=0, disabled=True),
        html.Aside(
            [
                html.Div(
                    [
                        html.H1("EvacSim"),
                        html.Div(id="status-line", className="status-line"),
                    ],
                    className="brand-block",
                ),
                html.Div(
                    [
                        html.Button("Iniciar", id="start-button", n_clicks=0, className="primary-button"),
                        html.Button("Reiniciar", id="reset-button", n_clicks=0, className="secondary-button"),
                    ],
                    className="button-row",
                ),
                html.Div(
                    [
                        html.Label("Agentes"),
                        dcc.Slider(
                            id="agent-slider",
                            min=5,
                            max=150,
                            step=5,
                            value=DEFAULT_AGENT_COUNT,
                            marks={5: "5", 50: "50", 100: "100", 150: "150"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        html.Label("Velocidad"),
                        dcc.Slider(
                            id="speed-slider",
                            min=1,
                            max=MAX_SIMULATION_SPEED,
                            step=1,
                            value=2,
                            marks={1: "1x", 5: "5x", 10: "10x"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        legend_item("#1f2933", "Pared"),
                        legend_item("#16a34a", "Salida"),
                        legend_item("#7f8c8d", "Obstaculo"),
                        legend_item("#2563eb", "Agente"),
                    ],
                    className="legend",
                ),
            ],
            className="sidebar",
        ),
        html.Main(
            [
                dcc.Graph(
                    id="grid-view",
                    figure=renderer.render(get_model()),
                    config={"displayModeBar": False, "responsive": True},
                    className="grid-graph",
                )
            ],
            className="canvas",
        ),
    ],
    className="app-shell",
)

app.index_string = """
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            * { box-sizing: border-box; }
            body {
                margin: 0;
                background: #e5e7eb;
                color: #17202a;
                font-family: "Segoe UI", Tahoma, sans-serif;
            }
            .app-shell {
                display: grid;
                grid-template-columns: 320px 1fr;
                min-height: 100vh;
            }
            .sidebar {
                background: #f8fafc;
                border-right: 1px solid #d5dce5;
                padding: 28px 24px;
                display: flex;
                flex-direction: column;
                gap: 24px;
            }
            .brand-block h1 {
                margin: 0 0 8px;
                font-size: 34px;
                line-height: 1;
                color: #111827;
            }
            .status-line {
                min-height: 22px;
                color: #52606d;
                font-size: 14px;
            }
            .button-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 10px;
            }
            button {
                border: 0;
                border-radius: 6px;
                min-height: 42px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 700;
            }
            .primary-button {
                background: #0f766e;
                color: #ffffff;
            }
            .secondary-button {
                background: #dbe4ee;
                color: #17202a;
            }
            .control-group label {
                display: block;
                margin-bottom: 16px;
                font-size: 13px;
                font-weight: 800;
                text-transform: uppercase;
                color: #334155;
            }
            .legend {
                display: grid;
                gap: 10px;
                padding-top: 8px;
            }
            .legend-item {
                display: flex;
                align-items: center;
                gap: 10px;
                font-size: 14px;
                color: #334155;
            }
            .legend-swatch {
                width: 16px;
                height: 16px;
                border-radius: 4px;
                border: 1px solid rgba(15, 23, 42, 0.15);
            }
            .canvas {
                padding: 24px;
                display: flex;
                align-items: stretch;
            }
            .grid-graph {
                width: 100%;
                min-height: calc(100vh - 48px);
                background: #f8fafc;
                border: 1px solid #d5dce5;
                border-radius: 8px;
                overflow: hidden;
            }
            @media (max-width: 900px) {
                .app-shell {
                    grid-template-columns: 1fr;
                }
                .sidebar {
                    border-right: 0;
                    border-bottom: 1px solid #d5dce5;
                }
                .canvas {
                    padding: 16px;
                }
                .grid-graph {
                    min-height: 520px;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""


@app.callback(
    Output("is-running", "data"),
    Output("simulation-clock", "disabled"),
    Output("start-button", "children"),
    Input("start-button", "n_clicks"),
    Input("reset-button", "n_clicks"),
    State("is-running", "data"),
)
def sync_running_state(
    start_clicks: int,
    reset_clicks: int,
    is_running: bool,
) -> tuple[bool, bool, str]:
    triggered = [item["prop_id"] for item in callback_context.triggered]
    if any(prop.startswith("reset-button.") for prop in triggered):
        is_running = False
    elif any(prop.startswith("start-button.") for prop in triggered):
        is_running = not bool(is_running)

    return is_running, not is_running, "Pausar" if is_running else "Iniciar"


@app.callback(
    Output("simulation-clock", "interval"),
    Input("speed-slider", "value"),
)
def update_speed(speed: int) -> int:
    return max(80, int(1000 / max(speed, 1)))


@app.callback(
    Output("grid-view", "figure"),
    Output("status-line", "children"),
    Input("simulation-clock", "n_intervals"),
    Input("reset-button", "n_clicks"),
    State("agent-slider", "value"),
)
def update_simulation(
    n_intervals: int,
    reset_clicks: int,
    agent_count: int,
):
    global model
    triggered = [item["prop_id"] for item in callback_context.triggered]

    if any(prop.startswith("reset-button.") for prop in triggered):
        model = create_model(agent_count)
    elif n_intervals > 0 and any(prop.startswith("simulation-clock.") for prop in triggered):
        simulation = get_model()
        if simulation.running:
            simulation.step()

    simulation = get_model()
    status = f"Paso {simulation.current_step} | Evacuados {simulation.evacuated_count}/{simulation.num_agents}"
    return renderer.render(simulation), status


if __name__ == "__main__":
    app.run(debug=False)

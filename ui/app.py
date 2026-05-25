from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = PACKAGE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dash import Dash, Input, Output, State, callback_context, dcc, html

from evacsim.engine.simulation import EvacuationModel
from evacsim.ui.simulation_controller import SimulationController
from evacsim.visualization.renderer import PlotlyGridRenderer


DEFAULT_AGENT_COUNT = 25
MAX_SIMULATION_SPEED = 10
ROUTE_ALGORITHMS = ["astar", "bfs", "dijkstra"]

model = None
controller = SimulationController()
renderer = PlotlyGridRenderer(30)


def get_model() -> EvacuationModel:
    global model
    if model is None:
        model = controller.create_model(
            scenario_name=controller.default_scenario,
            agent_count=DEFAULT_AGENT_COUNT,
            route_algorithm=controller.default_algorithm,
            stress_level=controller.default_stress_level,
        )
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
                        html.Button("Vista", id="reset-view-button", n_clicks=0, className="secondary-button"),
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
                        html.Label("Nivel de estres"),
                        dcc.Slider(
                            id="stress-slider",
                            min=0.5,
                            max=2.0,
                            step=0.1,
                            value=1.0,
                            marks={0.5: "0.5x", 1.0: "1x", 1.5: "1.5x", 2.0: "2x"},
                            tooltip={"placement": "bottom", "always_visible": False},
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        html.Label("Escenario"),
                        dcc.Dropdown(
                            id="scenario-selector",
                            options=[
                                {"label": name.replace("_", " ").title(), "value": name}
                                for name in controller.list_scenarios()
                            ],
                            value=controller.default_scenario,
                            clearable=False,
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        html.Label("Algoritmo de ruta"),
                        dcc.Dropdown(
                            id="route-selector",
                            options=[{"label": algo.upper(), "value": algo} for algo in ROUTE_ALGORITHMS],
                            value=controller.default_algorithm,
                            clearable=False,
                        ),
                    ],
                    className="control-group",
                ),
                html.Button("Exportar datos", id="export-button", n_clicks=0, className="secondary-button"),
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
                    config={
                        "displayModeBar": True,
                        "displaylogo": False,
                        "responsive": False,
                        "modeBarButtonsToRemove": [
                            "lasso2d",
                            "select2d",
                            "autoScale2d",
                            "toggleSpikelines",
                        ],
                    },
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
                grid-template-columns: repeat(3, 1fr);
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
                height: 720px;
                max-height: calc(100vh - 48px);
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
                    height: 520px;
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
    Input("reset-view-button", "n_clicks"),
    Input("scenario-selector", "value"),
    Input("route-selector", "value"),
    Input("stress-slider", "value"),
    Input("export-button", "n_clicks"),
    State("agent-slider", "value"),
)
def update_simulation(
    n_intervals: int,
    reset_clicks: int,
    reset_view_clicks: int,
    scenario_name: str,
    route_algorithm: str,
    stress_level: float,
    export_clicks: int,
    agent_count: int,
):
    global model
    triggered = [item["prop_id"] for item in callback_context.triggered]

    if (
        model is None
        or any(
            prop.startswith(prefix)
            for prefix in (
                "reset-button.",
                "scenario-selector.",
                "stress-slider.",
                "agent-slider.",
            )
            for prop in triggered
        )
    ):
        model = controller.create_model(
            scenario_name=scenario_name,
            agent_count=agent_count,
            route_algorithm=route_algorithm,
            stress_level=stress_level,
        )
        model.scenario_name = scenario_name
    elif any(prop.startswith("route-selector.") for prop in triggered):
        simulation = get_model()
        simulation.route_manager.set_algorithm(route_algorithm)
    elif any(prop.startswith("export-button.") for prop in triggered):
        simulation = get_model()
        paths, rows = controller.export_metrics(simulation)
        exported = ", ".join(Path(p).name for p in paths) if paths else "sin archivos"
        status = f"Paso {simulation.current_step} | Evacuados {simulation.evacuated_count}/{simulation.num_agents} | Exportado: {rows} filas ({exported})"
        return renderer.render(simulation, reset_view_clicks), status
    elif n_intervals > 0 and any(prop.startswith("simulation-clock.") for prop in triggered):
        simulation = get_model()
        if simulation.running:
            simulation.step()

    simulation = get_model()
    simulation.scenario_name = scenario_name
    status = f"Paso {simulation.current_step} | Evacuados {simulation.evacuated_count}/{simulation.num_agents}"
    return renderer.render(simulation, reset_view_clicks), status


if __name__ == "__main__":
    app.run(debug=False)

from __future__ import annotations

import sys
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parents[1]
PROJECT_DIR = PACKAGE_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from dash import Dash, Input, Output, State, callback_context, dcc, html

from evacsim.agents.personality import PERSONALITY_PROFILES, PersonalityType
from evacsim.engine.simulation import EvacuationModel
from evacsim.ui.simulation_controller import SimulationController
from evacsim.visualization.renderer import PlotlyGridRenderer


DEFAULT_AGENT_COUNT = 25
MAX_SIMULATION_SPEED = 10
ROUTE_ALGORITHMS = ["astar", "bfs", "dijkstra"]
PERSONALITY_OPTIONS = [
    {
        "label": PERSONALITY_PROFILES[personality].label,
        "value": personality.value,
    }
    for personality in PersonalityType
]

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
                html.Div(
                    [
                        html.Label("Personalidades visibles"),
                        dcc.Checklist(
                            id="personality-filter",
                            options=PERSONALITY_OPTIONS,
                            value=[personality.value for personality in PersonalityType],
                            className="personality-filter",
                            inputClassName="personality-filter-input",
                            labelClassName="personality-filter-label",
                        ),
                    ],
                    className="control-group",
                ),
                html.Div(
                    [
                        html.Label("Trayectorias"),
                        dcc.Checklist(
                            id="trajectory-toggle",
                            options=[{"label": "Mostrar trayectorias", "value": "show"}],
                            value=[],
                            className="trajectory-toggle",
                            inputClassName="personality-filter-input",
                            labelClassName="personality-filter-label",
                        ),
                        dcc.Dropdown(
                            id="trajectory-mode",
                            options=[
                                {"label": "Ruta de todos", "value": "all"},
                                {"label": "Ruta individual", "value": "individual"},
                                {"label": "Todos + individual", "value": "both"},
                                {"label": "Optima vs real", "value": "comparison"},
                            ],
                            value="all",
                            clearable=False,
                        ),
                        dcc.Dropdown(
                            id="trajectory-agent",
                            options=[],
                            value=0,
                            clearable=False,
                        ),
                        html.Div(id="path-summary", className="path-summary"),
                    ],
                    className="control-group trajectory-panel",
                ),
                html.Div(
                    [
                        html.Label("Mapa de calor"),
                        dcc.Checklist(
                            id="heatmap-toggle",
                            options=[{"label": "Mostrar mapa de calor", "value": "show"}],
                            value=["show"],
                            className="trajectory-toggle",
                            inputClassName="personality-filter-input",
                            labelClassName="personality-filter-label",
                        ),
                        html.Button(
                            "Exportar imagen",
                            id="export-heatmap-image-button",
                            n_clicks=0,
                            className="secondary-button",
                        ),
                        html.Button(
                            "Exportar CSV",
                            id="export-heatmap-csv-button",
                            n_clicks=0,
                            className="secondary-button",
                        ),
                    ],
                    className="control-group heatmap-panel",
                ),
                html.Button("Exportar datos", id="export-button", n_clicks=0, className="secondary-button"),
                html.Div(
                    [
                        legend_item("#1f2933", "Pared"),
                        legend_item("#16a34a", "Salida"),
                        legend_item("#7f8c8d", "Obstaculo"),
                        *[
                            legend_item(PERSONALITY_PROFILES[p].color, PERSONALITY_PROFILES[p].label)
                            for p in PersonalityType
                        ],
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
                    figure=renderer.render(get_model(), show_heatmap=True),
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
            .personality-filter {
                display: grid;
                grid-template-columns: repeat(2, minmax(0, 1fr));
                gap: 10px 12px;
                font-size: 14px;
                color: #334155;
            }
            .personality-filter-label {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 650;
                text-transform: none;
                margin: 0;
            }
            .personality-filter-input {
                accent-color: #0f766e;
            }
            .trajectory-panel {
                display: grid;
                gap: 12px;
            }
            .heatmap-panel {
                display: grid;
                gap: 12px;
            }
            .trajectory-toggle {
                font-size: 14px;
                color: #334155;
            }
            .path-summary {
                min-height: 42px;
                padding: 10px 12px;
                border: 1px solid #d5dce5;
                border-radius: 6px;
                background: #ffffff;
                color: #334155;
                font-size: 13px;
                line-height: 1.35;
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
    Output("trajectory-agent", "options"),
    Output("path-summary", "children"),
    Input("simulation-clock", "n_intervals"),
    Input("reset-button", "n_clicks"),
    Input("reset-view-button", "n_clicks"),
    Input("scenario-selector", "value"),
    Input("route-selector", "value"),
    Input("stress-slider", "value"),
    Input("export-button", "n_clicks"),
    Input("export-heatmap-image-button", "n_clicks"),
    Input("export-heatmap-csv-button", "n_clicks"),
    Input("personality-filter", "value"),
    Input("trajectory-toggle", "value"),
    Input("trajectory-mode", "value"),
    Input("trajectory-agent", "value"),
    Input("heatmap-toggle", "value"),
    State("agent-slider", "value"),
    State("is-running", "data"),
)
def update_simulation(
    n_intervals: int,
    reset_clicks: int,
    reset_view_clicks: int,
    scenario_name: str,
    route_algorithm: str,
    stress_level: float,
    export_clicks: int,
    export_heatmap_image_clicks: int,
    export_heatmap_csv_clicks: int,
    visible_personalities: list[str],
    trajectory_toggle: list[str],
    trajectory_mode: str,
    selected_agent_id: int | None,
    heatmap_toggle: list[str],
    agent_count: int,
    is_running: bool,
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
        agent_options, selected_agent_id = _trajectory_agent_options(simulation, selected_agent_id)
        show_trajectories = "show" in (trajectory_toggle or [])
        show_heatmap = "show" in (heatmap_toggle or [])
        return (
            renderer.render(
                simulation,
                reset_view_clicks,
                visible_personalities,
                show_trajectories,
                trajectory_mode,
                selected_agent_id,
                show_heatmap,
            ),
            status,
            agent_options,
            _path_summary(simulation, selected_agent_id, show_trajectories),
        )
    elif any(prop.startswith("export-heatmap-image-button.") for prop in triggered):
        simulation = get_model()
        path = controller.export_heatmap_image(simulation)
        status = _status_with_export(simulation, f"Imagen heatmap: {Path(path).name}")
        agent_options, selected_agent_id = _trajectory_agent_options(simulation, selected_agent_id)
        show_trajectories = "show" in (trajectory_toggle or [])
        show_heatmap = "show" in (heatmap_toggle or [])
        return (
            renderer.render(
                simulation,
                reset_view_clicks,
                visible_personalities,
                show_trajectories,
                trajectory_mode,
                selected_agent_id,
                show_heatmap,
            ),
            status,
            agent_options,
            _path_summary(simulation, selected_agent_id, show_trajectories),
        )
    elif any(prop.startswith("export-heatmap-csv-button.") for prop in triggered):
        simulation = get_model()
        paths = controller.export_heatmap_csv(simulation)
        exported = ", ".join(Path(p).name for p in paths)
        status = _status_with_export(simulation, f"CSV heatmap: {exported}")
        agent_options, selected_agent_id = _trajectory_agent_options(simulation, selected_agent_id)
        show_trajectories = "show" in (trajectory_toggle or [])
        show_heatmap = "show" in (heatmap_toggle or [])
        return (
            renderer.render(
                simulation,
                reset_view_clicks,
                visible_personalities,
                show_trajectories,
                trajectory_mode,
                selected_agent_id,
                show_heatmap,
            ),
            status,
            agent_options,
            _path_summary(simulation, selected_agent_id, show_trajectories),
        )
    elif _should_advance_simulation(triggered, n_intervals, is_running):
        simulation = get_model()
        if simulation.running:
            simulation.step()

    simulation = get_model()
    simulation.scenario_name = scenario_name
    status = f"Paso {simulation.current_step} | Evacuados {simulation.evacuated_count}/{simulation.num_agents}"
    agent_options, selected_agent_id = _trajectory_agent_options(simulation, selected_agent_id)
    show_trajectories = "show" in (trajectory_toggle or [])
    show_heatmap = "show" in (heatmap_toggle or [])
    return (
        renderer.render(
            simulation,
            reset_view_clicks,
            visible_personalities,
            show_trajectories,
            trajectory_mode,
            selected_agent_id,
            show_heatmap,
        ),
        status,
        agent_options,
        _path_summary(simulation, selected_agent_id, show_trajectories),
    )


def _status_with_export(simulation: EvacuationModel, exported: str) -> str:
    return (
        f"Paso {simulation.current_step} | "
        f"Evacuados {simulation.evacuated_count}/{simulation.num_agents} | "
        f"Exportado: {exported}"
    )


def _should_advance_simulation(
    triggered: list[str],
    n_intervals: int,
    is_running: bool,
) -> bool:
    return (
        bool(is_running)
        and n_intervals > 0
        and triggered == ["simulation-clock.n_intervals"]
    )


def _trajectory_agent_options(
    simulation: EvacuationModel,
    selected_agent_id: int | None,
) -> tuple[list[dict[str, int | str]], int | None]:
    agents = list(simulation.schedule.agents) if simulation.schedule is not None else []
    options = [
        {"label": f"Agente {agent.unique_id}", "value": agent.unique_id}
        for agent in agents
    ]
    valid_ids = {agent.unique_id for agent in agents}
    if selected_agent_id in valid_ids:
        return options, selected_agent_id
    return options, agents[0].unique_id if agents else None


def _path_summary(
    simulation: EvacuationModel,
    selected_agent_id: int | None,
    show_trajectories: bool,
) -> str:
    agents = list(simulation.schedule.agents) if simulation.schedule is not None else []
    selected_agent = next(
        (agent for agent in agents if agent.unique_id == selected_agent_id),
        None,
    )
    if selected_agent is None:
        return "Sin agentes disponibles."

    real_length = selected_agent.walked_path_length()
    optimal_length = max(0, len(getattr(selected_agent, "optimal_path", [])) - 1)
    visibility = "activas" if show_trajectories else "ocultas"
    return (
        f"Trayectorias {visibility}. "
        f"Agente {selected_agent.unique_id}: recorrido {real_length} celdas"
        f" | optima {optimal_length} celdas"
    )


if __name__ == "__main__":
    app.run(debug=False)

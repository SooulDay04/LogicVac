from __future__ import annotations

import argparse
import sys
from typing import Optional

from evacsim.config import GRID_SIZE
from evacsim.data.exporter import DataExporter
from evacsim.engine.scenario_loader import ScenarioLoader
from evacsim.engine.simulation import EvacuationModel
from evacsim.metrics.reporter import MetricsReporter
from evacsim.visualization.charts import MetricsCharts
from evacsim.visualization.grid_renderer import GridRenderer


def run_scenario(
    scenario_name: str,
    max_steps: int = 500,
    visualize: bool = False,
    export: bool = False,
) -> None:
    loader = ScenarioLoader()
    config = loader.load_scenario(scenario_name)

    print(f"Running {config['name']}: {config['description']}")
    print(f"  Agents: {config['num_agents']}")
    print(f"  Grid size: {config['grid_size']}")
    print(f"  Exits: {config['num_exits']}")
    print(f"  Obstacles: {config['has_obstacles']}")
    print()

    model = EvacuationModel(
        num_agents=config["num_agents"],
        grid_size=config["grid_size"],
        seed=config.get("seed"),
    )
    model.setup()

    renderer = GridRenderer(config["grid_size"])
    reporter = MetricsReporter()

    for step in range(max_steps):
        if not model.running:
            break
        model.step()

        if visualize and step % 50 == 0:
            renderer.render(model, show=False)

    if model.metrics_collector is not None:
        data = model.metrics_collector.get_data()
        report = reporter.generate_report(data, scenario_name)
        reporter.print_report(report)

        if export:
            exporter = DataExporter()
            exporter.export_csv(data, f"{scenario_name}_results.csv")
            print(f"\nData exported to evacsim/data/output/{scenario_name}_results.csv")

    print(f"\nSimulation complete. Final step: {model.current_step}")
    print(f"Evacuated: {model.evacuated_count}/{model.num_agents}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Evacuation Simulator")
    parser.add_argument(
        "--scenario",
        type=str,
        default="scenario_1",
        help="Scenario to run (scenario_1 to scenario_5)",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=500,
        help="Maximum number of steps",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Enable visualization",
    )
    parser.add_argument(
        "--export",
        action="store_true",
        help="Export results to CSV",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios",
    )

    args = parser.parse_args()

    if args.list:
        loader = ScenarioLoader()
        print("Available scenarios:")
        for name in loader.list_scenarios():
            config = loader.load_scenario(name)
            print(f"  {name}: {config['description']}")
        return

    run_scenario(
        scenario_name=args.scenario,
        max_steps=args.steps,
        visualize=args.visualize,
        export=args.export,
    )


if __name__ == "__main__":
    main()

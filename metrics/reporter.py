from __future__ import annotations

from typing import Any

from evacsim.metrics.calculator import MetricsCalculator


class MetricsReporter:
    def __init__(self) -> None:
        self.reports: list[dict[str, Any]] = []

    def generate_report(
        self,
        data: list[dict[str, Any]],
        scenario_name: str = "",
        evacuation_times: dict[int, int] | None = None,
        cell_transits: dict[tuple[int, int], int] | None = None,
        route_usage: dict[tuple[tuple[int, int], ...], int] | None = None,
    ) -> dict[str, Any]:
        summary = MetricsCalculator.summarize(data)
        evacuation_times = evacuation_times or {}
        cell_transits = cell_transits or {}
        route_usage = route_usage or {}
        mean_evac, std_evac = MetricsCalculator.mean_and_std_from_dict_values(
            evacuation_times
        )
        evacuated_per_tick = MetricsCalculator.evacuated_per_tick(data)
        top_cells = sorted(
            cell_transits.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:10]
        top_routes = sorted(
            route_usage.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:1]
        completion_ratio = (
            summary.get("final_evacuated", 0) / max(1, summary.get("total_agents", 1))
        )
        total_time = max(1, summary.get("total_steps", 0))
        scenario_efficiency = completion_ratio / total_time

        report = {
            "scenario": scenario_name,
            "summary": summary,
            "total_evacuation_time": summary.get("total_steps", 0),
            "individual_evacuation_time": evacuation_times,
            "average_evacuation_time": mean_evac,
            "std_evacuation_time": std_evac,
            "evacuated_per_tick": evacuated_per_tick,
            "max_congestion": MetricsCalculator.max_congestion(data),
            "most_transited_cells": [
                {"cell": cell, "transits": count}
                for cell, count in top_cells
            ],
            "most_used_route": {
                "route": top_routes[0][0] if top_routes else [],
                "uses": top_routes[0][1] if top_routes else 0,
            },
            "scenario_efficiency": scenario_efficiency,
            "data_points": len(data),
        }
        self.reports.append(report)
        return report

    def print_report(self, report: dict[str, Any]) -> None:
        print(f"Scenario: {report.get('scenario', 'N/A')}")
        summary = report.get("summary", {})
        print(f"  Total steps: {summary.get('total_steps', 0)}")
        print(f"  Final evacuated: {summary.get('final_evacuated', 0)}")
        print(f"  Total agents: {summary.get('total_agents', 0)}")
        print(f"  Throughput: {summary.get('throughput', 0):.4f}")
        print(f"  Mean stress: {summary.get('mean_stress', 0):.2f}")
        print(f"  Max avg stress: {summary.get('max_avg_stress', 0):.2f}")

    def compare_scenarios(
        self, reports: list[dict[str, Any]]
    ) -> dict[str, Any]:
        comparison = {}
        for report in reports:
            name = report.get("scenario", "unknown")
            summary = report.get("summary", {})
            comparison[name] = {
                "total_steps": summary.get("total_steps", 0),
                "throughput": summary.get("throughput", 0),
                "mean_stress": summary.get("mean_stress", 0),
            }
        return comparison

    def get_all_reports(self) -> list[dict[str, Any]]:
        return self.reports

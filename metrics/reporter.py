from __future__ import annotations

from typing import Any

from evacsim.metrics.calculator import MetricsCalculator


class MetricsReporter:
    def __init__(self) -> None:
        self.reports: list[dict[str, Any]] = []

    def generate_report(
        self, data: list[dict[str, Any]], scenario_name: str = ""
    ) -> dict[str, Any]:
        summary = MetricsCalculator.summarize(data)
        report = {
            "scenario": scenario_name,
            "summary": summary,
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

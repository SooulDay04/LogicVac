from __future__ import annotations

import math
from typing import Any


class MetricsCalculator:
    @staticmethod
    def calculate_mean(values: list[float]) -> float:
        if not values:
            return 0.0
        return sum(values) / len(values)

    @staticmethod
    def calculate_std_dev(values: list[float]) -> float:
        if len(values) < 2:
            return 0.0
        mean = MetricsCalculator.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / (len(values) - 1)
        return math.sqrt(variance)

    @staticmethod
    def calculate_total_evacuation_time(
        data: list[dict[str, Any]],
    ) -> int:
        if not data:
            return 0
        for record in reversed(data):
            if record.get("evacuation_rate", 0) >= 1.0:
                return record["step"]
        return data[-1]["step"] if data else 0

    @staticmethod
    def calculate_max_stress(data: list[dict[str, Any]]) -> float:
        if not data:
            return 0.0
        return max(record.get("avg_stress", 0) for record in data)

    @staticmethod
    def calculate_throughput(
        data: list[dict[str, Any]],
    ) -> float:
        if not data:
            return 0.0
        total_time = MetricsCalculator.calculate_total_evacuation_time(data)
        if total_time == 0:
            return 0.0
        final_evacuated = data[-1].get("evacuated", 0)
        return final_evacuated / total_time

    @staticmethod
    def summarize(data: list[dict[str, Any]]) -> dict[str, Any]:
        if not data:
            return {}

        stress_values = [r.get("avg_stress", 0) for r in data]
        return {
            "total_steps": MetricsCalculator.calculate_total_evacuation_time(
                data
            ),
            "max_avg_stress": MetricsCalculator.calculate_max_stress(data),
            "mean_stress": MetricsCalculator.calculate_mean(stress_values),
            "std_dev_stress": MetricsCalculator.calculate_std_dev(
                stress_values
            ),
            "throughput": MetricsCalculator.calculate_throughput(data),
            "final_evacuated": data[-1].get("evacuated", 0),
            "total_agents": data[-1].get("total_agents", 0),
        }

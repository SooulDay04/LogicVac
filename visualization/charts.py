from __future__ import annotations

from typing import Any, Optional

import matplotlib.pyplot as plt
import pandas as pd


class MetricsCharts:
    def __init__(self) -> None:
        pass

    def plot_evacuation_progress(
        self,
        data: list[dict[str, Any]],
        ax: Optional[plt.Axes] = None,
        show: bool = False,
    ) -> plt.Figure:
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        else:
            fig = ax.figure

        df = pd.DataFrame(data)
        ax.plot(df["step"], df["evacuated"], label="Evacuated", marker="o")
        ax.plot(df["step"], df["moving"], label="Moving", marker="s")
        ax.plot(df["step"], df["blocked"], label="Blocked", marker="^")
        ax.plot(df["step"], df["panic"], label="Panic", marker="x")

        ax.set_xlabel("Step")
        ax.set_ylabel("Agent Count")
        ax.set_title("Evacuation Progress")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if show:
            plt.show()

        return fig

    def plot_stress_over_time(
        self,
        data: list[dict[str, Any]],
        ax: Optional[plt.Axes] = None,
        show: bool = False,
    ) -> plt.Figure:
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(10, 6))
        else:
            fig = ax.figure

        df = pd.DataFrame(data)
        ax.plot(df["step"], df["avg_stress"], label="Avg Stress", color="red")
        ax.set_xlabel("Step")
        ax.set_ylabel("Stress Level")
        ax.set_title("Average Stress Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)

        if show:
            plt.show()

        return fig

    def plot_comparison(
        self,
        scenarios_data: dict[str, list[dict[str, Any]]],
        show: bool = False,
    ) -> plt.Figure:
        fig, axes = plt.subplots(2, 1, figsize=(10, 12))

        for name, data in scenarios_data.items():
            df = pd.DataFrame(data)
            axes[0].plot(
                df["step"], df["evacuation_rate"], label=name, marker="o"
            )
            axes[1].plot(
                df["step"], df["avg_stress"], label=name, marker="s"
            )

        axes[0].set_xlabel("Step")
        axes[0].set_ylabel("Evacuation Rate")
        axes[0].set_title("Evacuation Rate Comparison")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)

        axes[1].set_xlabel("Step")
        axes[1].set_ylabel("Avg Stress")
        axes[1].set_title("Stress Comparison")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)

        plt.tight_layout()

        if show:
            plt.show()

        return fig

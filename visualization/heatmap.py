from __future__ import annotations

from typing import Optional

import matplotlib.pyplot as plt
import numpy as np

from evacsim.crowd.density import DensityCalculator


class DensityHeatmap:
    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size
        self.calculator = DensityCalculator(grid_size)

    def plot(
        self,
        positions: list[tuple[int, int]],
        ax: Optional[plt.Axes] = None,
        show: bool = False,
    ) -> plt.Figure:
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        else:
            fig = ax.figure

        density = self.calculator.calculate_density(positions)
        density_array = np.array(density)

        im = ax.imshow(
            density_array, cmap="hot", interpolation="nearest"
        )
        fig.colorbar(im, ax=ax, label="Density")
        ax.set_title("Agent Density Heatmap")
        ax.set_xticks([])
        ax.set_yticks([])

        if show:
            plt.show()

        return fig

    def plot_comparison(
        self,
        density_snapshots: list[list[tuple[int, int]]],
        labels: Optional[list[str]] = None,
        show: bool = False,
    ) -> plt.Figure:
        n = len(density_snapshots)
        fig, axes = plt.subplots(1, n, figsize=(6 * n, 6))
        if n == 1:
            axes = [axes]

        if labels is None:
            labels = [f"Snapshot {i}" for i in range(n)]

        for i, positions in enumerate(density_snapshots):
            density = self.calculator.calculate_density(positions)
            density_array = np.array(density)
            axes[i].imshow(
                density_array, cmap="hot", interpolation="nearest"
            )
            axes[i].set_title(labels[i])
            axes[i].set_xticks([])
            axes[i].set_yticks([])

        plt.tight_layout()

        if show:
            plt.show()

        return fig

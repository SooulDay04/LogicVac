from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import matplotlib.pyplot as plt
import numpy as np

from evacsim.config import CELL_COLORS, CellType

if TYPE_CHECKING:
    from evacsim.engine.simulation import EvacuationModel


class GridRenderer:
    def __init__(self, grid_size: int) -> None:
        self.grid_size = grid_size

    def render(
        self,
        model: EvacuationModel,
        ax: Optional[plt.Axes] = None,
        show: bool = False,
    ) -> plt.Figure:
        if ax is None:
            fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        else:
            fig = ax.figure

        grid_image = self._build_grid_image(model)
        ax.imshow(grid_image, interpolation="nearest")

        agent_positions = [
            agent.pos
            for agent in model.schedule.agents
            if not agent.attributes.is_evacuated()
        ]
        if agent_positions:
            xs = [p[0] for p in agent_positions]
            ys = [p[1] for p in agent_positions]
            ax.scatter(xs, ys, c="blue", s=50, marker="o", zorder=3)

        ax.set_title(f"Step {model.current_step}")
        ax.set_xticks([])
        ax.set_yticks([])

        if show:
            plt.show()

        return fig

    def _build_grid_image(self, model: EvacuationModel) -> np.ndarray:
        env_grid = model.environment.grid
        image = np.zeros((self.grid_size, self.grid_size, 3))

        for y in range(self.grid_size):
            for x in range(self.grid_size):
                cell_type = env_grid.get_cell(x, y)
                color = CELL_COLORS.get(cell_type, (1.0, 1.0, 1.0))
                image[y, x] = color

        return image

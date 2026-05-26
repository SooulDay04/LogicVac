from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt

from evacsim.heatmaps.tracker import HeatmapTracker


class HeatmapExporter:
    def __init__(self, output_dir: str | Path) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def export_image(self, tracker: HeatmapTracker, filename: str) -> str:
        path = self.output_dir / filename
        fig, ax = plt.subplots(1, 1, figsize=(8, 8))
        image = ax.imshow(
            tracker.cumulative_density,
            cmap="hot",
            interpolation="nearest",
        )
        fig.colorbar(image, ax=ax, label="Densidad acumulada")
        ax.set_title("Mapa de calor acumulado")
        ax.set_xticks([])
        ax.set_yticks([])
        fig.tight_layout()
        fig.savefig(path, dpi=160)
        plt.close(fig)
        return str(path)

    def export_csv(self, tracker: HeatmapTracker, base_name: str) -> list[str]:
        cell_path = self.output_dir / f"{base_name}_cells.csv"
        route_path = self.output_dir / f"{base_name}_routes.csv"
        self._write_rows(
            cell_path,
            tracker.cell_rows(),
            ["x", "y", "occupancy_count", "cumulative_density", "congestion_rank"],
        )
        self._write_rows(
            route_path,
            tracker.route_rows(),
            ["from_x", "from_y", "to_x", "to_y", "frequency"],
        )
        return [str(cell_path), str(route_path)]

    def _write_rows(self, path: Path, rows: list[dict], fieldnames: list[str]) -> None:
        with path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

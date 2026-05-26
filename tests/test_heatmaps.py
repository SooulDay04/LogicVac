import unittest
from tempfile import TemporaryDirectory

from evacsim.heatmaps.exports import HeatmapExporter
from evacsim.heatmaps.tracker import HeatmapTracker


class DummyAttributes:
    def __init__(self, evacuated: bool = False) -> None:
        self.evacuated = evacuated

    def is_evacuated(self) -> bool:
        return self.evacuated


class DummyAgent:
    def __init__(
        self,
        unique_id: int,
        pos: tuple[int, int] | None,
        history: list[tuple[int, int]],
        evacuated: bool = False,
    ) -> None:
        self.unique_id = unique_id
        self.pos = pos
        self.path_history = history
        self.attributes = DummyAttributes(evacuated)


class TestHeatmapTracker(unittest.TestCase):
    def test_records_cell_occupancy_and_cumulative_density(self) -> None:
        tracker = HeatmapTracker(grid_size=5)
        tracker.record_step([DummyAgent(1, (2, 2), [(2, 2)])])
        tracker.record_step([DummyAgent(1, (2, 2), [(2, 2)])])

        self.assertEqual(tracker.occupancy_counts[2, 2], 2)
        self.assertGreater(tracker.cumulative_density[2, 2], 0)
        self.assertEqual(tracker.steps_recorded, 2)

    def test_records_route_frequency_once_per_new_segment(self) -> None:
        tracker = HeatmapTracker(grid_size=5)
        agent = DummyAgent(1, (0, 0), [(0, 0)])
        tracker.record_step([agent])

        agent.path_history = [(0, 0), (1, 0)]
        agent.pos = (1, 0)
        tracker.record_step([agent])
        tracker.record_step([agent])

        self.assertEqual(tracker.route_frequency[((0, 0), (1, 0))], 1)

    def test_congestion_zones_are_sorted_by_density(self) -> None:
        tracker = HeatmapTracker(grid_size=5)
        tracker.record_step([DummyAgent(1, (1, 1), [(1, 1)])])
        tracker.record_step([DummyAgent(1, (3, 3), [(1, 1), (3, 3)])])
        tracker.record_step([DummyAgent(1, (3, 3), [(1, 1), (3, 3)])])

        zones = tracker.congestion_zones(limit=2)

        self.assertEqual(len(zones), 2)
        self.assertGreaterEqual(
            zones[0]["cumulative_density"],
            zones[1]["cumulative_density"],
        )

    def test_exports_image_and_csv_files(self) -> None:
        tracker = HeatmapTracker(grid_size=5)
        agent = DummyAgent(1, (1, 1), [(1, 1), (2, 1)])
        tracker.record_step([agent])
        tracker.record_step([agent])

        with TemporaryDirectory() as directory:
            exporter = HeatmapExporter(directory)
            image_path = exporter.export_image(tracker, "heatmap.png")
            csv_paths = exporter.export_csv(tracker, "heatmap")

            self.assertTrue(image_path.endswith("heatmap.png"))
            for path in [image_path, *csv_paths]:
                with open(path, "rb") as file:
                    self.assertGreater(len(file.read()), 0)


if __name__ == "__main__":
    unittest.main()

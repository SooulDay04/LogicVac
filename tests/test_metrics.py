import unittest

from evacsim.metrics.calculator import MetricsCalculator
from evacsim.metrics.collector import MetricsCollector


class TestMetrics(unittest.TestCase):
    def setUp(self) -> None:
        self.sample_data = [
            {
                "step": 0,
                "total_agents": 25,
                "evacuated": 0,
                "moving": 25,
                "blocked": 0,
                "panic": 0,
                "avg_stress": 0.0,
                "evacuation_rate": 0.0,
            },
            {
                "step": 10,
                "total_agents": 25,
                "evacuated": 10,
                "moving": 15,
                "blocked": 0,
                "panic": 0,
                "avg_stress": 15.0,
                "evacuation_rate": 0.4,
            },
            {
                "step": 20,
                "total_agents": 25,
                "evacuated": 25,
                "moving": 0,
                "blocked": 0,
                "panic": 0,
                "avg_stress": 10.0,
                "evacuation_rate": 1.0,
            },
        ]

    def test_calculate_mean(self) -> None:
        result = MetricsCalculator.calculate_mean([1.0, 2.0, 3.0])
        self.assertAlmostEqual(result, 2.0)

    def test_calculate_mean_empty(self) -> None:
        result = MetricsCalculator.calculate_mean([])
        self.assertEqual(result, 0.0)

    def test_calculate_std_dev(self) -> None:
        result = MetricsCalculator.calculate_std_dev([2.0, 4.0, 4.0, 4.0, 5.0, 5.0, 7.0, 9.0])
        self.assertAlmostEqual(result, 2.0, places=0)

    def test_total_evacuation_time(self) -> None:
        result = MetricsCalculator.calculate_total_evacuation_time(
            self.sample_data
        )
        self.assertEqual(result, 20)

    def test_max_stress(self) -> None:
        result = MetricsCalculator.calculate_max_stress(self.sample_data)
        self.assertEqual(result, 15.0)

    def test_summarize(self) -> None:
        summary = MetricsCalculator.summarize(self.sample_data)
        self.assertIn("total_steps", summary)
        self.assertIn("mean_stress", summary)
        self.assertIn("throughput", summary)

    def test_collector_data(self) -> None:
        collector = MetricsCollector()
        self.assertEqual(len(collector.get_data()), 0)
        collector.clear()
        self.assertEqual(len(collector.get_data()), 0)


if __name__ == "__main__":
    unittest.main()

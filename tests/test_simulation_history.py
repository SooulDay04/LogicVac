import unittest

from evacsim.ui.simulation_controller import SimulationController


class TestSimulationHistory(unittest.TestCase):
    def test_captures_initial_and_step_snapshots(self) -> None:
        controller = SimulationController()
        model = controller.create_model("scenario_1", agent_count=5)

        self.assertEqual(model.simulation_history.latest_tick, 0)
        initial = model.simulation_history.get(0)
        self.assertIsNotNone(initial)
        self.assertEqual(initial["tick"], 0)
        self.assertEqual(len(initial["agents"]), 5)
        self.assertIn("cumulative_density", initial["heatmap"])

        model.step()

        step = model.simulation_history.get(1)
        self.assertIsNotNone(step)
        self.assertEqual(step["tick"], 1)
        self.assertEqual(len(step["agents"]), 5)
        self.assertIn("series", step["metrics"])
        self.assertGreaterEqual(len(step["metrics"]["series"]), 1)


if __name__ == "__main__":
    unittest.main()

import unittest

from evacsim.engine.scenario_loader import ScenarioLoader


class TestScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.loader = ScenarioLoader()

    def test_list_scenarios(self) -> None:
        scenarios = self.loader.list_scenarios()
        self.assertEqual(len(scenarios), 6)
        self.assertIn("scenario_1", scenarios)
        self.assertIn("scenario_5", scenarios)
        self.assertIn("scenario_6", scenarios)

    def test_load_scenario_1(self) -> None:
        config = self.loader.load_scenario("scenario_1")
        self.assertEqual(config["num_agents"], 25)
        self.assertEqual(config["num_exits"], 1)
        self.assertFalse(config["has_obstacles"])

    def test_load_scenario_2(self) -> None:
        config = self.loader.load_scenario("scenario_2")
        self.assertEqual(config["num_agents"], 50)
        self.assertEqual(config["num_exits"], 2)
        self.assertTrue(config["has_obstacles"])

    def test_load_scenario_3(self) -> None:
        config = self.loader.load_scenario("scenario_3")
        self.assertEqual(config["num_agents"], 100)

    def test_load_scenario_4(self) -> None:
        config = self.loader.load_scenario("scenario_4")
        self.assertTrue(config.get("speed_variation", False))

    def test_load_scenario_5(self) -> None:
        config = self.loader.load_scenario("scenario_5")
        self.assertTrue(config["social_behavior"])

    def test_load_scenario_6(self) -> None:
        config = self.loader.load_scenario("scenario_6")
        self.assertEqual(config["num_exits"], 4)
        self.assertEqual(len(config["layout"]), 30)
        self.assertTrue(all(len(row) == 30 for row in config["layout"]))

    def test_load_unknown_scenario(self) -> None:
        config = self.loader.load_scenario("unknown")
        self.assertIn("num_agents", config)


if __name__ == "__main__":
    unittest.main()

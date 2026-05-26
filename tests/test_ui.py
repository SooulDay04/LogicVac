import unittest

from evacsim.ui.app import _should_advance_simulation


class TestUiSimulationClock(unittest.TestCase):
    def test_controls_do_not_advance_simulation_while_paused(self) -> None:
        self.assertFalse(
            _should_advance_simulation(
                ["trajectory-toggle.value"],
                n_intervals=3,
                is_running=False,
            )
        )

    def test_mixed_control_and_clock_events_do_not_advance(self) -> None:
        self.assertFalse(
            _should_advance_simulation(
                ["trajectory-toggle.value", "simulation-clock.n_intervals"],
                n_intervals=3,
                is_running=True,
            )
        )

    def test_clock_advances_only_when_running(self) -> None:
        self.assertTrue(
            _should_advance_simulation(
                ["simulation-clock.n_intervals"],
                n_intervals=3,
                is_running=True,
            )
        )


if __name__ == "__main__":
    unittest.main()

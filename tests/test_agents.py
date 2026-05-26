import unittest

from evacsim.agents.attributes import AgentAttributes
from evacsim.agents.personality import PERSONALITY_PROFILES, PersonalityType
from evacsim.agents.states import AgentState


class TestAgents(unittest.TestCase):
    def test_agent_attributes_creation(self) -> None:
        attrs = AgentAttributes(1, speed=1.5)
        self.assertEqual(attrs.agent_id, 1)
        self.assertEqual(attrs.speed, 1.5)
        self.assertEqual(attrs.personality, PersonalityType.NORMAL)
        self.assertEqual(attrs.stress, 0.0)
        self.assertEqual(attrs.state, AgentState.IDLE)

    def test_personality_changes_speed(self) -> None:
        attrs = AgentAttributes(1, speed=1.0, personality=PersonalityType.ANSIOSO)
        profile = PERSONALITY_PROFILES[PersonalityType.ANSIOSO]
        self.assertEqual(attrs.speed, profile.speed_multiplier)

    def test_all_personalities_have_behavior_modifiers(self) -> None:
        self.assertEqual(len(PERSONALITY_PROFILES), 5)
        for personality in PersonalityType:
            profile = PERSONALITY_PROFILES[personality]
            self.assertGreater(profile.speed_multiplier, 0)
            self.assertGreaterEqual(profile.follow_tendency, 0)
            self.assertLessEqual(profile.follow_tendency, 1)
            self.assertGreaterEqual(profile.route_change_probability, 0)
            self.assertLessEqual(profile.route_change_probability, 1)
            self.assertGreaterEqual(profile.min_distance, 0)
            self.assertGreaterEqual(profile.push_tendency, 0)
            self.assertLessEqual(profile.push_tendency, 1)

    def test_ansioso_can_push_and_lider_can_yield(self) -> None:
        anxious = PERSONALITY_PROFILES[PersonalityType.ANSIOSO]
        leader = PERSONALITY_PROFILES[PersonalityType.LIDER]
        self.assertGreater(anxious.push_tendency, 0)
        self.assertTrue(leader.yield_near_exit)

    def test_stress_increase(self) -> None:
        attrs = AgentAttributes(1)
        attrs.increase_stress(30.0)
        self.assertEqual(attrs.stress, 30.0)

    def test_stress_decrease(self) -> None:
        attrs = AgentAttributes(1)
        attrs.increase_stress(50.0)
        attrs.decrease_stress(20.0)
        self.assertEqual(attrs.stress, 30.0)

    def test_stress_max_cap(self) -> None:
        attrs = AgentAttributes(1)
        attrs.increase_stress(200.0)
        self.assertEqual(attrs.stress, 100.0)

    def test_stress_min_floor(self) -> None:
        attrs = AgentAttributes(1)
        attrs.decrease_stress(50.0)
        self.assertEqual(attrs.stress, 0.0)

    def test_state_change(self) -> None:
        attrs = AgentAttributes(1)
        attrs.set_state(AgentState.MOVING)
        self.assertEqual(attrs.state, AgentState.MOVING)

    def test_is_panic(self) -> None:
        attrs = AgentAttributes(1)
        attrs.set_state(AgentState.PANIC)
        self.assertTrue(attrs.is_panic())
        attrs.set_state(AgentState.IDLE)
        self.assertFalse(attrs.is_panic())

    def test_is_evacuated(self) -> None:
        attrs = AgentAttributes(1)
        attrs.set_state(AgentState.EVACUATED)
        self.assertTrue(attrs.is_evacuated())
        attrs.set_state(AgentState.MOVING)
        self.assertFalse(attrs.is_evacuated())


if __name__ == "__main__":
    unittest.main()

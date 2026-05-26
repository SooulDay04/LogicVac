from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class PersonalityType(Enum):
    CALMADO = "calmado"
    NORMAL = "normal"
    ANSIOSO = "ansioso"
    LIDER = "lider"
    SEGUIDOR = "seguidor"


@dataclass(frozen=True)
class PersonalityProfile:
    speed_multiplier: float
    congestion_stress_multiplier: float
    blocked_step_threshold: int
    follow_tendency: float
    route_change_probability: float
    min_distance: int
    push_tendency: float
    yield_near_exit: bool
    color: str
    label: str


PERSONALITY_PROFILES = {
    PersonalityType.CALMADO: PersonalityProfile(
        speed_multiplier=0.85,
        congestion_stress_multiplier=0.6,
        blocked_step_threshold=5,
        follow_tendency=0.35,
        route_change_probability=0.08,
        min_distance=1,
        push_tendency=0.0,
        yield_near_exit=False,
        color="#0f766e",
        label="Calmado",
    ),
    PersonalityType.NORMAL: PersonalityProfile(
        speed_multiplier=1.0,
        congestion_stress_multiplier=1.0,
        blocked_step_threshold=3,
        follow_tendency=0.4,
        route_change_probability=0.18,
        min_distance=0,
        push_tendency=0.0,
        yield_near_exit=False,
        color="#2563eb",
        label="Normal",
    ),
    PersonalityType.ANSIOSO: PersonalityProfile(
        speed_multiplier=1.35,
        congestion_stress_multiplier=1.6,
        blocked_step_threshold=1,
        follow_tendency=0.15,
        route_change_probability=0.55,
        min_distance=0,
        push_tendency=0.8,
        yield_near_exit=False,
        color="#dc2626",
        label="Ansioso",
    ),
    PersonalityType.LIDER: PersonalityProfile(
        speed_multiplier=1.25,
        congestion_stress_multiplier=0.8,
        blocked_step_threshold=2,
        follow_tendency=0.05,
        route_change_probability=0.35,
        min_distance=1,
        push_tendency=0.05,
        yield_near_exit=True,
        color="#ca8a04",
        label="Lider",
    ),
    PersonalityType.SEGUIDOR: PersonalityProfile(
        speed_multiplier=0.95,
        congestion_stress_multiplier=1.1,
        blocked_step_threshold=4,
        follow_tendency=0.95,
        route_change_probability=0.12,
        min_distance=0,
        push_tendency=0.0,
        yield_near_exit=False,
        color="#7c3aed",
        label="Seguidor",
    ),
}


def normalize_personality(value: PersonalityType | str | None) -> PersonalityType:
    if isinstance(value, PersonalityType):
        return value
    if value is None:
        return PersonalityType.NORMAL

    normalized = value.lower().replace("í", "i")
    for personality in PersonalityType:
        if personality.value == normalized:
            return personality
    return PersonalityType.NORMAL

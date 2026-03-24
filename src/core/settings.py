from dataclasses import dataclass


@dataclass(frozen=True)
class LiftSettings:
    name: str
    abbreviation: str
    bodyweight_coefficient: float
    rounding_increment: float
    one_rep_max: float
    training_max_factor: float


@dataclass(frozen=True)
class ProgramWeekSettings:
    name: str
    scaling_factors: list[float]
    reps_per_set: list[int]


@dataclass(frozen=True)
class AppSettings:
    bodyweight: float
    zero_weight_strictness: float
    competition_attempt_factors: list[float]
    lifts: list[LiftSettings]
    program_weeks: list[ProgramWeekSettings]

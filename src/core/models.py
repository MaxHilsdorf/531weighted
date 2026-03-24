from dataclasses import dataclass
from enum import Enum
from math import floor


class ProgramWeek(Enum):
    FIVE: str = "5"
    THREE: str = "3"
    ONE: str = "1"
    DELOAD: str = "deload"


@dataclass(frozen=True)
class Lift:
    name: str
    abbreviation: str
    bodyweight_coefficient: float
    rounding_increment: float

    def bodyweight_offset(self, bodyweight: float) -> float:
        return bodyweight * self.bodyweight_coefficient

    @property
    def depends_on_bodyweight(self) -> bool:
        return self.bodyweight_coefficient > 0

    @property
    def smallest_increment(self) -> float:
        return self.rounding_increment

    def round_weight(self, weight: float) -> float:
        increment = self.smallest_increment
        return round(floor((weight / increment) + 0.5) * increment, 2)


@dataclass
class LiftContext:
    lift: Lift
    one_rep_max: float


@dataclass
class LiftPerformance:
    lift: Lift
    weight: float
    reps: int


@dataclass
class CompetitionAttempt:
    lift: Lift
    attempt_number: int
    weight: float


@dataclass
class LiftProgramContext:
    lift_context: LiftContext
    training_max_factor: float


@dataclass
class ProgramWeekContext:
    program_week: ProgramWeek
    scaling_factors: list[float]
    reps_per_set: list[int]


@dataclass
class LiftSummary:
    lift_context: LiftContext
    training_max: float


@dataclass
class LiftPlan:
    lift_context: LiftContext
    performances: list[LiftPerformance]


@dataclass
class ProgramWeekPlan:
    program_week: ProgramWeek
    lift_plans: list[LiftPlan]


@dataclass
class CompetitionAttemptPlan:
    lift_context: LiftContext
    attempts: list[CompetitionAttempt]

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

    def bodyweight_offset(self, bodyweight: float) -> float:
        return bodyweight * self.bodyweight_coefficient

    @property
    def depends_on_bodyweight(self) -> bool:
        return self.bodyweight_coefficient > 0

    @property
    def smallest_increment(self) -> float:
        return 1.25 if self.depends_on_bodyweight else 2.5

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
class LiftProgramContext:
    lift_context: LiftContext
    training_max_factor: float

@dataclass
class ProgramWeekContext:
    program_week: ProgramWeek
    scaling_factors: list[float]
    reps_per_set: list[int]


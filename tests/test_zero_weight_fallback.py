from core.calculators import StrengthCalculator
from core.models import Lift, LiftContext, LiftProgramContext


def test_zero_weight_reps_are_never_below_one() -> None:
    lift = Lift(
        name="Muscle Up",
        abbreviation="MU",
        bodyweight_coefficient=1.0,
        rounding_increment=1.25,
    )
    lift_context = LiftContext(lift=lift, one_rep_max=10)
    calculator = StrengthCalculator(
        lift_program_contexts={
            lift: LiftProgramContext(
                lift_context=lift_context, training_max_factor=0.87
            )
        },
        bodyweight=74,
        zero_weight_strictness=1.0,
    )

    assert calculator.get_zero_weight_reps(lift, raw_weight=-30, target_reps=5) == 1


def test_zero_weight_strictness_softens_rep_reduction() -> None:
    lift = Lift(
        name="Muscle Up",
        abbreviation="MU",
        bodyweight_coefficient=0.85,
        rounding_increment=1.25,
    )
    lift_context = LiftContext(lift=lift, one_rep_max=15)
    strict_calculator = StrengthCalculator(
        lift_program_contexts={
            lift: LiftProgramContext(
                lift_context=lift_context, training_max_factor=0.87
            )
        },
        bodyweight=74,
        zero_weight_strictness=1.0,
    )
    soft_calculator = StrengthCalculator(
        lift_program_contexts={
            lift: LiftProgramContext(
                lift_context=lift_context, training_max_factor=0.87
            )
        },
        bodyweight=74,
        zero_weight_strictness=0.3,
    )

    strict_reps = strict_calculator.get_zero_weight_reps(
        lift, raw_weight=-12, target_reps=5
    )
    soft_reps = soft_calculator.get_zero_weight_reps(
        lift, raw_weight=-12, target_reps=5
    )

    assert soft_reps >= strict_reps

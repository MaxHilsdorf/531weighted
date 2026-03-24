from core.calculators import StrengthCalculator
from core.models import Lift, LiftContext, LiftProgramContext


def test_training_max_uses_bodyweight_coefficient() -> None:
    lift = Lift(
        name="Pull Up",
        abbreviation="PU",
        bodyweight_coefficient=0.95,
        rounding_increment=1.25,
    )
    lift_context = LiftContext(lift=lift, one_rep_max=60)
    calculator = StrengthCalculator(
        lift_program_contexts={
            lift: LiftProgramContext(
                lift_context=lift_context, training_max_factor=0.87
            )
        },
        bodyweight=74,
    )

    assert round(calculator.get_training_max(lift_context), 3) == 43.061


def test_training_max_for_standard_lift_matches_percentage() -> None:
    lift = Lift(
        name="Squat",
        abbreviation="SQ",
        bodyweight_coefficient=0.0,
        rounding_increment=2.5,
    )
    lift_context = LiftContext(lift=lift, one_rep_max=140)
    calculator = StrengthCalculator(
        lift_program_contexts={
            lift: LiftProgramContext(lift_context=lift_context, training_max_factor=0.9)
        },
        bodyweight=74,
    )

    assert calculator.get_training_max(lift_context) == 126


def test_scaled_weight_preserves_negative_values_when_floor_is_disabled() -> None:
    lift = Lift(
        name="Muscle Up",
        abbreviation="MU",
        bodyweight_coefficient=1.0,
        rounding_increment=1.25,
    )
    calculator = StrengthCalculator(lift_program_contexts={}, bodyweight=74)

    assert (
        calculator.get_scaled_weight(
            lift=lift, base_weight=4.0, factor=0.65, apply_floor=False
        )
        < 0
    )
    assert (
        calculator.get_scaled_weight(
            lift=lift, base_weight=4.0, factor=0.65, apply_floor=True
        )
        == 0.0
    )

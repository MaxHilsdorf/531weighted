from core.models import Lift


def test_bodyweight_lift_rounds_to_nearest_1_25kg() -> None:
    lift = Lift(
        name="Pull Up",
        abbreviation="PU",
        bodyweight_coefficient=1.0,
        rounding_increment=1.25,
    )

    assert lift.round_weight(13.6) == 13.75


def test_non_bodyweight_lift_rounds_to_nearest_2_5kg() -> None:
    lift = Lift(
        name="Squat",
        abbreviation="SQ",
        bodyweight_coefficient=0.25,
        rounding_increment=2.5,
    )

    assert lift.round_weight(101.2) == 100.0


def test_partial_bodyweight_lift_can_still_round_to_nearest_2_5kg() -> None:
    lift = Lift(
        name="Squat",
        abbreviation="SQ",
        bodyweight_coefficient=0.25,
        rounding_increment=2.5,
    )

    assert lift.round_weight(23.75) == 25.0

from core.models import Lift, LiftContext, LiftProgramContext
from core.planners import CompetitionAttemptPlanner
from core.report_formatters import format_attempt_report


def test_attempt_report_uses_attempt_factors_and_rounding() -> None:
    squat = Lift(
        name="Squat",
        abbreviation="SQ",
        bodyweight_coefficient=0.0,
        rounding_increment=2.5,
    )
    squat_context = LiftContext(lift=squat, one_rep_max=140)
    planner = CompetitionAttemptPlanner(
        lift_program_contexts={
            squat: LiftProgramContext(
                lift_context=squat_context, training_max_factor=0.9
            )
        },
        bodyweight=74,
        attempt_factors=[0.87, 0.95, 1.0],
    )

    report = format_attempt_report(planner)

    assert "1st 122.5kg" in report
    assert "2nd 132.5kg" in report
    assert "3rd 140kg" in report


def test_attempt_planner_uses_bodyweight_adjusted_math_for_bodyweight_lifts() -> None:
    pull_up = Lift(
        name="Pull Up",
        abbreviation="PU",
        bodyweight_coefficient=0.95,
        rounding_increment=1.25,
    )
    pull_up_context = LiftContext(lift=pull_up, one_rep_max=60)
    planner = CompetitionAttemptPlanner(
        lift_program_contexts={
            pull_up: LiftProgramContext(
                lift_context=pull_up_context, training_max_factor=0.87
            )
        },
        bodyweight=74,
        attempt_factors=[0.87, 0.95, 1.0],
    )

    attempt_plan = planner.get_attempt_plans()[0]

    assert [attempt.weight for attempt in attempt_plan.attempts] == [42.5, 53.75, 60.0]

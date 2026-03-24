from core.models import (
    Lift,
    LiftContext,
    LiftProgramContext,
    ProgramWeek,
    ProgramWeekContext,
)
from core.planners import FiveThreeOneProgram
from core.report_formatters import format_program_report


def test_program_report_contains_week_sections_in_order() -> None:
    squat = Lift(
        name="Squat",
        abbreviation="SQ",
        bodyweight_coefficient=0.0,
        rounding_increment=2.5,
    )
    squat_context = LiftContext(lift=squat, one_rep_max=140)
    planner = FiveThreeOneProgram(
        lift_program_contexts={
            squat: LiftProgramContext(
                lift_context=squat_context, training_max_factor=0.9
            )
        },
        program_week_contexts={
            ProgramWeek.FIVE: ProgramWeekContext(
                ProgramWeek.FIVE, [0.65, 0.75, 0.85], [5, 5, 5]
            ),
            ProgramWeek.THREE: ProgramWeekContext(
                ProgramWeek.THREE, [0.7, 0.8, 0.9], [3, 3, 3]
            ),
            ProgramWeek.ONE: ProgramWeekContext(
                ProgramWeek.ONE, [0.75, 0.85, 0.95], [5, 3, 1]
            ),
        },
        bodyweight=74,
    )

    report = format_program_report(planner)

    assert "Lift Overview" in report
    assert report.index("Week 5") < report.index("Week 3") < report.index("Week 1")

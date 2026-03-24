from pathlib import Path

from core.config_loader import (
    build_attempt_factors,
    build_lift_program_contexts,
    build_program_week_contexts,
    load_settings,
)
from core.planners import CompetitionAttemptPlanner, FiveThreeOneProgram
from core.report_formatters import format_attempt_report, format_program_report


def main() -> None:
    config_path = Path(__file__).resolve().parent.parent.parent / "config.yaml"
    settings = load_settings(config_path)

    lift_program_contexts = build_lift_program_contexts(settings.lifts)
    program_week_contexts = build_program_week_contexts(settings.program_weeks)
    attempt_factors = build_attempt_factors(settings.competition_attempt_factors)
    zero_weight_strictness = settings.zero_weight_strictness
    bodyweight = settings.bodyweight

    attempt_planner = CompetitionAttemptPlanner(
        lift_program_contexts=lift_program_contexts,
        bodyweight=bodyweight,
        attempt_factors=attempt_factors,
        zero_weight_strictness=zero_weight_strictness,
    )
    program = FiveThreeOneProgram(
        lift_program_contexts=lift_program_contexts,
        program_week_contexts=program_week_contexts,
        bodyweight=bodyweight,
        zero_weight_strictness=zero_weight_strictness,
    )

    print(format_attempt_report(attempt_planner))
    print()
    print(format_program_report(program))


if __name__ == "__main__":
    main()

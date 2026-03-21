from pathlib import Path

from config import load_config
from models import Lift, LiftContext, LiftProgramContext, ProgramWeek, ProgramWeekContext
from programming import FiveThreeOneProgram


def main() -> None:
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    config = load_config(config_path)

    lift_program_contexts = _build_lift_program_contexts(config["lifts"])
    program_week_contexts = _build_program_week_contexts(config["program_weeks"])

    program = FiveThreeOneProgram(
        lift_program_contexts=lift_program_contexts,
        program_week_contexts=program_week_contexts,
        bodyweight=float(config["bodyweight"]),
    )

    print(program.generate_program_report())


def _build_lift_program_contexts(lifts_config: list[dict]) -> dict[Lift, LiftProgramContext]:
    lift_program_contexts: dict[Lift, LiftProgramContext] = {}

    for lift_config in lifts_config:
        lift = Lift(
            name=lift_config["name"],
            abbreviation=lift_config["abbreviation"],
            is_bodyweight=lift_config["is_bodyweight"],
        )
        lift_context = LiftContext(
            lift=lift,
            one_rep_max=float(lift_config["one_rep_max"]),
        )
        lift_program_contexts[lift] = LiftProgramContext(
            lift_context=lift_context,
            training_max_factor=float(lift_config["training_max_factor"]),
        )

    return lift_program_contexts


def _build_program_week_contexts(program_weeks_config: list[dict]) -> dict[ProgramWeek, ProgramWeekContext]:
    program_week_contexts: dict[ProgramWeek, ProgramWeekContext] = {}

    for week_config in program_weeks_config:
        week_name, week_values = next(iter(week_config.items()))
        week_settings = _flatten_week_settings(week_values)
        program_week = ProgramWeek(week_name)

        program_week_contexts[program_week] = ProgramWeekContext(
            program_week=program_week,
            scaling_factors=[float(value) for value in week_settings["scaling_factors"]],
            reps_per_set=[int(value) for value in week_settings["reps_per_set"]],
        )

    return program_week_contexts


def _flatten_week_settings(week_values: list[dict]) -> dict:
    flattened_settings = {}

    for item in week_values:
        flattened_settings.update(item)

    return flattened_settings


if __name__ == "__main__":
    main()

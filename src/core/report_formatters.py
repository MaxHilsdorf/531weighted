from __future__ import annotations

from typing import TYPE_CHECKING

from .models import LiftSummary

if TYPE_CHECKING:
    from .planners import CompetitionAttemptPlanner, FiveThreeOneProgram


def format_weight(weight: float) -> str:
    return f"{weight:.2f}".rstrip("0").rstrip(".")


def format_program_report(program: FiveThreeOneProgram) -> str:
    report_lines = ["5/3/1 Program", "============="]
    report_lines.extend(["", "Lift Overview"])

    for lift_summary in program.get_lift_summaries():
        report_lines.append(_format_lift_summary(lift_summary))

    for week_plan in program.get_program_week_plans():
        report_lines.extend(["", f"Week {week_plan.program_week.value}"])
        for lift_plan in week_plan.lift_plans:
            performance_summary = ", ".join(
                f"{format_weight(performance.weight)}kg*{performance.reps}"
                for performance in lift_plan.performances
            )
            report_lines.append(
                f"  {lift_plan.lift_context.lift.name}: {performance_summary}"
            )

    return "\n".join(report_lines)


def format_attempt_report(planner: CompetitionAttemptPlanner) -> str:
    report_lines = ["Competition Attempts", "===================="]

    for attempt_plan in planner.get_attempt_plans():
        attempts_summary = ", ".join(
            f"{_format_attempt_label(attempt.attempt_number)} {format_weight(attempt.weight)}kg"
            for attempt in attempt_plan.attempts
        )
        report_lines.append(
            f"  {attempt_plan.lift_context.lift.name}: {attempts_summary}"
        )

    return "\n".join(report_lines)


def _format_lift_summary(lift_summary: LiftSummary) -> str:
    return (
        f"  {lift_summary.lift_context.lift.name}: "
        f"1RM {format_weight(lift_summary.lift_context.one_rep_max)}kg, "
        f"TM {format_weight(lift_summary.training_max)}kg"
    )


def _format_attempt_label(attempt_number: int) -> str:
    if attempt_number == 1:
        return "1st"
    if attempt_number == 2:
        return "2nd"
    if attempt_number == 3:
        return "3rd"

    return f"{attempt_number}th"

from dataclasses import dataclass

import streamlit as st

from core.config_loader import (
    build_attempt_factors,
    build_lift_program_contexts,
    build_program_week_contexts,
)
from core.models import CompetitionAttemptPlan, LiftSummary, ProgramWeekPlan
from core.planners import CompetitionAttemptPlanner, FiveThreeOneProgram
from core.report_formatters import (
    format_attempt_report,
    format_program_report,
    format_weight,
)
from core.settings import AppSettings


@dataclass(frozen=True)
class TableSection:
    title: str
    rows: list[dict[str, str]]
    raw_text: str


@dataclass(frozen=True)
class ProgramSection:
    overview_rows: list[dict[str, str]]
    week_sections: list[TableSection]
    raw_text: str


@dataclass(frozen=True)
class GeneratedOutput:
    attempt_section: TableSection
    program_section: ProgramSection


def build_output(settings: AppSettings) -> GeneratedOutput:
    lift_program_contexts = build_lift_program_contexts(settings.lifts)
    program_week_contexts = build_program_week_contexts(settings.program_weeks)
    attempt_factors = build_attempt_factors(settings.competition_attempt_factors)

    attempt_planner = CompetitionAttemptPlanner(
        lift_program_contexts=lift_program_contexts,
        bodyweight=settings.bodyweight,
        attempt_factors=attempt_factors,
        zero_weight_strictness=settings.zero_weight_strictness,
    )
    program = FiveThreeOneProgram(
        lift_program_contexts=lift_program_contexts,
        program_week_contexts=program_week_contexts,
        bodyweight=settings.bodyweight,
        zero_weight_strictness=settings.zero_weight_strictness,
    )

    return GeneratedOutput(
        attempt_section=TableSection(
            title="Competition Attempts",
            rows=_build_attempt_rows(attempt_planner.get_attempt_plans()),
            raw_text=format_attempt_report(attempt_planner),
        ),
        program_section=ProgramSection(
            overview_rows=_build_lift_summary_rows(program.get_lift_summaries()),
            week_sections=_build_week_sections(program.get_program_week_plans()),
            raw_text=format_program_report(program),
        ),
    )


def render_output(output: GeneratedOutput, selected_section: str) -> None:
    if selected_section == "attempts":
        _render_attempt_section(output.attempt_section)
        return

    _render_program_section(output.program_section)


@st.dialog("Raw Text")
def _show_raw_text_dialog(title: str, raw_text: str) -> None:
    st.caption(title)
    st.code(raw_text, language="text", height=420)


def _render_attempt_section(section: TableSection) -> None:
    st.subheader(section.title)
    st.table(_to_columnar_table(section.rows))
    _render_raw_text_button(
        label="Open Raw Text",
        button_key="attempts-raw-text",
        dialog_title=section.title,
        raw_text=section.raw_text,
    )


def _render_program_section(section: ProgramSection) -> None:
    st.subheader("5/3/1 Program")
    st.caption("This is the 4-week progression of the 5/3/1 cycle.")
    st.caption("Lift Overview")
    st.table(_to_columnar_table(section.overview_rows))

    for week_section in section.week_sections:
        st.caption(week_section.title)
        st.table(_to_columnar_table(week_section.rows))

    _render_raw_text_button(
        label="Open Raw Text",
        button_key="program-raw-text",
        dialog_title="5/3/1 Program",
        raw_text=section.raw_text,
    )


def _render_raw_text_button(
    label: str,
    button_key: str,
    dialog_title: str,
    raw_text: str,
) -> None:
    raw_text_button_column, _ = st.columns([0.28, 0.72])
    if raw_text_button_column.button(
        label,
        key=button_key,
        use_container_width=True,
    ):
        _show_raw_text_dialog(dialog_title, raw_text)


def _build_attempt_rows(
    attempt_plans: list[CompetitionAttemptPlan],
) -> list[dict[str, str]]:
    return [
        {
            "Lift": attempt_plan.lift_context.lift.name,
            **{
                _format_attempt_label(
                    attempt.attempt_number
                ): f"{format_weight(attempt.weight)}kg"
                for attempt in attempt_plan.attempts
            },
        }
        for attempt_plan in attempt_plans
    ]


def _build_lift_summary_rows(
    lift_summaries: list[LiftSummary],
) -> list[dict[str, str]]:
    return [
        {
            "Lift": lift_summary.lift_context.lift.name,
            "1RM": f"{format_weight(lift_summary.lift_context.one_rep_max)}kg",
            "TM": f"{format_weight(lift_summary.training_max)}kg",
        }
        for lift_summary in lift_summaries
    ]


def _build_week_sections(week_plans: list[ProgramWeekPlan]) -> list[TableSection]:
    week_sections = []

    for week_plan in week_plans:
        rows = []
        for lift_plan in week_plan.lift_plans:
            rows.append(
                {
                    "Lift": lift_plan.lift_context.lift.name,
                    **{
                        f"Set {index}": f"{format_weight(performance.weight)}kg x {performance.reps}"
                        for index, performance in enumerate(
                            lift_plan.performances,
                            start=1,
                        )
                    },
                }
            )

        week_sections.append(
            TableSection(
                title=_format_program_phase_title(week_plan.program_week.value),
                rows=rows,
                raw_text="",
            )
        )

    return week_sections


def _to_columnar_table(rows: list[dict[str, str]]) -> dict[str, list[str]]:
    if not rows:
        return {}

    return {column: [row[column] for row in rows] for column in rows[0]}


def _format_attempt_label(attempt_number: int) -> str:
    if attempt_number == 1:
        return "1st"
    if attempt_number == 2:
        return "2nd"
    if attempt_number == 3:
        return "3rd"

    return f"{attempt_number}th"


def _format_program_phase_title(program_week_name: str) -> str:
    if program_week_name == "5":
        return "Week 1: 5s"
    if program_week_name == "3":
        return "Week 2: 3s"
    if program_week_name == "1":
        return "Week 3: 5/3/1"
    if program_week_name == "deload":
        return "Week 4: Deload"

    return f"Cycle Week: {program_week_name}"

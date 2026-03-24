from pathlib import Path


_SOURCE_CORE_PATH = Path(__file__).resolve().parent.parent / "src" / "core"
__path__ = [str(_SOURCE_CORE_PATH)]

from .calculators import StrengthCalculator
from .config_loader import (
    build_attempt_factors,
    build_lift_program_contexts,
    build_program_week_contexts,
    build_settings,
    load_config,
    load_settings,
    merge_config_overrides,
)
from .defaults import get_default_settings
from .models import (
    CompetitionAttempt,
    CompetitionAttemptPlan,
    Lift,
    LiftContext,
    LiftPerformance,
    LiftPlan,
    LiftProgramContext,
    LiftSummary,
    ProgramWeek,
    ProgramWeekContext,
    ProgramWeekPlan,
)
from .planners import CompetitionAttemptPlanner, FiveThreeOneProgram
from .report_formatters import format_attempt_report, format_program_report
from .settings import AppSettings, LiftSettings, ProgramWeekSettings

__all__ = [
    "AppSettings",
    "CompetitionAttempt",
    "CompetitionAttemptPlan",
    "CompetitionAttemptPlanner",
    "FiveThreeOneProgram",
    "Lift",
    "LiftContext",
    "LiftPerformance",
    "LiftPlan",
    "LiftProgramContext",
    "LiftSettings",
    "LiftSummary",
    "ProgramWeek",
    "ProgramWeekContext",
    "ProgramWeekPlan",
    "ProgramWeekSettings",
    "StrengthCalculator",
    "build_attempt_factors",
    "build_lift_program_contexts",
    "build_program_week_contexts",
    "build_settings",
    "format_attempt_report",
    "format_program_report",
    "get_default_settings",
    "load_config",
    "load_settings",
    "merge_config_overrides",
]

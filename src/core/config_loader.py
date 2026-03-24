from pathlib import Path
from typing import Any

import yaml

from core.defaults import get_default_settings
from core.models import (
    Lift,
    LiftContext,
    LiftProgramContext,
    ProgramWeek,
    ProgramWeekContext,
)
from core.settings import AppSettings, LiftSettings, ProgramWeekSettings


def load_config(config_path: str | Path) -> dict[str, Any]:
    resolved_path = Path(config_path).expanduser().resolve()

    with resolved_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a top-level mapping")

    return config


def load_settings(config_path: str | Path) -> AppSettings:
    resolved_config_path = Path(config_path).expanduser().resolve()
    config_overrides = load_config(resolved_config_path)

    local_override_path = _resolve_local_override_path(resolved_config_path)
    if local_override_path.exists():
        local_overrides = load_config(local_override_path)
        config_overrides = merge_config_overrides(
            local_overrides,
            base_config=merge_config_overrides(config_overrides),
        )

    return build_settings(config_overrides)


def build_settings(config_overrides: dict[str, Any] | None = None) -> AppSettings:
    merged_config = merge_config_overrides(config_overrides or {})
    return AppSettings(
        bodyweight=float(merged_config["bodyweight"]),
        zero_weight_strictness=float(merged_config["zero_weight_strictness"]),
        competition_attempt_factors=[
            float(value) for value in merged_config["competition_attempt_factors"]
        ],
        lifts=[
            LiftSettings(
                name=lift_config["name"],
                abbreviation=lift_config["abbreviation"],
                bodyweight_coefficient=float(lift_config["bodyweight_coefficient"]),
                rounding_increment=_get_rounding_increment(lift_config),
                one_rep_max=float(lift_config["one_rep_max"]),
                training_max_factor=float(lift_config["training_max_factor"]),
            )
            for lift_config in merged_config["lifts"]
        ],
        program_weeks=[
            ProgramWeekSettings(
                name=week_config["name"],
                scaling_factors=[
                    float(value) for value in week_config["scaling_factors"]
                ],
                reps_per_set=[int(value) for value in week_config["reps_per_set"]],
            )
            for week_config in merged_config["program_weeks"]
        ],
    )


def merge_config_overrides(
    config_overrides: dict[str, Any],
    base_config: dict[str, Any] | None = None,
) -> dict[str, Any]:
    defaults = base_config or _settings_to_dict(get_default_settings())
    merged_config = {
        "bodyweight": float(config_overrides.get("bodyweight", defaults["bodyweight"])),
        "zero_weight_strictness": float(
            config_overrides.get(
                "zero_weight_strictness", defaults["zero_weight_strictness"]
            )
        ),
        "competition_attempt_factors": config_overrides.get(
            "competition_attempt_factors", defaults["competition_attempt_factors"]
        ),
        "lifts": _merge_lifts(defaults["lifts"], config_overrides.get("lifts", [])),
        "program_weeks": _merge_program_weeks(
            defaults["program_weeks"],
            config_overrides.get("program_weeks", []),
        ),
    }

    return merged_config


def build_lift_program_contexts(
    lifts_config: list[dict] | list[LiftSettings],
) -> dict[Lift, LiftProgramContext]:
    lift_program_contexts: dict[Lift, LiftProgramContext] = {}

    for lift_config in lifts_config:
        lift_data = _coerce_lift_config(lift_config)
        lift = Lift(
            name=lift_data["name"],
            abbreviation=lift_data["abbreviation"],
            bodyweight_coefficient=float(lift_data["bodyweight_coefficient"]),
            rounding_increment=_get_rounding_increment(lift_data),
        )
        lift_context = LiftContext(
            lift=lift, one_rep_max=float(lift_data["one_rep_max"])
        )
        lift_program_contexts[lift] = LiftProgramContext(
            lift_context=lift_context,
            training_max_factor=float(lift_data["training_max_factor"]),
        )

    return lift_program_contexts


def build_program_week_contexts(
    program_weeks_config: list[dict] | list[ProgramWeekSettings],
) -> dict[ProgramWeek, ProgramWeekContext]:
    program_week_contexts: dict[ProgramWeek, ProgramWeekContext] = {}

    for week_config in program_weeks_config:
        week_data = _coerce_program_week_config(week_config)
        program_week = ProgramWeek(week_data["name"])
        program_week_contexts[program_week] = ProgramWeekContext(
            program_week=program_week,
            scaling_factors=[float(value) for value in week_data["scaling_factors"]],
            reps_per_set=[int(value) for value in week_data["reps_per_set"]],
        )

    return program_week_contexts


def build_attempt_factors(attempt_factors_config: list[float]) -> list[float]:
    return [float(value) for value in attempt_factors_config]


def _settings_to_dict(settings: AppSettings) -> dict[str, Any]:
    return {
        "bodyweight": settings.bodyweight,
        "zero_weight_strictness": settings.zero_weight_strictness,
        "competition_attempt_factors": list(settings.competition_attempt_factors),
        "lifts": [
            {
                "name": lift.name,
                "abbreviation": lift.abbreviation,
                "bodyweight_coefficient": lift.bodyweight_coefficient,
                "rounding_increment": lift.rounding_increment,
                "one_rep_max": lift.one_rep_max,
                "training_max_factor": lift.training_max_factor,
            }
            for lift in settings.lifts
        ],
        "program_weeks": [
            {
                "name": week.name,
                "scaling_factors": list(week.scaling_factors),
                "reps_per_set": list(week.reps_per_set),
            }
            for week in settings.program_weeks
        ],
    }


def _merge_lifts(
    default_lifts: list[dict[str, Any]], override_lifts: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    merged_lifts: list[dict[str, Any]] = []
    remaining_override_lifts = [
        override_lift
        for override_lift in override_lifts
        if isinstance(override_lift, dict)
    ]

    for default_lift in default_lifts:
        override_lift = _pop_matching_lift_override(
            default_lift, remaining_override_lifts
        )
        merged_lifts.append({**default_lift, **override_lift})

    merged_identifiers = {
        identifier
        for lift in merged_lifts
        for identifier in _get_lift_identifiers(lift)
    }
    for override_lift in remaining_override_lifts:
        if not merged_identifiers.intersection(_get_lift_identifiers(override_lift)):
            merged_lifts.append(override_lift)

    return merged_lifts


def _merge_program_weeks(
    default_program_weeks: list[dict[str, Any]],
    override_program_weeks: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    merged_program_weeks: list[dict[str, Any]] = []
    coerced_override_program_weeks = [
        _coerce_program_week_config(week) for week in override_program_weeks
    ]
    overrides_by_name = {
        override_week["name"]: override_week
        for override_week in coerced_override_program_weeks
    }

    for default_program_week in default_program_weeks:
        override_program_week = overrides_by_name.pop(default_program_week["name"], {})
        merged_program_weeks.append({**default_program_week, **override_program_week})

    merged_program_weeks.extend(overrides_by_name.values())
    return merged_program_weeks


def _coerce_lift_config(lift_config: dict[str, Any] | LiftSettings) -> dict[str, Any]:
    if isinstance(lift_config, LiftSettings):
        return {
            "name": lift_config.name,
            "abbreviation": lift_config.abbreviation,
            "bodyweight_coefficient": lift_config.bodyweight_coefficient,
            "rounding_increment": lift_config.rounding_increment,
            "one_rep_max": lift_config.one_rep_max,
            "training_max_factor": lift_config.training_max_factor,
        }

    return lift_config


def _get_rounding_increment(lift_config: dict[str, Any] | LiftSettings) -> float:
    if isinstance(lift_config, LiftSettings):
        return float(lift_config.rounding_increment)

    if "rounding_increment" in lift_config:
        return float(lift_config["rounding_increment"])

    bodyweight_coefficient = float(lift_config.get("bodyweight_coefficient", 0.0))
    return 1.25 if bodyweight_coefficient > 0 else 2.5


def _coerce_program_week_config(
    week_config: dict[str, Any] | ProgramWeekSettings,
) -> dict[str, Any]:
    if isinstance(week_config, ProgramWeekSettings):
        return {
            "name": week_config.name,
            "scaling_factors": list(week_config.scaling_factors),
            "reps_per_set": list(week_config.reps_per_set),
        }

    if "name" in week_config:
        return week_config

    week_name, week_values = next(iter(week_config.items()))
    week_settings = _flatten_week_settings(week_values)
    return {
        "name": week_name,
        "scaling_factors": list(week_settings["scaling_factors"]),
        "reps_per_set": list(week_settings["reps_per_set"]),
    }


def _flatten_week_settings(week_values: list[dict]) -> dict:
    flattened_settings = {}

    for item in week_values:
        flattened_settings.update(item)

    return flattened_settings


def _resolve_local_override_path(config_path: Path) -> Path:
    return config_path.with_name(f"{config_path.name}.local")


def _pop_matching_lift_override(
    default_lift: dict[str, Any],
    override_lifts: list[dict[str, Any]],
) -> dict[str, Any]:
    default_identifiers = _get_lift_identifiers(default_lift)

    for index, override_lift in enumerate(override_lifts):
        if default_identifiers.intersection(_get_lift_identifiers(override_lift)):
            return override_lifts.pop(index)

    return {}


def _get_lift_identifiers(lift_config: dict[str, Any]) -> set[str]:
    identifiers = set()

    if "abbreviation" in lift_config:
        identifiers.add(str(lift_config["abbreviation"]))
    if "name" in lift_config:
        identifiers.add(str(lift_config["name"]))

    return identifiers

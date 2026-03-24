from pathlib import Path
from typing import Any

import yaml

from .defaults import get_default_settings
from .models import (
    Lift,
    LiftContext,
    LiftProgramContext,
    ProgramWeek,
    ProgramWeekContext,
)
from .settings import AppSettings, LiftSettings, ProgramWeekSettings


def load_config(config_path: str | Path) -> dict[str, Any]:
    resolved_path = Path(config_path).expanduser().resolve()

    with resolved_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file) or {}

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a top-level mapping")

    return config


def load_settings(config_path: str | Path) -> AppSettings:
    return build_settings(_load_layered_config(config_path))


def build_settings(config_overrides: dict[str, Any] | None = None) -> AppSettings:
    merged_config = merge_config_overrides(config_overrides or {})
    return AppSettings(
        bodyweight=_require_float(merged_config, "bodyweight", "app settings"),
        zero_weight_strictness=_require_float(
            merged_config,
            "zero_weight_strictness",
            "app settings",
        ),
        competition_attempt_factors=_build_attempt_factors_config(
            merged_config.get("competition_attempt_factors", [])
        ),
        lifts=_build_lift_settings(merged_config.get("lifts", [])),
        program_weeks=_build_program_week_settings(
            merged_config.get("program_weeks", [])
        ),
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
        lift = _build_lift(lift_data, context="lift program context")
        lift_context = LiftContext(
            lift=lift,
            one_rep_max=_require_float(lift_data, "one_rep_max", lift.name),
        )
        lift_program_contexts[lift] = LiftProgramContext(
            lift_context=lift_context,
            training_max_factor=_require_float(
                lift_data,
                "training_max_factor",
                lift.name,
            ),
        )

    return lift_program_contexts


def build_program_week_contexts(
    program_weeks_config: list[dict] | list[ProgramWeekSettings],
) -> dict[ProgramWeek, ProgramWeekContext]:
    program_week_contexts: dict[ProgramWeek, ProgramWeekContext] = {}

    for week_config in program_weeks_config:
        week_data = _coerce_program_week_config(week_config)
        program_week_name = _require_str(week_data, "name", "program week")
        program_week = ProgramWeek(program_week_name)
        program_week_contexts[program_week] = ProgramWeekContext(
            program_week=program_week,
            scaling_factors=_coerce_float_list(
                week_data.get("scaling_factors", []),
                f"{program_week_name} scaling_factors",
            ),
            reps_per_set=_coerce_int_list(
                week_data.get("reps_per_set", []),
                f"{program_week_name} reps_per_set",
            ),
        )

    return program_week_contexts


def build_attempt_factors(attempt_factors_config: list[float]) -> list[float]:
    return _build_attempt_factors_config(attempt_factors_config)


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


def _load_layered_config(config_path: str | Path) -> dict[str, Any]:
    resolved_config_path = Path(config_path).expanduser().resolve()
    merged_config = merge_config_overrides(load_config(resolved_config_path))

    local_override_path = _resolve_local_override_path(resolved_config_path)
    if not local_override_path.exists():
        return merged_config

    local_overrides = load_config(local_override_path)
    return merge_config_overrides(local_overrides, base_config=merged_config)


def _build_lift_settings(lifts_config: list[dict[str, Any]]) -> list[LiftSettings]:
    return [
        LiftSettings(
            name=_require_str(lift_config, "name", "lift settings"),
            abbreviation=_require_str(lift_config, "abbreviation", "lift settings"),
            bodyweight_coefficient=_require_float(
                lift_config,
                "bodyweight_coefficient",
                _describe_lift(lift_config),
            ),
            rounding_increment=_get_rounding_increment(lift_config),
            one_rep_max=_require_float(
                lift_config,
                "one_rep_max",
                _describe_lift(lift_config),
            ),
            training_max_factor=_require_float(
                lift_config,
                "training_max_factor",
                _describe_lift(lift_config),
            ),
        )
        for lift_config in lifts_config
    ]


def _build_program_week_settings(
    program_weeks_config: list[dict[str, Any]],
) -> list[ProgramWeekSettings]:
    return [
        ProgramWeekSettings(
            name=_require_str(week_config, "name", "program week settings"),
            scaling_factors=_coerce_float_list(
                week_config.get("scaling_factors", []),
                f"{week_config.get('name', 'program week')} scaling_factors",
            ),
            reps_per_set=_coerce_int_list(
                week_config.get("reps_per_set", []),
                f"{week_config.get('name', 'program week')} reps_per_set",
            ),
        )
        for week_config in program_weeks_config
    ]


def _build_lift(lift_config: dict[str, Any], context: str) -> Lift:
    return Lift(
        name=_require_str(lift_config, "name", context),
        abbreviation=_require_str(lift_config, "abbreviation", context),
        bodyweight_coefficient=_require_float(
            lift_config,
            "bodyweight_coefficient",
            _describe_lift(lift_config),
        ),
        rounding_increment=_get_rounding_increment(lift_config),
    )


def _build_attempt_factors_config(attempt_factors_config: list[Any]) -> list[float]:
    return _coerce_float_list(attempt_factors_config, "competition_attempt_factors")


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


def _describe_lift(lift_config: dict[str, Any]) -> str:
    if "name" in lift_config:
        return str(lift_config["name"])

    return "lift"


def _require_str(config: dict[str, Any], key: str, context: str) -> str:
    if key not in config:
        raise ValueError(f"Missing '{key}' in {context}.")

    return str(config[key])


def _require_float(config: dict[str, Any], key: str, context: str) -> float:
    if key not in config:
        raise ValueError(f"Missing '{key}' in {context}.")

    try:
        return float(config[key])
    except (TypeError, ValueError) as error:
        raise ValueError(f"Expected '{key}' in {context} to be numeric.") from error


def _coerce_float_list(values: list[Any], context: str) -> list[float]:
    try:
        return [float(value) for value in values]
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Expected {context} to contain only numeric values."
        ) from error


def _coerce_int_list(values: list[Any], context: str) -> list[int]:
    try:
        return [int(value) for value in values]
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Expected {context} to contain only integer values."
        ) from error

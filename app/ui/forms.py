from dataclasses import dataclass

from core.settings import AppSettings, LiftSettings
import streamlit as st


BODYWEIGHT_COEFFICIENT_HELP = (
    "How much BW counts. 1.0 = full BW, 0.0 = external load only."
)
TRAINING_MAX_FACTOR_HELP = "TM as a share of effective 1RM. Usually 0.85 to 0.90."
ROUNDING_INCREMENT_HELP = "Load jump for this lift. Usually 1.25 or 2.5."
ZERO_WEIGHT_STRICTNESS_HELP = (
    "Controls how aggressively reps are reduced when a calculated load drops below "
    "0kg. Higher values are stricter and reduce reps more."
)


@dataclass(frozen=True)
class ParsedDecimalInput:
    value: float
    error: str | None = None


def render_settings_form(
    initial_settings: AppSettings,
) -> tuple[AppSettings, bool]:
    validation_errors: list[str] = []

    with st.form("planner-form"):
        st.subheader("Inputs")
        bodyweight_input = _render_decimal_input(
            st,
            "Bodyweight (kg)",
            value=float(initial_settings.bodyweight),
            key="bodyweight",
            min_value=0.0,
            max_value=250.0,
        )
        _append_error(validation_errors, bodyweight_input.error)

        st.caption("Lifts")
        lift_settings: list[LiftSettings] = []
        for left_lift, right_lift in _pair_lifts(initial_settings.lifts):
            lift_columns = st.columns(2)
            left_lift_settings, left_errors = _render_lift_input(
                lift_columns[0],
                left_lift,
            )
            lift_settings.append(left_lift_settings)
            validation_errors.extend(left_errors)
            if right_lift is not None:
                right_lift_settings, right_errors = _render_lift_input(
                    lift_columns[1],
                    right_lift,
                )
                lift_settings.append(right_lift_settings)
                validation_errors.extend(right_errors)

        attempt_factors = list(initial_settings.competition_attempt_factors)
        zero_weight_strictness = initial_settings.zero_weight_strictness
        with st.expander("Advanced Settings"):
            attempt_factors, attempt_errors = _render_attempt_factor_inputs(
                initial_settings.competition_attempt_factors
            )
            validation_errors.extend(attempt_errors)

            st.caption("Lift coefficients and training max factors")
            advanced_lift_settings: list[LiftSettings] = []
            for lift in lift_settings:
                advanced_lift, advanced_errors = _render_advanced_lift_inputs(lift)
                advanced_lift_settings.append(advanced_lift)
                validation_errors.extend(advanced_errors)
            lift_settings = advanced_lift_settings

            zero_weight_strictness = st.slider(
                "Zero-weight strictness",
                min_value=0.0,
                max_value=1.0,
                value=float(initial_settings.zero_weight_strictness),
                step=0.05,
                help=ZERO_WEIGHT_STRICTNESS_HELP,
            )

        if validation_errors:
            st.error(
                "Please fix the highlighted input values before generating output."
            )
            for error in validation_errors:
                st.caption(f"- {error}")

        submitted = st.form_submit_button("Generate", use_container_width=True)

    settings = AppSettings(
        bodyweight=bodyweight_input.value,
        zero_weight_strictness=zero_weight_strictness,
        competition_attempt_factors=attempt_factors,
        lifts=lift_settings,
        program_weeks=initial_settings.program_weeks,
    )

    return settings, submitted and not validation_errors


def _render_lift_input(
    container: st.delta_generator.DeltaGenerator, lift: LiftSettings
) -> tuple[LiftSettings, list[str]]:
    one_rep_max = _render_decimal_input(
        container,
        f"{lift.name} 1RM (kg)",
        value=float(lift.one_rep_max),
        key=f"{lift.abbreviation}-one-rep-max",
        min_value=0.0,
        max_value=500.0,
    )
    errors: list[str] = []
    _append_error(errors, one_rep_max.error)
    return (
        LiftSettings(
            name=lift.name,
            abbreviation=lift.abbreviation,
            bodyweight_coefficient=lift.bodyweight_coefficient,
            rounding_increment=lift.rounding_increment,
            one_rep_max=one_rep_max.value,
            training_max_factor=lift.training_max_factor,
        ),
        errors,
    )


def _render_advanced_lift_inputs(lift: LiftSettings) -> tuple[LiftSettings, list[str]]:
    st.markdown(f"**{lift.name}**")
    columns = st.columns(3)
    bodyweight_coefficient = _render_decimal_input(
        columns[0],
        "BW coeff.",
        value=float(lift.bodyweight_coefficient),
        key=f"{lift.abbreviation}-bodyweight-coefficient",
        min_value=0.0,
        max_value=1.5,
        help=BODYWEIGHT_COEFFICIENT_HELP,
    )
    training_max_factor = _render_decimal_input(
        columns[1],
        "TM factor",
        value=float(lift.training_max_factor),
        key=f"{lift.abbreviation}-training-max-factor",
        min_value=0.0,
        max_value=1.2,
        help=TRAINING_MAX_FACTOR_HELP,
    )
    rounding_increment = _render_decimal_input(
        columns[2],
        "Increment",
        value=float(lift.rounding_increment),
        key=f"{lift.abbreviation}-rounding-increment",
        min_value=0.25,
        max_value=10.0,
        help=ROUNDING_INCREMENT_HELP,
    )
    errors: list[str] = []
    _append_error(errors, bodyweight_coefficient.error)
    _append_error(errors, training_max_factor.error)
    _append_error(errors, rounding_increment.error)
    return (
        LiftSettings(
            name=lift.name,
            abbreviation=lift.abbreviation,
            bodyweight_coefficient=bodyweight_coefficient.value,
            rounding_increment=rounding_increment.value,
            one_rep_max=lift.one_rep_max,
            training_max_factor=training_max_factor.value,
        ),
        errors,
    )


def _render_attempt_factor_inputs(
    attempt_factors: list[float],
) -> tuple[list[float], list[str]]:
    errors: list[str] = []

    # Guard against empty attempt_factors to avoid st.columns(0), which raises an error.
    if not attempt_factors:
        st.error(
            "No attempt factors are configured. Please configure at least one attempt factor."
        )
        errors.append(
            "No attempt factors are configured. Please configure at least one attempt factor."
        )
        return [], errors

    columns = st.columns(len(attempt_factors))
    labels = ["1st attempt", "2nd attempt", "3rd attempt"]
    rendered_attempt_factors = []

    for index, attempt_factor in enumerate(attempt_factors):
        label = labels[index] if index < len(labels) else f"Attempt {index + 1}"
        parsed_attempt_factor = _render_decimal_input(
            columns[index],
            label,
            value=float(attempt_factor),
            key=f"attempt-factor-{index}",
            min_value=0.0,
            max_value=1.2,
        )
        rendered_attempt_factors.append(parsed_attempt_factor.value)
        _append_error(errors, parsed_attempt_factor.error)

    return rendered_attempt_factors, errors


def _pair_lifts(
    lifts: list[LiftSettings],
) -> list[tuple[LiftSettings, LiftSettings | None]]:
    paired_lifts = []

    for index in range(0, len(lifts), 2):
        left_lift = lifts[index]
        right_lift = lifts[index + 1] if index + 1 < len(lifts) else None
        paired_lifts.append((left_lift, right_lift))

    return paired_lifts


def _render_decimal_input(
    container: st.delta_generator.DeltaGenerator,
    label: str,
    value: float,
    key: str,
    min_value: float | None = None,
    max_value: float | None = None,
    help: str | None = None,
) -> ParsedDecimalInput:
    raw_value = container.text_input(
        label,
        value=_format_decimal_input(value),
        key=key,
        help=help,
    )
    normalized_value = raw_value.strip().replace(",", ".")

    try:
        parsed_value = float(normalized_value)
    except ValueError:
        return ParsedDecimalInput(
            value=value,
            error=f"{label}: enter a valid number using digits and an optional decimal point.",
        )

    if min_value is not None:
        if parsed_value < min_value:
            return ParsedDecimalInput(
                value=value,
                error=f"{label}: value must be at least {min_value}.",
            )

    if max_value is not None:
        if parsed_value > max_value:
            return ParsedDecimalInput(
                value=value,
                error=f"{label}: value must be at most {max_value}.",
            )

    return ParsedDecimalInput(value=parsed_value)


def _format_decimal_input(value: float) -> str:
    if value.is_integer():
        return str(int(value))

    return f"{value:.2f}".rstrip("0").rstrip(".")


def _append_error(errors: list[str], error: str | None) -> None:
    if error is not None:
        errors.append(error)

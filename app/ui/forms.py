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


def render_settings_form(
    initial_settings: AppSettings,
) -> tuple[AppSettings, bool]:
    with st.form("planner-form"):
        st.subheader("Inputs")
        bodyweight = st.number_input(
            "Bodyweight (kg)",
            min_value=0.0,
            value=float(initial_settings.bodyweight),
            step=0.5,
        )

        st.caption("Lifts")
        lift_settings = []
        for left_lift, right_lift in _pair_lifts(initial_settings.lifts):
            lift_columns = st.columns(2)
            lift_settings.append(_render_lift_input(lift_columns[0], left_lift))
            if right_lift is not None:
                lift_settings.append(_render_lift_input(lift_columns[1], right_lift))

        with st.expander("Advanced Settings"):
            attempt_factors = _render_attempt_factor_inputs(
                initial_settings.competition_attempt_factors
            )

            st.caption("Lift coefficients and training max factors")
            advanced_lift_settings = []
            for lift in lift_settings:
                advanced_lift_settings.append(_render_advanced_lift_inputs(lift))
            lift_settings = advanced_lift_settings

            zero_weight_strictness = st.slider(
                "Zero-weight strictness",
                min_value=0.0,
                max_value=1.0,
                value=float(initial_settings.zero_weight_strictness),
                step=0.05,
                help=ZERO_WEIGHT_STRICTNESS_HELP,
            )

        submitted = st.form_submit_button("Generate", use_container_width=True)

    settings = AppSettings(
        bodyweight=bodyweight,
        zero_weight_strictness=zero_weight_strictness
        if "zero_weight_strictness" in locals()
        else initial_settings.zero_weight_strictness,
        competition_attempt_factors=attempt_factors
        if "attempt_factors" in locals()
        else list(initial_settings.competition_attempt_factors),
        lifts=lift_settings,
        program_weeks=initial_settings.program_weeks,
    )

    return settings, submitted


def _render_lift_input(
    container: st.delta_generator.DeltaGenerator, lift: LiftSettings
) -> LiftSettings:
    one_rep_max = container.number_input(
        f"{lift.name} 1RM (kg)",
        min_value=0.0,
        value=float(lift.one_rep_max),
        step=1.0,
        key=f"{lift.abbreviation}-one-rep-max",
    )
    return LiftSettings(
        name=lift.name,
        abbreviation=lift.abbreviation,
        bodyweight_coefficient=lift.bodyweight_coefficient,
        rounding_increment=lift.rounding_increment,
        one_rep_max=one_rep_max,
        training_max_factor=lift.training_max_factor,
    )


def _render_advanced_lift_inputs(lift: LiftSettings) -> LiftSettings:
    st.markdown(f"**{lift.name}**")
    columns = st.columns(3)
    bodyweight_coefficient = columns[0].number_input(
        "BW coeff.",
        min_value=0.0,
        value=float(lift.bodyweight_coefficient),
        step=0.05,
        key=f"{lift.abbreviation}-bodyweight-coefficient",
        help=BODYWEIGHT_COEFFICIENT_HELP,
    )
    training_max_factor = columns[1].number_input(
        "TM factor",
        min_value=0.0,
        value=float(lift.training_max_factor),
        step=0.01,
        key=f"{lift.abbreviation}-training-max-factor",
        help=TRAINING_MAX_FACTOR_HELP,
    )
    rounding_increment = columns[2].number_input(
        "Increment",
        min_value=0.25,
        value=float(lift.rounding_increment),
        step=0.25,
        key=f"{lift.abbreviation}-rounding-increment",
        help=ROUNDING_INCREMENT_HELP,
    )
    return LiftSettings(
        name=lift.name,
        abbreviation=lift.abbreviation,
        bodyweight_coefficient=bodyweight_coefficient,
        rounding_increment=rounding_increment,
        one_rep_max=lift.one_rep_max,
        training_max_factor=training_max_factor,
    )


def _render_attempt_factor_inputs(attempt_factors: list[float]) -> list[float]:
    columns = st.columns(len(attempt_factors))
    labels = ["1st attempt", "2nd attempt", "3rd attempt"]
    rendered_attempt_factors = []

    for index, attempt_factor in enumerate(attempt_factors):
        label = labels[index] if index < len(labels) else f"Attempt {index + 1}"
        rendered_attempt_factors.append(
            columns[index].number_input(
                label,
                min_value=0.0,
                value=float(attempt_factor),
                step=0.01,
                key=f"attempt-factor-{index}",
            )
        )

    return rendered_attempt_factors


def _pair_lifts(
    lifts: list[LiftSettings],
) -> list[tuple[LiftSettings, LiftSettings | None]]:
    paired_lifts = []

    for index in range(0, len(lifts), 2):
        left_lift = lifts[index]
        right_lift = lifts[index + 1] if index + 1 < len(lifts) else None
        paired_lifts.append((left_lift, right_lift))

    return paired_lifts

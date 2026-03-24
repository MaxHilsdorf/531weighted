from core.settings import AppSettings, LiftSettings, ProgramWeekSettings


def get_default_settings() -> AppSettings:
    return AppSettings(
        bodyweight=75.0,
        zero_weight_strictness=0.3,
        competition_attempt_factors=[0.87, 0.95, 1.0],
        lifts=[
            LiftSettings(
                name="Muscle Up",
                abbreviation="MU",
                bodyweight_coefficient=0.85,
                rounding_increment=1.25,
                one_rep_max=5.0,
                training_max_factor=0.87,
            ),
            LiftSettings(
                name="Pull Up",
                abbreviation="PU",
                bodyweight_coefficient=0.95,
                rounding_increment=1.25,
                one_rep_max=40.0,
                training_max_factor=0.87,
            ),
            LiftSettings(
                name="Dip",
                abbreviation="D",
                bodyweight_coefficient=0.85,
                rounding_increment=1.25,
                one_rep_max=60.0,
                training_max_factor=0.87,
            ),
            LiftSettings(
                name="Squat",
                abbreviation="SQ",
                bodyweight_coefficient=0.25,
                rounding_increment=2.5,
                one_rep_max=100.0,
                training_max_factor=0.90,
            ),
        ],
        program_weeks=[
            ProgramWeekSettings(
                name="5", scaling_factors=[0.65, 0.75, 0.85], reps_per_set=[5, 5, 5]
            ),
            ProgramWeekSettings(
                name="3", scaling_factors=[0.70, 0.80, 0.90], reps_per_set=[3, 3, 3]
            ),
            ProgramWeekSettings(
                name="1", scaling_factors=[0.75, 0.85, 0.95], reps_per_set=[5, 3, 1]
            ),
            ProgramWeekSettings(
                name="deload",
                scaling_factors=[0.40, 0.50, 0.60],
                reps_per_set=[5, 5, 5],
            ),
        ],
    )

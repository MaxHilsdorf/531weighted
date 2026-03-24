from app.ui.renderers import build_output
from core.defaults import get_default_settings
from core.settings import AppSettings, LiftSettings


def test_build_output_supports_both_sections() -> None:
    default_settings = get_default_settings()
    settings = AppSettings(
        bodyweight=74,
        zero_weight_strictness=default_settings.zero_weight_strictness,
        competition_attempt_factors=default_settings.competition_attempt_factors,
        lifts=[
            LiftSettings(
                name=lift.name,
                abbreviation=lift.abbreviation,
                bodyweight_coefficient=lift.bodyweight_coefficient,
                rounding_increment=lift.rounding_increment,
                one_rep_max=20 if lift.abbreviation == "MU" else 100,
                training_max_factor=lift.training_max_factor,
            )
            for lift in default_settings.lifts
        ],
        program_weeks=default_settings.program_weeks,
    )

    output = build_output(settings)

    assert output.attempt_section.title == "Competition Attempts"
    assert output.attempt_section.rows
    assert "Competition Attempts" in output.attempt_section.raw_text
    assert output.program_section.overview_rows
    assert output.program_section.week_sections
    assert "5/3/1 Program" in output.program_section.raw_text

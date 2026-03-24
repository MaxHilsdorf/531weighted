from pathlib import Path

import pytest

from core.config_loader import build_settings, load_config


def test_load_config_reads_existing_repo_config() -> None:
    config = load_config(Path(__file__).resolve().parent.parent / "config.yaml")

    assert "lifts" in config
    assert "program_weeks" in config


def test_load_config_rejects_non_mapping_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "invalid.yaml"
    config_path.write_text("- just\n- a\n- list\n", encoding="utf-8")

    with pytest.raises(ValueError, match="top-level mapping"):
        load_config(config_path)


def test_build_settings_merges_partial_overrides_over_defaults() -> None:
    settings = build_settings(
        {
            "bodyweight": 80,
            "lifts": [
                {"abbreviation": "PU", "one_rep_max": 55},
            ],
        }
    )

    pull_up = next(lift for lift in settings.lifts if lift.abbreviation == "PU")
    squat = next(lift for lift in settings.lifts if lift.abbreviation == "SQ")

    assert settings.bodyweight == 80
    assert pull_up.one_rep_max == 55
    assert pull_up.training_max_factor == 0.87
    assert pull_up.rounding_increment == 1.25
    assert squat.name == "Squat"
    assert squat.rounding_increment == 2.5


def test_build_settings_preserves_default_program_weeks_when_not_overridden() -> None:
    settings = build_settings({})

    assert [week.name for week in settings.program_weeks] == ["5", "3", "1", "deload"]


def test_load_settings_accepts_partial_file_overrides(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        "bodyweight: 81\nlifts:\n  - abbreviation: PU\n    one_rep_max: 58\n",
        encoding="utf-8",
    )

    from core.config_loader import load_settings

    settings = load_settings(config_path)

    assert settings.bodyweight == 81
    assert (
        next(lift for lift in settings.lifts if lift.abbreviation == "PU").one_rep_max
        == 58
    )


def test_load_settings_applies_local_overrides_when_present(tmp_path: Path) -> None:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(
        (
            "bodyweight: 80\n"
            "lifts:\n"
            "  - name: Pull Up\n"
            "    abbreviation: PU\n"
            "    one_rep_max: 50\n"
        ),
        encoding="utf-8",
    )
    local_config_path = tmp_path / "config.yaml.local"
    local_config_path.write_text(
        ("bodyweight: 81\nlifts:\n  - name: Pull Up\n    one_rep_max: 58\n"),
        encoding="utf-8",
    )

    from core.config_loader import load_settings

    settings = load_settings(config_path)

    pull_up = next(lift for lift in settings.lifts if lift.abbreviation == "PU")

    assert settings.bodyweight == 81
    assert pull_up.one_rep_max == 58


def test_build_settings_merges_lift_overrides_by_name() -> None:
    settings = build_settings(
        {
            "lifts": [
                {"name": "Squat", "training_max_factor": 0.92},
            ],
        }
    )

    squat = next(lift for lift in settings.lifts if lift.abbreviation == "SQ")

    assert squat.training_max_factor == 0.92

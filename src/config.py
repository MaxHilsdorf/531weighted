from pathlib import Path
from typing import Any

import yaml


def load_config(config_path: str | Path) -> dict[str, Any]:
	resolved_path = Path(config_path).expanduser().resolve()

	with resolved_path.open("r", encoding="utf-8") as config_file:
		config = yaml.safe_load(config_file)

	if not isinstance(config, dict):
		raise ValueError("Config file must contain a top-level mapping")

	if "lifts" not in config or not isinstance(config["lifts"], list):
		raise ValueError("Config file must define a 'lifts' list")

	if "program_weeks" not in config or not isinstance(config["program_weeks"], list):
		raise ValueError("Config file must define a 'program_weeks' list")

	return config

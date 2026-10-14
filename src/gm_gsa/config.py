from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMER_ID_RE = re.compile(r"^[0-9]{10}$")


class ConfigurationError(ValueError):
    pass


def normalize_customer_id(value: str | int | None) -> str:
    candidate = re.sub(r"[^0-9]", "", str(value or ""))
    if not CUSTOMER_ID_RE.fullmatch(candidate):
        raise ConfigurationError("Google Ads customer IDs must contain exactly 10 digits.")
    return candidate


def load_yaml(path: str | Path) -> dict[str, Any]:
    resolved = Path(path)
    if not resolved.exists():
        raise ConfigurationError(f"Configuration file does not exist: {resolved}")
    with resolved.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if not isinstance(data, dict):
        raise ConfigurationError(f"Expected a YAML mapping in {resolved}")
    return data


def load_dotenv_if_available(path: str | Path | None = None) -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(dotenv_path=path, override=False)


def required_env(names: list[str]) -> dict[str, str]:
    missing = [name for name in names if not os.getenv(name)]
    if missing:
        raise ConfigurationError(
            "Missing required environment variables: " + ", ".join(sorted(missing))
        )
    return {name: os.environ[name] for name in names}


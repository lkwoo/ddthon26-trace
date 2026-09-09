"""Configuration loading (distractor: unrelated to the questions)."""

import os


def get_setting(name: str, default: str = "") -> str:
    """Read a configuration setting from the environment."""
    return os.environ.get(name, default)


def as_bool(value: str) -> bool:
    """Interpret a configuration string as a boolean."""
    return value.strip().lower() in {"1", "true", "yes", "on"}

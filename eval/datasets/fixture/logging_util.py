"""Logging helpers (distractor: unrelated to the questions)."""

import sys


def log_info(message: str) -> None:
    """Write an informational log line to stdout."""
    sys.stdout.write(f"INFO: {message}\n")


def log_error(message: str) -> None:
    """Write an error log line to stderr."""
    sys.stderr.write(f"ERROR: {message}\n")

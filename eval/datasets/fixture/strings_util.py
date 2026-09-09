"""String helpers (distractor: unrelated to the questions)."""


def slugify(text: str) -> str:
    """Turn arbitrary text into a lowercase hyphenated slug."""
    return "-".join(text.lower().split())


def truncate(text: str, length: int) -> str:
    """Truncate text to a maximum length, adding an ellipsis when cut."""
    if len(text) <= length:
        return text
    return text[: max(0, length - 1)] + "…"

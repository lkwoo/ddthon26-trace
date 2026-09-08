"""Token estimation and budget-aware snippet selection (US-A3, US-N2, PBT-03).

`estimate_tokens` is a deterministic, local heuristic (Q4=A) — no external
tokenizer dependency (NFR-C3). `select_snippet` guarantees the returned snippet
never exceeds the budget (BR-17) and marks truncation (BR-19).
"""

from __future__ import annotations

import math

from ..domain.models import Snippet


def estimate_tokens(text: str) -> int:
    """Deterministic token estimate.

    Monotonic and non-negative (PBT-03): a superset string never estimates
    fewer tokens. Approximates ~4 chars/token plus a symbol/newline correction.
    """
    if not text:
        return 0
    char_tokens = math.ceil(len(text) / 4)
    # Newlines and structural symbols tend to be their own tokens.
    symbol_bonus = sum(1 for ch in text if ch in "\n{}()[];,:")
    return char_tokens + symbol_bonus


def select_snippet(text: str, token_budget: int) -> Snippet:
    """Return a snippet whose estimate is within ``token_budget``.

    Truncation strategy (Q3=A / BR-18): keep the leading (target) body, drop
    trailing lines until the budget is met.
    """
    if token_budget < 0:
        raise ValueError("token_budget must be non-negative")

    full = estimate_tokens(text)
    if full <= token_budget:
        return Snippet(text=text, estimated_tokens=full, truncated=False)

    # Truncate line-by-line from the end (preserve the target-proximate head).
    lines = text.splitlines(keepends=True)
    kept: list[str] = []
    for line in lines:
        candidate = "".join(kept) + line
        if estimate_tokens(candidate) > token_budget:
            break
        kept.append(line)

    snippet_text = "".join(kept)
    # If even the first line overflows, hard-trim by characters as a last resort.
    if not snippet_text and token_budget > 0:
        approx_chars = max(0, token_budget * 4 - 1)
        snippet_text = text[:approx_chars]
        while estimate_tokens(snippet_text) > token_budget and snippet_text:
            snippet_text = snippet_text[:-1]

    return Snippet(
        text=snippet_text,
        estimated_tokens=estimate_tokens(snippet_text),
        truncated=True,
    )

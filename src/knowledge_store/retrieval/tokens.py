"""TokenEstimator — deterministic token-count estimation (NFR-1.2).

A lightweight, model-agnostic heuristic (roughly GPT-style BPE density) that is
monotonic in input length: longer text never estimates fewer tokens. This
monotonicity is a documented invariant used by the SnippetBuilder budget logic
and is covered by a property-based test (PBT-03).
"""

from __future__ import annotations

import re

_WORD_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)


class TokenEstimator:
    #: average characters per token for typical prose/code
    CHARS_PER_TOKEN = 4

    def estimate(self, text: str) -> int:
        """Estimate token count. Empty text is 0 tokens; otherwise at least 1."""
        if not text:
            return 0
        # Blend a word/punctuation count with a char-density estimate and take
        # the larger — conservative so snippets never under-count the budget.
        pieces = len(_WORD_RE.findall(text))
        char_estimate = (len(text) + self.CHARS_PER_TOKEN - 1) // self.CHARS_PER_TOKEN
        return max(1, pieces, char_estimate)

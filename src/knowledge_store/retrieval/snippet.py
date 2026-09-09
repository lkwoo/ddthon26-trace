"""SnippetBuilder — token-budget-aware scope cutting (US-6.3, NFR-1.2).

Given target content and a token budget, returns the most relevant minimal scope
that does not exceed the budget while preserving semantic-unit (line) boundaries
where possible. When even the first semantic unit exceeds the budget, the text is
hard-cut to fit. The returned ``estimated_tokens`` is always ``<= token_budget``
for any ``token_budget >= 1`` — a documented invariant covered by PBT (PBT-03).
"""

from __future__ import annotations

from knowledge_store.retrieval.tokens import TokenEstimator
from knowledge_store.types import SnippetResult, Status


class SnippetBuilder:
    def __init__(self, estimator: TokenEstimator | None = None) -> None:
        self._estimator = estimator or TokenEstimator()

    def build(self, text: str, token_budget: int) -> SnippetResult:
        if token_budget < 1:
            return SnippetResult(status=Status.OK, text="", estimated_tokens=0,
                                 token_budget=token_budget, truncated=bool(text))
        if not text:
            return SnippetResult(status=Status.OK, text="", estimated_tokens=0,
                                 token_budget=token_budget, truncated=False)

        units = text.splitlines(keepends=True)
        acc: list[str] = []
        for unit in units:
            candidate = "".join(acc + [unit])
            if self._estimator.estimate(candidate) <= token_budget:
                acc.append(unit)
            else:
                break

        if acc:
            snippet = "".join(acc)
            truncated = len(snippet) < len(text)
            return SnippetResult(
                status=Status.OK, text=snippet,
                estimated_tokens=self._estimator.estimate(snippet),
                token_budget=token_budget, truncated=truncated,
            )

        # First unit alone exceeds the budget: hard-cut by characters to fit.
        snippet = self._hard_cut(text, token_budget)
        return SnippetResult(
            status=Status.OK, text=snippet,
            estimated_tokens=self._estimator.estimate(snippet),
            token_budget=token_budget, truncated=True,
        )

    def _hard_cut(self, text: str, token_budget: int) -> str:
        """Shrink text until its estimate fits the budget (guaranteed to fit)."""
        max_chars = token_budget * TokenEstimator.CHARS_PER_TOKEN
        snippet = text[:max_chars]
        while snippet and self._estimator.estimate(snippet) > token_budget:
            snippet = snippet[: max(0, len(snippet) - max(1, len(snippet) // 8))]
        return snippet

"""Pure retrieval-quality metrics (recall@k, reciprocal rank, MRR).

All functions here are pure and deterministic — same inputs always produce the
same output — which is exactly what the Property-Based Testing extension expects
to cover (PBT Partial mode: pure functions). Metrics operate on an already
*ranked, de-duplicated* list of predicted item ids (here, file paths) and a set
of gold (relevant) ids. Working at a single granularity keeps the semantic and
grep baselines directly comparable.

Conventions:
* ``ranked`` is ordered best-first and must not contain duplicates for rank math
  to be meaningful; :func:`dedup` is provided to enforce that upstream.
* ``gold`` is the set of relevant ids. An empty gold set is treated as vacuously
  satisfied (recall 1.0, reciprocal rank 1.0) so aggregate math stays well-defined.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Sequence


def dedup(items: Iterable[str]) -> list[str]:
    """Return ``items`` with duplicates removed, preserving first-seen order."""
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        if it not in seen:
            seen.add(it)
            out.append(it)
    return out


def recall_at_k(ranked: Sequence[str], gold: Iterable[str], k: int) -> float:
    """Fraction of gold items present in the top-``k`` of ``ranked``.

    Returns a value in ``[0.0, 1.0]``. It is monotonically non-decreasing in
    ``k`` (widening the window can only find more gold). An empty gold set is
    vacuously satisfied and returns ``1.0``.
    """
    gold_set = set(gold)
    if not gold_set:
        return 1.0
    if k <= 0:
        return 0.0
    topk = set(ranked[:k])
    found = len(gold_set & topk)
    return found / len(gold_set)


def reciprocal_rank(ranked: Sequence[str], gold: Iterable[str]) -> float:
    """``1 / rank`` of the first relevant item (1-indexed), else ``0.0``.

    An empty gold set returns ``1.0`` (vacuously satisfied). The result is always
    in ``[0.0, 1.0]`` and takes values in ``{0} ∪ {1/n : n>=1}``.
    """
    gold_set = set(gold)
    if not gold_set:
        return 1.0
    for i, item in enumerate(ranked):
        if item in gold_set:
            return 1.0 / (i + 1)
    return 0.0


def mrr(reciprocal_ranks: Iterable[float]) -> float:
    """Mean reciprocal rank over a collection of per-query reciprocal ranks.

    Returns ``0.0`` for an empty collection.
    """
    rrs = list(reciprocal_ranks)
    if not rrs:
        return 0.0
    return sum(rrs) / len(rrs)


@dataclass(frozen=True)
class EvalScore:
    """Per-query score for one retriever."""

    recall_at_1: float
    recall_at_5: float
    recall_at_10: float
    reciprocal_rank: float

    def to_dict(self) -> dict[str, float]:
        return {
            "recall@1": self.recall_at_1,
            "recall@5": self.recall_at_5,
            "recall@10": self.recall_at_10,
            "reciprocal_rank": self.reciprocal_rank,
        }


def evaluate_ranking(ranked: Sequence[str], gold: Iterable[str]) -> EvalScore:
    """Compute the full per-query score (recall@1/5/10 + reciprocal rank)."""
    gold_list = list(gold)
    return EvalScore(
        recall_at_1=recall_at_k(ranked, gold_list, 1),
        recall_at_5=recall_at_k(ranked, gold_list, 5),
        recall_at_10=recall_at_k(ranked, gold_list, 10),
        reciprocal_rank=reciprocal_rank(ranked, gold_list),
    )

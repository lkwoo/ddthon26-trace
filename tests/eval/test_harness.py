"""Regression tests for the evaluation harness.

These are the "thin pytest wrapper asserting a minimum baseline" (Q6=C). They run
on whatever embedding provider is available (``allow_hash=True``) so they work in
CI without the heavyweight learned model, while the standalone ``python -m eval``
runner enforces the learned-model policy by default.
"""

from __future__ import annotations

import pytest

from eval.__main__ import _load
from eval.harness import (
    ProviderPolicyError,
    provider_is_learned,
    run_evaluation,
)
from knowledge_store.services.system import KnowledgeSystem


def _run(corpus: str):
    dataset, root, files = _load(corpus)
    assert files, f"corpus {corpus!r} resolved no files"
    return run_evaluation(dataset, root, files, allow_hash=True, limit=10)


def _all_scores_in_unit_interval(result) -> None:
    for method in result.methods.values():
        for score in method.per_query.values():
            for value in score.to_dict().values():
                assert 0.0 <= value <= 1.0


def test_fixture_baseline_is_perfect_and_deterministic():
    result = _run("fixture")
    _all_scores_in_unit_interval(result)
    assert set(result.methods) == {"semantic", "grep"}
    for name in ("semantic", "grep"):
        m = result.methods[name]
        # The fixture is keyword-obvious with distinct topics; every gold file is
        # found at rank 1 by both methods. This is the regression floor.
        assert m.mean_recall_at_1 == pytest.approx(1.0), name
        assert m.mean_recall_at_10 == pytest.approx(1.0), name
        assert m.mrr == pytest.approx(1.0), name


def test_repo_dogfood_baseline_floor():
    result = _run("repo")
    _all_scores_in_unit_interval(result)
    assert result.num_questions >= 15

    semantic = result.methods["semantic"]
    grep = result.methods["grep"]
    # Minimum-baseline guards (not exact pins) against catastrophic regression, on the
    # HASH fallback provider (the learned model is absent in CI). Increment-2 progression:
    #   original (blank-line chunks + pure vector): recall@10 0.833, MRR 0.621
    #   U-Chunking (method-aware chunks + pure vector): recall@10 0.944, MRR 0.444
    #     -> coverage up; MRR down is a bag-of-words dilution artifact (fixture stays 1.0),
    #        i.e. the "pure vector loses to grep on code" effect U-Hybrid targets.
    #   U-Hybrid (method-aware chunks + BM25/RRF fusion): recall@10 1.000, MRR ~0.575
    #     -> hybrid beats pure-vector on the SAME chunks on EVERY metric (recall@1
    #        0.222->0.333, recall@10 0.944->1.000, MRR 0.440->0.565); coverage now matches
    #        grep's best. On a learned code model both halves are strong and MRR exceeds
    #        either alone. These floors lock in the hybrid gains.
    assert semantic.mean_recall_at_10 >= 0.95
    assert grep.mean_recall_at_10 >= 0.90
    assert semantic.mrr >= 0.50
    assert grep.mrr >= 0.60


def test_provider_policy_fails_loud_on_hash_fallback(tmp_path):
    # Only meaningful when the learned model is absent (hash fallback active).
    probe = KnowledgeSystem(tmp_path, in_memory=True)
    try:
        learned = provider_is_learned(probe)
    finally:
        probe.close()
    if learned:
        pytest.skip("learned embedding model is installed; policy gate not exercised")

    dataset, root, files = _load("fixture")
    with pytest.raises(ProviderPolicyError):
        run_evaluation(dataset, root, files, allow_hash=False)

"""Property-based tests for the pure evaluation metrics + dataset round-trip.

Covered under PBT Partial mode: pure functions (recall@k, reciprocal rank, MRR)
and serialization round-trip (EvalDataset JSON).
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from eval.dataset import EvalDataset, EvalQuestion
from eval.metrics import (
    dedup,
    evaluate_ranking,
    mrr,
    recall_at_k,
    reciprocal_rank,
)

# Small id alphabet so gold and ranked lists actually overlap sometimes.
_ids = st.text(alphabet="abcdef", min_size=1, max_size=3)
_ranked = st.lists(_ids, min_size=0, max_size=20)
_gold = st.sets(_ids, min_size=0, max_size=6)


@given(_ranked, _gold, st.integers(min_value=-3, max_value=25))
def test_recall_in_unit_interval(ranked, gold, k):
    r = recall_at_k(ranked, gold, k)
    assert 0.0 <= r <= 1.0


@given(_ranked, _gold, st.integers(min_value=0, max_value=25))
def test_recall_monotonic_non_decreasing_in_k(ranked, gold, k):
    # Widening the top-k window can only find more (or equal) gold.
    assert recall_at_k(ranked, gold, k) <= recall_at_k(ranked, gold, k + 1) + 1e-12


@given(_ranked, _gold)
def test_recall_full_window_finds_all_present(ranked, gold):
    # With k >= len(ranked), recall equals the fraction of gold present anywhere.
    deduped = dedup(ranked)
    present = len(set(gold) & set(deduped))
    expected = 1.0 if not gold else present / len(set(gold))
    assert abs(recall_at_k(ranked, gold, len(ranked)) - expected) < 1e-9


@given(_ranked, _gold)
def test_reciprocal_rank_range_and_shape(ranked, gold):
    rr = reciprocal_rank(ranked, gold)
    assert 0.0 <= rr <= 1.0
    if gold:
        # rr is 0 or exactly 1/n for some rank n.
        if rr > 0:
            inv = 1.0 / rr
            assert abs(inv - round(inv)) < 1e-9


@given(_ranked, _gold)
def test_reciprocal_rank_top1_relevant_is_one(ranked, gold):
    if ranked and gold and ranked[0] in gold:
        assert reciprocal_rank(ranked, gold) == 1.0


@given(st.lists(st.floats(min_value=0.0, max_value=1.0), max_size=30))
def test_mrr_in_unit_interval(rrs):
    assert 0.0 <= mrr(rrs) <= 1.0


@given(_ranked)
def test_empty_gold_is_vacuously_satisfied(ranked):
    assert recall_at_k(ranked, set(), 5) == 1.0
    assert reciprocal_rank(ranked, set()) == 1.0


@given(_ranked, _gold)
def test_evaluate_ranking_consistent_with_scalars(ranked, gold):
    score = evaluate_ranking(ranked, gold)
    assert score.recall_at_1 == recall_at_k(ranked, gold, 1)
    assert score.recall_at_5 == recall_at_k(ranked, gold, 5)
    assert score.recall_at_10 == recall_at_k(ranked, gold, 10)
    assert score.reciprocal_rank == reciprocal_rank(ranked, gold)


# --- serialization round-trip (PBT-02 style) -------------------------------

_question = st.builds(
    EvalQuestion,
    id=st.text(alphabet="qid-0123456789", min_size=1, max_size=8),
    intent=st.text(min_size=0, max_size=40),
    gold_files=st.lists(st.text(alphabet="abc/._", min_size=1, max_size=8),
                        min_size=0, max_size=4).map(tuple),
    note=st.text(min_size=0, max_size=20),
)


@given(st.lists(_question, min_size=0, max_size=6),
       st.lists(st.text(alphabet="abc/", min_size=1, max_size=6), max_size=3))
def test_dataset_json_round_trip(questions, corpus):
    ds = EvalDataset(name="rt", questions=questions, corpus=corpus)
    restored = EvalDataset.from_json(ds.to_json())
    assert restored.to_dict() == ds.to_dict()

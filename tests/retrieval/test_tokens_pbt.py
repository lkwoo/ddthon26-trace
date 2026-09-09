"""PBT-03 — TokenEstimator monotonicity invariant (NFR-1.2).

Property: appending text never decreases the estimate; a prefix never estimates
more than the whole. Determinism is also asserted.
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from knowledge_store.retrieval.tokens import TokenEstimator

_text = st.text(min_size=0, max_size=300)


@given(a=_text, extra=_text)
@settings(max_examples=300)
def test_monotonic_under_append(a, extra):
    est = TokenEstimator()
    assert est.estimate(a) <= est.estimate(a + extra)


@given(text=_text)
@settings(max_examples=200)
def test_deterministic(text):
    est = TokenEstimator()
    assert est.estimate(text) == est.estimate(text)


@given(text=st.text(min_size=1, max_size=300))
def test_non_empty_is_at_least_one(text):
    assert TokenEstimator().estimate(text) >= 1


def test_empty_is_zero():
    assert TokenEstimator().estimate("") == 0

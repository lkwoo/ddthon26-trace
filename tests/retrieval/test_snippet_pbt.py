"""PBT-03 — SnippetBuilder token-budget invariant (US-6.3, NFR-1.2).

Property: for any text and any budget >= 1, the returned snippet's estimated
tokens never exceed the budget, and the snippet is a substring-composed prefix
of the source (semantic-unit preserving or hard-cut).
"""

from hypothesis import given, settings
from hypothesis import strategies as st

from knowledge_store.retrieval.snippet import SnippetBuilder
from knowledge_store.retrieval.tokens import TokenEstimator


@given(text=st.text(min_size=0, max_size=400), budget=st.integers(min_value=1, max_value=200))
@settings(max_examples=300)
def test_never_exceeds_budget(text, budget):
    result = SnippetBuilder().build(text, budget)
    assert result.estimated_tokens <= budget


@given(text=st.text(min_size=1, max_size=400), budget=st.integers(min_value=1, max_value=5))
@settings(max_examples=200)
def test_tiny_budget_still_fits(text, budget):
    # Even a hard-cut path must respect the budget.
    result = SnippetBuilder(TokenEstimator()).build(text, budget)
    assert result.estimated_tokens <= budget
    assert len(result.text) <= len(text)


@given(text=st.text(min_size=0, max_size=200))
def test_zero_budget_yields_empty(text):
    result = SnippetBuilder().build(text, 0)
    assert result.text == ""
    assert result.estimated_tokens == 0

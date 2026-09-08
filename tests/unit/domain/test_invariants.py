"""PBT-03 invariant properties for pure domain functions + example-based tests (PBT-10)."""

from hypothesis import given
from hypothesis import strategies as st

from agentic_kb.domain import graph_builder
from agentic_kb.domain.chunking import estimate_tokens, select_snippet
from agentic_kb.testing import strategies as ge


# --- estimate_tokens: monotonic + non-negative (PBT-03) ---
@given(st.text(), st.text())
def test_estimate_tokens_monotonic(a, b):
    assert estimate_tokens(a) >= 0
    # appending never decreases the estimate
    assert estimate_tokens(a + b) >= estimate_tokens(a)


# --- select_snippet: budget respected, truncation flag correct (PBT-03, BR-17/19) ---
@given(st.text(max_size=500), st.integers(min_value=0, max_value=300))
def test_select_snippet_within_budget(text, budget):
    snip = select_snippet(text, budget)
    assert snip.estimated_tokens <= budget
    assert snip.estimated_tokens == estimate_tokens(snip.text)
    if estimate_tokens(text) <= budget:
        assert snip.truncated is False
        assert snip.text == text
    else:
        assert snip.truncated is True


# --- graph_builder: edges deduped + endpoints in nodes (PBT-03, BR-26) ---
@given(st.lists(ge.parsed_units(), max_size=5))
def test_graph_build_integrity(units):
    graph = graph_builder.build(units)
    node_ids = {n.id for n in graph.nodes}
    for e in graph.edges:
        assert e.src in node_ids and e.dst in node_ids
    assert len(set(graph.edges)) == len(graph.edges)  # no duplicates
    # determinism: building twice yields identical output
    assert graph_builder.build(units) == graph


# --- example-based (PBT-10) ---
def test_estimate_tokens_empty():
    assert estimate_tokens("") == 0


def test_select_snippet_zero_budget():
    snip = select_snippet("def f():\n    return 1\n", 0)
    assert snip.estimated_tokens == 0
    assert snip.truncated is True

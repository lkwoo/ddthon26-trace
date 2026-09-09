# U5 Retrieval & Summarization — Code Summary

**Stage**: CONSTRUCTION → Code Generation
**Unit**: `u5-retrieval-summarization`
**Status**: Code generation complete (code already written and tested).

---

## Files

| File | Description |
|---|---|
| `knowledge_store/retrieval/tokens.py` | `TokenEstimator` — deterministic, monotonic token-count heuristic (`CHARS_PER_TOKEN = 4`). |
| `knowledge_store/retrieval/snippet.py` | `SnippetBuilder` — budget-aware, line-boundary-preserving scope cutter with `_hard_cut` fallback → `SnippetResult`. |
| `knowledge_store/retrieval/summary_store.py` | `SummaryStore` — content-to-summarize extraction + Agent-authored summary persistence/read + `pending()`. |
| `knowledge_store/retrieval/__init__.py` | Exports `TokenEstimator`, `SnippetBuilder`, `SummaryStore`. |

## Key public API

```python
TokenEstimator().estimate(text: str) -> int          # 0 for empty, else >=1, monotonic
SnippetBuilder(estimator=None).build(text, token_budget) -> SnippetResult
SummaryStore(repos).extract_for_summary(ref_id) -> Content | None
SummaryStore(repos).store_summary(chunk_id, text) -> Status
SummaryStore(repos).get_summary(chunk_id) -> Summary | None
SummaryStore(repos).pending() -> list[str]
```

## Tests exercising this unit

| Test | What it covers | Result |
|---|---|---|
| `tests/retrieval/test_tokens_pbt.py::test_monotonic_under_append` | PBT-03 monotonicity of `estimate` | pass |
| `...::test_deterministic` | same input → same estimate | pass |
| `...::test_non_empty_is_at_least_one` / `test_empty_is_zero` | ≥1 / 0 boundary | pass |
| `tests/retrieval/test_snippet_pbt.py::test_never_exceeds_budget` | PBT-03 budget invariant | pass |
| `...::test_tiny_budget_still_fits` | hard-cut path respects tiny budget | pass |
| `...::test_zero_budget_yields_empty` | budget 0 → empty snippet | pass |
| `tests/services/test_pipeline.py::test_summarization_is_agent_driven` | FR-5 Agent-authored summary flow via `SummaryStore` | pass |

Whole suite: **36 tests green** (including Hypothesis PBT). Code generation for
U5 is complete; no changes required.

# U5 Retrieval & Summarization — Business Logic Model

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u5-retrieval-summarization`
**Package**: `knowledge_store/retrieval/`
**Components**: C10 SnippetBuilder + TokenEstimator, C12 SummaryStore

---

## Responsibilities

U5 provides token-efficient retrieval and Agent-driven summarization support. It
holds no SQL and never calls an LLM; summary *text* is authored by the Agent
(FR-5), while this unit only extracts content-to-summarize and persists/reads it
through repositories.

1. **TokenEstimator.estimate(text)** — deterministic, model-agnostic token count
   heuristic. Empty text → 0; otherwise ≥ 1. Monotonic in input length
   (invariant, PBT-03).
2. **SnippetBuilder.build(text, token_budget)** — return the most relevant
   minimal scope not exceeding the budget, preserving line (semantic-unit)
   boundaries; falls back to a character `_hard_cut` when the first unit alone
   overflows. Returns a `SnippetResult` whose `estimated_tokens <= token_budget`
   for any `token_budget >= 1` (invariant, PBT-03).
3. **SummaryStore** — `extract_for_summary(ref_id)` returns `Content` for a
   chunk; `store_summary(chunk_id, text)` persists Agent-authored summaries via
   `SummaryRepository`; `get_summary(chunk_id)` reads them; `pending()` lists
   chunk ids (latest versions) that still lack a summary.

---

## Flow — Smart Snippet (budget-preserving)

```
build(text, budget)
   |
   +-- budget < 1 ? --> SnippetResult(text="", tokens=0, truncated=bool(text))
   |
   +-- text empty ? --> SnippetResult(text="", tokens=0, truncated=False)
   |
   v
   split text into line units (splitlines keepends)
   |
   for each unit: estimate(acc + unit) <= budget ? accumulate : break
   |
   +-- acc non-empty --> snippet = join(acc); estimate(snippet) <= budget
   |
   +-- acc empty ----> SnippetBuilder._hard_cut(text, budget)  (char shrink to fit)
   |
   v
   SnippetResult(status=OK, text, estimated_tokens, token_budget, truncated)
```

## Flow — Agent-driven Summarization (FR-5)

```
Agent --> get_content_to_summarize(ref_id) --> SummaryStore.extract_for_summary
                                                    |
                                          ChunkRepository.get(ref_id) -> Content
Agent authors summary text (LLM on the AGENT side, never the server)
Agent --> store_summary(chunk_id, text) --> SummaryStore.store_summary
                                                    |
                                          SummaryRepository.put(chunk_id, text)
SummaryStore.pending() = latest chunk ids  -  chunk ids already summarized
```

---

## Key names (as implemented)

- `TokenEstimator.estimate`, `TokenEstimator.CHARS_PER_TOKEN`
- `SnippetBuilder.build`, `SnippetBuilder._hard_cut`
- `SummaryStore.extract_for_summary`, `.store_summary`, `.get_summary`, `.pending`

All operations return typed results (`SnippetResult`, `Content`, `Summary`,
`Status`) — no exceptions for expected outcomes (App Design Q7).

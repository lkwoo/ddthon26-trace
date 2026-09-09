# U5 Retrieval & Summarization — Business Rules

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u5-retrieval-summarization`

Rules are enumerated as implemented in `retrieval/tokens.py`, `snippet.py`,
`summary_store.py`. Traceability: FR-5, FR-6.2, NFR-1.2, US-5.1, US-5.2, US-6.3,
US-9.3.

---

## Token estimation

- **R5-1** Empty text estimates exactly **0** tokens; any non-empty text
  estimates **≥ 1** token. (`TokenEstimator.estimate`)
- **R5-2 (INVARIANT, PBT-03)** `estimate` is **monotonic** under append: for any
  `a`, `extra`, `estimate(a) <= estimate(a + extra)`; equivalently a prefix never
  estimates more than the whole. Enforced by `tests/retrieval/test_tokens_pbt.py`.
- **R5-3** `estimate` is **deterministic** — same input yields same output; no
  state, randomness, or I/O. Heuristic blends word/punctuation count with a
  char-density estimate (`CHARS_PER_TOKEN = 4`) and takes the larger, so the
  budget is never under-counted (conservative). (NFR-1.2)

## Smart snippet

- **R5-4 (INVARIANT, PBT-03)** For any text and any `token_budget >= 1`, the
  returned `SnippetResult.estimated_tokens <= token_budget`. Enforced by
  `tests/retrieval/test_snippet_pbt.py`. (US-6.3, NFR-1.2)
- **R5-5** The snippet **preserves line (semantic-unit) boundaries** where
  possible: units are accumulated via `text.splitlines(keepends=True)` while the
  running estimate stays within budget.
- **R5-6** When even the first unit exceeds the budget, `_hard_cut` performs a
  character-level shrink until the estimate fits (guaranteed to fit; empty text
  fits any budget). This is the only path that breaks a line boundary.
- **R5-7** `token_budget < 1` yields an empty snippet (`text=""`, `tokens=0`);
  `truncated` reflects whether source text existed. Empty source text yields an
  empty, non-truncated snippet.
- **R5-8** `truncated` is `True` whenever the returned snippet is shorter than
  the source (`len(snippet) < len(text)`) or a hard-cut occurred.

## Agent-driven summarization

- **R5-9 (FR-5, US-5.1)** The server **never generates summary text**. `Content`
  returned by `extract_for_summary` is the raw material the Agent summarizes; no
  LLM is invoked server-side (NFR-3.1).
- **R5-10 (US-5.2)** `store_summary` persists an **Agent-authored** summary only
  if the target chunk exists; otherwise returns `Status.NOT_FOUND`. Persistence
  is delegated to `SummaryRepository` (no direct SQL).
- **R5-11 (US-5.2)** `get_summary(chunk_id)` returns the stored `Summary` or
  `None`; `extract_for_summary` returns `None` for an unknown chunk.
- **R5-12** `pending()` lists **latest-version** chunk ids lacking a summary,
  computed as `all_latest()` minus already-summarized ids.

## Extension compliance (PBT Partial ON)

- PBT-03 monotonicity (R5-2) and the budget invariant (R5-4) are **enforced**
  targets with property-based tests. Security / Resiliency extensions: **N/A**
  (local, offline, LLM-free unit; no auth/network/failure-injection surface).

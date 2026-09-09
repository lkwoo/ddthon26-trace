# U5 Retrieval & Summarization — Logical Components

**Stage**: CONSTRUCTION → NFR Design
**Unit**: `u5-retrieval-summarization`

Concrete classes mapped to `components.md` (C10, C12) and `services.md`.

---

| Class (file) | Component | Role (one line) |
|---|---|---|
| `TokenEstimator` (`retrieval/tokens.py`) | C10 (TokenEstimator) | Deterministic, monotonic token-count heuristic; no state, no I/O. |
| `SnippetBuilder` (`retrieval/snippet.py`) | C10 (SnippetBuilder) | Budget-aware, boundary-preserving scope cutter producing `SnippetResult`. |
| `SnippetBuilder._hard_cut` | C10 | Character-level shrink fallback guaranteeing the snippet fits the budget. |
| `SummaryStore` (`retrieval/summary_store.py`) | C12 (SummaryStore) | Extract content-to-summarize, persist/read Agent-authored summaries, list pending. |

## Collaborators (outside U5)
| Collaborator | Direction | Purpose |
|---|---|---|
| `Repositories.chunks` (U1) | downward | read chunk text/kind; `all_latest`, `get`, `by_source`. |
| `Repositories.summaries` (U1) | downward | `put` / `get` / `all` Agent-authored summaries. |
| `QueryService.smart_snippet` (U6) | inbound | resolves chunk then calls `SnippetBuilder.build`. |
| `SummarizationService` (U6) | inbound | wraps `SummaryStore` operations for MCP tools. |
| `KnowledgeSystem` (U6) | assembly | constructs `TokenEstimator`, `SnippetBuilder`, `SummaryStore`. |

All calls are **downward-only** (services → U5 helpers → repositories); U5 has
no peer or upward coupling.

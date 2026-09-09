# U5 Retrieval & Summarization — Domain Entities

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u5-retrieval-summarization`

Entities are the shared typed contracts from `knowledge_store/types/results.py`
consumed/produced by U5 (App Design Q7). U5 defines no new persisted schema; it
reads chunks and writes summaries via repositories.

---

## Entities

### SnippetResult (produced by SnippetBuilder.build)
| Field | Type | Notes |
|---|---|---|
| `status` | `Status` | always `OK` from `build` (or `NOT_FOUND` upstream in QueryService) |
| `text` | `str` | budget-preserving snippet (line-bounded or hard-cut) |
| `estimated_tokens` | `int` | `<= token_budget` for `budget >= 1` (invariant) |
| `token_budget` | `int` | requested budget |
| `truncated` | `bool` | snippet shorter than source / hard-cut occurred |

### Content (produced by SummaryStore.extract_for_summary)
| Field | Type | Notes |
|---|---|---|
| `ref_id` | `str` | chunk id to summarize (US-5.1) |
| `text` | `str` | raw content the Agent summarizes |
| `kind` | `str` | chunk kind (paragraph/section/code/…) |

### Summary (stored/read via SummaryStore)
| Field | Type | Notes |
|---|---|---|
| `chunk_id` | `str` | links Agent-authored summary to a chunk (US-5.2) |
| `text` | `str` | Agent-authored summary text (never server-generated) |

### Consumed contracts
- **Chunk** — read-only via `ChunkRepository.get` / `all_latest`; supplies
  `id`, `text`, `kind` for `Content` and `pending()`.
- **Status** — explicit outcome enum (`OK`, `NOT_FOUND`, …).

---

## Testable Properties (PBT-01)

| ID | Property | Entity/op | Status |
|---|---|---|---|
| **PBT-03** | `estimate` monotonic under append; prefix ≤ whole | `TokenEstimator.estimate` | **Enforced** — `tests/retrieval/test_tokens_pbt.py` |
| **PBT-03** | `estimated_tokens <= token_budget` for budget ≥ 1 | `SnippetBuilder.build` → `SnippetResult` | **Enforced** — `tests/retrieval/test_snippet_pbt.py` |
| PBT (adv.) | `estimate` deterministic (same in → same out) | `TokenEstimator.estimate` | Advisory (asserted in tokens PBT) |
| PBT (adv.) | non-empty text ⇒ estimate ≥ 1; empty ⇒ 0 | `TokenEstimator.estimate` | Advisory |
| PBT (adv.) | snippet length ≤ source length; budget 0 ⇒ empty | `SnippetBuilder.build` | Advisory |
| PBT (adv.) | `store_summary` idempotent-safe; `NOT_FOUND` for unknown chunk | `SummaryStore` | Advisory |

Enforced targets align with **PBT Partial ON** (PBT-02/03/07/08/09). Security /
Resiliency properties: **N/A** for this unit.

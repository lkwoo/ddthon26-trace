# U5 Retrieval & Summarization — NFR Design Patterns

**Stage**: CONSTRUCTION → NFR Design
**Unit**: `u5-retrieval-summarization`

---

## Patterns applied

### 1. Injected estimator (strategy / testability)
`SnippetBuilder(estimator: TokenEstimator | None = None)` accepts an estimator,
defaulting to a fresh `TokenEstimator`. This decouples budget arithmetic from
the cutting algorithm and lets PBT swap or reuse the estimator directly.

### 2. Conservative upper-bound heuristic (token efficiency — NFR-1.2)
`estimate = max(1, word_pieces, char_density)`. Never under-counts, so the
budget invariant holds even for adversarial inputs. Determinism + monotonicity
make the invariant provable and PBT-checkable (PBT-03).

### 3. Boundary-preserving accumulation with safe fallback
`build` accumulates whole line units while within budget (semantic preservation)
and only drops to `_hard_cut` character shrinking when the first unit alone
overflows — guaranteeing a fitting result for any `budget >= 1`.

### 4. Typed result envelopes (App Design Q7)
Every operation returns a dataclass (`SnippetResult`, `Content`, `Summary`) with
an explicit `Status` instead of raising for expected outcomes (empty text,
zero budget, unknown chunk). These serialize cleanly into U6's token-efficient
`ToolResult`.

### 5. Repository delegation (LLM-free, SQL-free — NFR-3.1 / Q4)
`SummaryStore` holds `Repositories` and delegates all persistence
(`chunks.get`, `summaries.put/get/all`, `chunks.all_latest`). No SQL and no LLM
calls originate in U5; summary text is Agent-authored (FR-5).

---

## Invariant enforcement (PBT Partial ON)

| Invariant | Design mechanism | Test |
|---|---|---|
| `estimate` monotonic (PBT-03) | conservative `max`-based heuristic, no state | `tests/retrieval/test_tokens_pbt.py` |
| `estimated_tokens <= budget`, budget ≥ 1 (PBT-03) | budget-gated accumulation + guaranteed `_hard_cut` | `tests/retrieval/test_snippet_pbt.py` |

Security / Resiliency design patterns: **N/A** (no network, auth, or failure
surfaces in this unit).

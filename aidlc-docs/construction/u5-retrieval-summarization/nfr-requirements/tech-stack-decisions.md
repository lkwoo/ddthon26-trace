# U5 Retrieval & Summarization — Tech Stack Decisions

**Stage**: CONSTRUCTION → NFR Requirements
**Unit**: `u5-retrieval-summarization`

---

## Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Token estimation | **Pure-Python deterministic heuristic** (`re` word/punct split + char-density, `CHARS_PER_TOKEN = 4`, take max) | No model download, no network (NFR-3.1); deterministic and monotonic (PBT-03); model-agnostic so it works offline for any agent. |
| Snippet cutting | **Standard-library string ops** (`splitlines(keepends=True)`, slicing) | Preserves line/semantic boundaries; zero dependencies; O(n) in text length → meets NFR-1.1. |
| Summary persistence | **Delegated to `SummaryRepository`** (U1), no SQL here | Keeps SQL isolated (App Design Q4); U5 stays a pure logic/helper unit. |
| Summary generation | **None (Agent-authored)** | FR-5 / NFR-3.1 — the server never calls an LLM; U5 only extracts `Content` and stores `Summary` text. |
| Result types | **Shared dataclasses** from `knowledge_store.types` | Typed contracts (Q7); JSON-serializable for U6 token-efficient envelopes. |
| Testing | **Hypothesis** property-based tests (PBT-09) | Enforce monotonicity and budget invariants across generated inputs. |

## Token-budget design justification (NFR-1.2)

The estimator is deliberately **conservative** — `max(1, word_pieces,
char_estimate)` — so it never *under*-estimates. Combined with `SnippetBuilder`
accumulating line units only while `estimate(acc) <= budget` and a guaranteed
`_hard_cut` fallback, the returned `estimated_tokens` is provably `<= budget`
for `budget >= 1`. This upper-bound guarantee is what makes smart snippets safe
for an agent's remaining context window (US-6.3, US-9.3) without any external
tokenizer.

## Dependencies
- Runtime: **Python standard library only** (`re`, string ops) for U5 logic.
- Test-only: **Hypothesis** (PBT-09).
- No `mcp`, no ML/embedding libraries required by this unit.

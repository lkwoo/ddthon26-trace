# U5 Retrieval & Summarization — NFR Requirements

**Stage**: CONSTRUCTION → NFR Requirements
**Unit**: `u5-retrieval-summarization`

---

## Applicable NFRs

### NFR-1 Performance / Token Efficiency
- **NFR-1.1 (latency)** Snippet building and token estimation are pure in-memory
  operations (regex + string slicing), well within the ≤ 1 s core-tool target.
- **NFR-1.2 (token efficiency)** Central to U5: `SnippetBuilder` returns the
  minimal budget-fitting scope, never full raw dumps; `TokenEstimator` is
  intentionally **conservative** (takes the larger of word-count and
  char-density) so a budget is never under-counted and downstream token spend
  stays bounded. (US-6.3, US-9.3)

### NFR-3 Cost & Resources (LLM-free)
- **NFR-3.1** U5 makes **no external LLM / embedding / network calls**. Summaries
  are Agent-authored (FR-5); the server only extracts content and persists text.
  Token estimation is a local deterministic heuristic — no tokenizer download.

### NFR-5 Discoverability
- **NFR-5.1** U5 has no direct MCP surface, but its capabilities (smart snippet,
  content-to-summarize, store/get summary) are exposed as self-describing tools
  by U6; U5 must return typed, serializable results (`SnippetResult`, `Content`,
  `Summary`) to support that discoverability.

---

## Non-applicable NFRs

| NFR | Determination | Rationale |
|---|---|---|
| Security extension | **N/A** | Local, offline, single-process; no auth, secrets, or network I/O in this unit. |
| Resiliency extension | **N/A** | No remote dependencies to retry/circuit-break; expected outcomes returned as typed `Status`, not exceptions. |

## PBT (Partial ON — enforced)
- **PBT-03** monotonicity of `estimate` and the snippet budget invariant are
  mandatory property-based tests for this unit (see `nfr-design`).

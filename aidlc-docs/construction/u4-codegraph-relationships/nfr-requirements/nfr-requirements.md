# U4 Code Structure & Relationships — NFR Requirements

Applicable NFRs for this unit. Security and Resiliency baselines are **OFF** →
marked N/A.

| NFR | Requirement | Applies to U4 | How U4 satisfies it |
|---|---|---|---|
| **NFR-1** Performance | Core reads ≤1s; token efficiency | Yes | In-process regex parsing + in-memory resolution; typed `GraphResult`/`Relationship` envelopes are compact. |
| **NFR-3.1** Cost/Resources | No external LLM/embedding/network API | Yes | Deterministic, LLM-free extraction; embedding strategy uses the *local* `SearchEngine`/`EmbeddingProvider` only. |
| **NFR-4** Installability | Minimal prerequisites; graceful degradation | Yes | tree-sitter optional — regex fallback guarantees analysis with stdlib `re` only. |
| **NFR-8.2** Testing (PBT) | Determinism of pure analysis | Yes (determinism) | `analyze` proven deterministic across runs; enforced round-trip/hash PBT live in U3. |
| **NFR-2.1** Data consistency | Structure reflects source; re-index resolves drift | Yes | Graph is a pure function of source; re-running after refactor re-syncs. |

## Extension compliance summary

| Extension | Status | Notes |
|---|---|---|
| Property-Based Testing (Partial) | Compliant | Determinism property covered; PBT-02/03 enforced targets belong to U3. |
| Security Baseline | N/A | Extension OFF; local/offline, no auth/network surface. |
| Resiliency Baseline | N/A | Extension OFF; unresolved refs handled by typed status, no distributed concerns. |

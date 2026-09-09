# U3 Ingestion & Chunking — NFR Requirements

Applicable NFRs for this unit. Security and Resiliency baselines are **OFF** →
marked N/A.

| NFR | Requirement | Applies to U3 | How U3 satisfies it |
|---|---|---|---|
| **NFR-1** Performance | Core reads ≤1s; token efficiency (NFR-1.2) | Yes | Pure in-process regex/JSON/hash work; typed results serialize to compact envelopes, no full-dump. |
| **NFR-3.1** Cost/Resources | No external LLM/embedding/network API | Yes | Extraction, chunking and MinHash versioning are entirely local, offline, LLM-free. |
| **NFR-4** Installability | Minimal prerequisites; graceful degradation | Yes | csv via stdlib; PDF/xlsx parsers optional — absence yields `Status.ERROR`, not a failed install. |
| **NFR-8.2** Testing (PBT) | Round-trip + hash-matching purity under PBT | Yes | Chunker serialize/deserialize round-trip (PBT-02) and MinHash determinism (PBT-03) enforced via Hypothesis. |
| **NFR-2.2** Data consistency | Version matching accuracy depends on similarity/hash | Yes | Deterministic threshold matching (default 0.6) over MinHash Jaccard estimate. |

## Extension compliance summary

| Extension | Status | Notes |
|---|---|---|
| Property-Based Testing (Partial) | Compliant | PBT-02/03/07/08/09 targets met (see code-summary). |
| Security Baseline | N/A | Extension OFF; unit is local, offline, no auth/network surface. |
| Resiliency Baseline | N/A | Extension OFF; no distributed/retry/timeout concerns in-process. |

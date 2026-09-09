# U3 Ingestion & Chunking — NFR Design Patterns

## Pluggable Extractor Registry (App Design Q5)

`ExtractorRegistry` holds an ordered list of objects satisfying the `Extractor`
Protocol (`supports`, `extract`). `resolve()` returns the first supporter;
`register()` allows adding formats without touching the registry. New formats are
opt-in via `default_registry()` ordering — no conditional branching in callers.
Supports NFR-4 (extensible install) and US-1.1 (unsupported handled by absence of
a supporter, returning a typed status).

## Graceful optional-dependency degradation

Heavy parsers (`pypdf`, `openpyxl`) are imported lazily *inside* `extract()`
behind `try/except`, returning `Status.ERROR` with an install hint when missing.
Core install stays minimal; the pipeline never crashes on an absent optional dep
(NFR-4, NFR-3.1). Same principle governs U4's tree-sitter/regex fallback.

## Deterministic pure-function design (enables PBT)

- Extraction, tag detection, chunking, MinHash signatures and Jaccard estimation
  are **pure functions** of their inputs — no clocks, no randomness, no I/O.
- `Chunk.id` and `serialize` are stable (`sort_keys=True`), so the round-trip
  property (PBT-02) and signature determinism (PBT-03) hold for arbitrary inputs.
- Only `ChunkVersioner.apply_version` performs I/O, and only through
  `ChunkRepository` — matching (`match`) stays pure and repo-free (see
  `test_identical_chunks_match` constructing the versioner with `chunk_repo=None`).

## Typed-result / no-exception control flow (App Design Q7)

Expected outcomes (unsupported format, missing parser, no version match) are
represented by `Status` enum values on typed results, not exceptions — keeping
the ingestion loop resilient and each step independently testable.

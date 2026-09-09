# U-Eval — Functional & NFR Design (Increment 2, item 5)

**Purpose**: Make retrieval quality *measurable* so the later chunking/hybrid work can be proven, and
guard against regressions.

## Business Logic Model
- **EvalQuestion**: `id`, `intent`, `gold_files` (file-level labels now), forward-compatible optional
  `gold_symbols`/`gold_lines` (unused until U-Chunking), `note`.
- **EvalDataset**: named set of questions + optional `corpus` hints; JSON load/save with lossless
  round-trip.
- **Retriever** (common shape `intent -> ranked, de-duplicated file paths`):
  - **SemanticRetriever**: wraps `QueryService.semantic_query`, requests a pool of chunk hits, maps each
    hit's `ref_id → chunk.source_path` via `ChunkRepository.get`, normalizes to corpus-relative paths,
    de-dups preserving rank.
  - **GrepRetriever**: keyword baseline; ranks files by query content-token frequency (stopword-filtered),
    drops zero-match files, deterministic tie-break by (−score, path).
- **Harness**: build in-memory `KnowledgeSystem` → enforce provider policy → ingest corpus → run both
  retrievers over every question → per-query `EvalScore` → aggregate mean recall@1/5/10 + MRR@10 per method.

## Business Rules
- **BR-1 (provider policy, Q5=A)**: If the embedding provider is the hash fallback (not the learned
  model) and `allow_hash` is not set, raise `ProviderPolicyError` — eval numbers must reflect the real
  model. `--allow-hash` overrides for environments without `fastembed`.
- **BR-2 (file granularity, Q2=C)**: A chunk hit counts for its `source_path`; the ranked chunk list is
  reduced to a ranked unique-file list before scoring. Gold is file-level now; schema is upgrade-ready.
- **BR-3 (empty gold)**: vacuously satisfied (recall 1.0, RR 1.0) to keep aggregates well-defined.
- **BR-4 (A/B, Q4=A)**: semantic and grep are scored identically and compared head-to-head on MRR@10.

## Testable Properties (PBT Partial — pure functions + serialization)
- recall@k ∈ [0,1]; monotonic non-decreasing in k; full-window recall = fraction of gold present.
- reciprocal_rank ∈ [0,1] and ∈ {0} ∪ {1/n}; top-1-relevant ⇒ 1.0.
- MRR ∈ [0,1]. EvalDataset JSON round-trip is lossless.

## NFR Notes
- **Offline/LLM-free** preserved: no new required deps; runs on hash fallback with `--allow-hash`.
- **Determinism**: hash provider + fixed dataset make fixture results deterministic → stable regression.
- **No SQL outside repositories**: harness reads only through `QueryService` / `ChunkRepository`.

## Recorded Baseline (hash provider, `--allow-hash`; NOT the learned model)
| Corpus | Method | recall@1 | recall@5 | recall@10 | MRR@10 |
|---|---|---|---|---|---|
| fixture (11 files, 5 q) | semantic | 1.000 | 1.000 | 1.000 | 1.000 |
| fixture | grep | 1.000 | 1.000 | 1.000 | 1.000 |
| repo (32 files, 18 q) | semantic | 0.500 | 0.778 | 0.833 | 0.621 |
| repo | grep | 0.556 | 0.889 | 1.000 | 0.706 |

**Key finding**: on the repo dogfood set, the **grep baseline beats pure vector search on every
metric** — the quantitative confirmation that pure semantic loses to keyword on code, and the
motivation for U-Chunking (item 1) and U-Hybrid (item 2). (Numbers are on the hash fallback; a learned
model run via `python -m eval` will differ, but the harness is the fixed measuring stick either way.)

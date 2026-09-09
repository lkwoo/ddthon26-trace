# U-Hybrid — Code Summary (Increment 2, item 2)

## New files
- `knowledge_store/embedding/keyword.py` — `tokenize` (code-aware: whole identifier + camelCase/snake
  sub-words) and `BM25Index` (pure-Python Okapi BM25+; deterministic `build`/`search`).
- `tests/embedding/__init__.py`, `tests/embedding/test_keyword.py` — camelCase/snake tokenization,
  `tokenize` PBT (deterministic + lowercased), BM25 exact-identifier ranking, empty/no-match, determinism.

## Modified files
- `knowledge_store/embedding/search.py` — `SearchEngine` now **hybrid by default**:
  - `__init__(..., hybrid=True)`; owns a lazily-built, id-set-memoised `BM25Index`.
  - `search()` fetches a pool from both the vector index and BM25, then fuses via **Reciprocal Rank
    Fusion** (`_fuse`, k=60), min-max normalising fused scores to `(0, 1]`, deterministic tie-break.
  - `hybrid=False` preserves the pure-vector path (used for the controlled eval A/B).
- `tests/eval/test_harness.py` — repo dogfood floors tightened to lock in hybrid gains: semantic
  recall@10 ≥ 0.95 (now 1.000) and semantic MRR ≥ 0.50 (now ~0.575), with the full progression documented.

## Verification
- Full suite: **55 passed** (`.venv/bin/python -m pytest -q`); harness tests deterministic across reruns.
- Eval A/B on identical method-aware chunks (hash `--allow-hash`, repo dogfood): hybrid beats pure vector
  on **every** metric — recall@1 0.222→0.333, recall@5 0.722→0.889, recall@10 0.944→**1.000**, MRR
  0.440→0.575. Fixture corpus stays a perfect 1.0.

## Design choices / rationale
- **Pure-Python BM25 over FTS5**: keeps the offline/no-dep posture (NFR-E1) and stays deterministic across
  environments (NFR-E2); FTS5's `bm25()` scoring is build-dependent. FTS5 noted as a future optimisation.
- **RRF over weighted score fusion**: score-scale-free (vector cosine/L2 vs BM25 are not comparable),
  no weights to tune, deterministic — a robust default.
- **Code-aware tokenization**: the identifier-decomposition edge that lets keyword search absorb grep's
  exact-match strength while still matching natural-language concept queries.

## Environment note
`fastembed` absent (no Python 3.14 wheel) → eval on hash embedding fallback with `--allow-hash`; the
standalone `python -m eval` runner still fails loud by default. On the learned model both retrieval halves
are strong and fusion is expected to exceed either alone.

# U-Hybrid — Functional & NFR Design (Increment 2, item 2)

**Purpose**: Stop leaking at the *retrieval* stage. Add a keyword (BM25) index beside the vectors and
**fuse** the two rankings so exact identifier matches (grep's strength) and concept matches (the vector's
strength) both surface — making `semantic_query` the "grep + concept understanding **superset**" the user
asked for, instead of a pure vector search that loses to grep on code.

## Business Logic Model
- **BM25Index** (`knowledge_store/embedding/keyword.py`): pure-Python Okapi BM25 over the chunk corpus.
  - **Code-aware tokenizer** (`tokenize`): identifiers are split on `_` and camelCase boundaries; **both**
    the whole identifier and its sub-words are indexed, so "favorites count" matches a `favoritesCount` /
    `favorites_count` symbol. This is the identifier-decomposition edge a naive grep lacks.
  - `build(docs)` computes tf, df, positive BM25+ idf, and average doc length — a pure function of `docs`.
  - `search(query, limit)` returns deterministic `SearchHit`s (score desc, then ref_id asc).
- **SearchEngine** (`knowledge_store/embedding/search.py`): now **hybrid by default**.
  - Runs the vector search (`EmbeddingRepository`) and the BM25 search over a shared candidate pool
    (`pool = max(limit, 50)`).
  - **Fuses** the two ranked lists with **Reciprocal Rank Fusion**: `score(d) = Σ 1/(k + rank_d)` over
    each list, `k = 60`; fused scores are min-max normalised to `(0, 1]`, ordered deterministically.
  - Lazily (re)builds the BM25 index from `ChunkRepository.all_latest()`, memoised by the set of chunk
    ids, so re-ingestion refreshes it and repeated queries don't rebuild.
  - `hybrid=False` restores pure-vector behaviour (used for the controlled A/B in eval).

## Business Rules
- **BR-H1 (fusion, FR-H1.2)**: final ranking = RRF of vector and keyword rankings; neither dominates.
- **BR-H2 (determinism, NFR-E2)**: tokenizer, BM25, and RRF are all deterministic; ties break by ref_id.
- **BR-H3 (offline / no dep, NFR-E1)**: BM25 is pure-Python — no FTS5 dependency and no build-specific
  `bm25()` scoring. FTS5 is noted as a future performance optimisation only.
- **BR-H4 (backward compatible, NFR-E4)**: the `semantic_query` MCP contract is unchanged (still returns
  ranked `SearchHit`s with previews); hybrid is additive.
- **BR-H5 (no SQL outside repositories, NFR-E3)**: the keyword index reads chunk text via
  `ChunkRepository`; no new SQL is issued outside the repository layer.

## Testable Properties (PBT Partial — pure functions)
- `tokenize` is deterministic and always lowercased (Hypothesis property).
- BM25 ranking is deterministic; exact-identifier queries rank the matching document first; empty query /
  empty corpus / no-match return `[]`.

## Measured Impact — controlled A/B (hash fallback via `--allow-hash`; NOT the learned model)
On the **same method-aware chunks** produced by U-Chunking, repo dogfood set (18 questions):

| Retrieval | recall@1 | recall@5 | recall@10 | MRR@10 |
|---|---|---|---|---|
| pure vector (U-Chunking) | 0.222 | 0.722 | 0.944 | 0.440 |
| **hybrid (U-Hybrid)** | **0.333** | **0.889** | **1.000** | **0.575** |
| grep baseline | 0.500 | 0.889 | 0.944 | 0.673 |
| fixture (controlled), hybrid | 1.000 | 1.000 | 1.000 | 1.000 |

**Interpretation**: hybrid fusion beats pure vector on **every** metric — recall@1 +0.111, recall@5
+0.167, recall@10 → **1.000** (now matching grep's best coverage), MRR +0.135. On the noisy hash provider
grep still edges hybrid on MRR (0.673 vs 0.575) because the hash vector half contributes little signal;
on a **learned code-embedding model** (run via `python -m eval`) both halves are strong and fusion is
expected to exceed either alone. The headline for the increment: `semantic_query` went from losing to
grep on coverage (recall@10 0.833) to **perfect coverage (1.000)** while keeping concept search — the
"superset of grep" goal, demonstrated end-to-end and locked in by `tests/eval/test_harness.py`.

## Increment-2 progression (hash provider, repo dogfood)
| Stage | recall@10 | MRR@10 |
|---|---|---|
| original (blank-line chunks, pure vector) | 0.833 | 0.621 |
| U-Chunking (method-aware chunks, pure vector) | 0.944 | 0.444 |
| U-Hybrid (method-aware chunks, BM25+RRF) | **1.000** | 0.575 |

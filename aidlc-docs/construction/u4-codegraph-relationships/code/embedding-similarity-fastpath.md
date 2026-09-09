# Change Note — Faster `EmbeddingSimilarityStrategy` (reuse stored vectors)

**Increment**: 4 · **Units touched**: u2-embedding-search, u4-codegraph-relationships
**Branch**: shortFix1 · **Depth**: targeted performance optimization (auto-adopt)
**User request**: "EmbeddingSimilarityStrategy이 더 빠르게 동작하도록 하는 방법은? 너무 오래 걸려서 해당 테스트는 제외하고 싶어."
**Scope confirmed (AskUserQuestion)**: **optimize the strategy** (not exclude the test). Making it fast removed the need to skip any test.

## Problem

`EmbeddingSimilarityStrategy.build()` called `SearchEngine.search(chunk.text, …)`
**once per chunk**. Each call re-did work that was pure overhead for relationship
building:

1. **Re-embedded the chunk text** — even though the pipeline (`services.py:91`) has
   *already* embedded and indexed every latest chunk (`index_many([(c.id, c.text) …])`)
   immediately before calling `relationship_builder.build(latest)` at `:92`.
2. Ran the **full hybrid intent path** — BM25 keyword index (re)build + Reciprocal Rank
   Fusion — whose keyword signal has no place in an *embedding-similarity* edge.
3. Attached a **preview** (`chunks.get()`) per hit, unused by relationships.
4. Forced `pool = max(limit, 50)`, so the vector scan considered 50 candidates per chunk.

On the no-`sqlite-vec` fallback the vector scan is a brute-force cosine over all stored
vectors, so the whole strategy was effectively **O(N²)** plus N redundant embeddings —
the ingestion-time bottleneck already flagged in `tag-enrichment.md` (line 78).

## Change 1 — `EmbeddingRepository.get_vector` (new: `store/repositories.py`)

`get_vector(ref_id) -> Optional[list[float]]` returns a chunk's already-persisted
embedding (handles both the `sqlite-vec` table and the brute-force fallback table),
so callers can reuse the indexed vector instead of re-embedding the source text.

## Change 2 — `SearchEngine.neighbors_of` (new: `embedding/search.py`)

```python
def neighbors_of(self, ref_id: str, limit: int = 5) -> list[SearchHit]:
```

A fast path for relationship building: looks up the item's stored vector via
`get_vector` and returns **pure-vector** nearest neighbours (`embeddings.search`),
**skipping** BM25 fusion and preview attachment. Returns `[]` if the item was never
indexed. Deterministic (vector rank order).

`SearchEngine.search()` (the free-text `semantic_query` path) is **unchanged** — the
hybrid RRF behaviour and its eval floors stay exactly as before.

## Change 3 — `EmbeddingSimilarityStrategy.build` (`codegraph/relationships.py`)

`self._search.search(chunk.text, limit=top_k+1)` → `self._search.neighbors_of(chunk.id,
limit=top_k+1)`. Per chunk this drops one query embedding, the BM25 index check, and one
`chunks.get()` per hit, and narrows the candidate pool from 50 to `top_k+1`.

## Behaviour change (intended)

The emitted `RelationType.EMBEDDING` edge `score` is now the **pure vector similarity**
(cosine, or `1/(1+distance)` under `sqlite-vec`) rather than the RRF-fused, min-max
normalised score `search()` returned. For an "embedding similarity" relation this is the
more faithful signal — the BM25 keyword term never belonged in it. Consequently the exact
set of edges clearing `min_score = 0.3` and the stored `score` values may shift. The
`semantic_query` retrieval quality (the eval target) is **not** affected, since `search()`
is untouched.

## Tests / verification

- `tests/services/test_pipeline.py` + `tests/codegraph/` — **14 pass**.
- Full suite — **65 passed, 1 skipped** (skip = learned-model policy gate, unrelated).
- fixture eval (`semantic_query`) — recall@{1,5,10} and MRR@10 all **1.000** (unchanged;
  `search()` untouched).

Run tests with `.venv/bin/python -m pytest`. Note: `fastembed` is not installed in this
env, so the win here is mostly the removed brute-force re-scans + redundant embeds; with a
learned model installed, eliminating N per-chunk embeddings is the larger saving.

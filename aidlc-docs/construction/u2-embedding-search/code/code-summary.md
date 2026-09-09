# U2 Embedding & Semantic Search — Code Summary

**Status**: Code generation complete. Full suite passes (36 tests).

## Files

| File | Scale | Description |
|---|---|---|
| `knowledge_store/embedding/provider.py` | ~120 LOC | `EmbeddingProvider` protocol; `HashingEmbeddingProvider` (deterministic offline); `LocalEmbeddingProvider` (fastembed + fallback); `get_default_provider` singleton; `_tokenize` helper. |
| `knowledge_store/embedding/search.py` | ~49 LOC | `SearchEngine`: `index`, `index_many`, `search` (embed -> repo search -> preview enrichment). |
| `knowledge_store/embedding/__init__.py` | ~22 LOC | Public exports for U2. |

## Key public classes / methods
- `EmbeddingProvider` (Protocol): `dimension`, `embed(texts) -> list[list[float]]`.
- `HashingEmbeddingProvider(dimension=256)`: deterministic, L2-normalized vectors.
- `LocalEmbeddingProvider(model_name="BAAI/bge-small-en-v1.5")`: `is_learned`,
  `dimension`, `embed`; graceful fastembed fallback.
- `get_default_provider() -> EmbeddingProvider`.
- `SearchEngine(repos, provider=None)`: `index(ref_id, text, kind)`,
  `index_many(items, kind) -> int`, `search(intent, limit) -> list[SearchHit]`.

## Tests exercising this unit
U2 has no isolated embedding test module; it is exercised through the pipeline's
`semantic_query`:
- `tests/services/test_pipeline.py::test_full_ingest_and_query` — ingestion
  indexes vectors via `SearchEngine`, then `QueryService.semantic_query(...)`
  runs embed + ranked search and returns `SearchHit`s.
- `tests/services/test_pipeline.py::test_reingest_bumps_version_not_duplicate`
  — relies on deterministic hashing embeddings so identical content matches.
- `tests/mcp/test_tools.py` — semantic query tool over the search path.

The default (offline) test run uses `HashingEmbeddingProvider`, whose determinism
keeps these results reproducible. The full test suite (36 tests) passes.

# U1 Storage Foundation — Code Summary

**Status**: Code generation complete. Full suite passes (36 tests).

## Files

| File | Scale | Description |
|---|---|---|
| `knowledge_store/store/schema.py` | ~95 LOC | Centralized versioned DDL. `SCHEMA_VERSION`, `CORE_DDL` (meta, chunks, chunk_versions, graph_nodes, graph_edges, relationships, summaries + indexes), `FALLBACK_EMBEDDING_DDL`, `vec_embedding_ddl(dimension)`. |
| `knowledge_store/store/store.py` | ~99 LOC | `KnowledgeStore`: connection lifecycle, `_try_load_vec`, `vec_enabled`, `init_schema`, `reindex`, `close`, context manager. |
| `knowledge_store/store/repositories.py` | ~274 LOC | `_pack`/`_unpack`/`_cosine` helpers; `ChunkRepository`, `GraphRepository`, `RelationshipRepository`, `EmbeddingRepository`, `SummaryRepository`; `Repositories` aggregate. |
| `knowledge_store/store/__init__.py` | ~27 LOC | Public exports for U1. |
| `knowledge_store/types/results.py` | ~276 LOC | Shared typed dataclasses + enums consumed by the repositories. |

## Key public classes / methods
- `KnowledgeStore(target_dir, in_memory=False)` — `connect()`, `init_schema(embedding_dimension=None)`, `reindex()`, `close()`, `vec_enabled`.
- `Repositories(store)` — `.chunks`, `.graph`, `.relationships`, `.embeddings`, `.summaries`.
- `ChunkRepository`: `upsert_new_version`, `get`, `latest_version`, `history`, `all_latest`, `by_source`.
- `EmbeddingRepository`: `upsert`, `search`, `count` (vec0 vs. cosine fallback).
- `GraphRepository`, `RelationshipRepository`, `SummaryRepository`: typed CRUD.

## Tests exercising this unit
U1 has no isolated store test module; it is exercised end-to-end through the
repositories via `tests/services/test_pipeline.py`:
- `test_full_ingest_and_query` — chunk upsert + version rows + graph nodes/edges
  + embedding upsert/search read back correctly.
- `test_reingest_bumps_version_not_duplicate` — validates single-latest-version
  invariant and history preservation (`upsert_new_version`).
- `test_unsupported_and_missing_files_are_reported` — typed-status persistence path.
- `test_summarization_is_agent_driven` — `SummaryRepository` put/get.
Additional coverage via `tests/mcp/test_tools.py` (embedding/search read path).

The full test suite (36 tests) passes.

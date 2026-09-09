# U1 Storage Foundation — Business Rules

Rules the code enforces, with FR/NFR/US references. Source of truth:
`knowledge_store/store/*.py`, `knowledge_store/types/results.py`.

## BR-U1-1 — All SQL is centralized in repositories (FR-6.1, App Design Q4)
Every SQL statement lives in `repositories.py`. No other component or unit
touches the `sqlite3.Connection`; they receive a `Repositories` aggregate and
call typed methods. `KnowledgeStore` exposes only `connect()`/`init_schema()`/
`reindex()`/`close()`, not query surface.

## BR-U1-2 — Typed results, not exceptions, for expected outcomes (App Design Q7)
Reads return typed domain objects (`Chunk`, `GraphNode`, `GraphEdge`,
`Relationship`, `Summary`, `SearchHit`) or `None` for not-found (e.g.
`ChunkRepository.get`, `SummaryRepository.get`). Absence is a normal value, not
an error. Enum fields (`EdgeType`, `RelationType`) round-trip through their
`.value` string on write and are reconstructed on read.

## BR-U1-3 — Schema is versioned and centralized (FR-8.2, US-8.2)
`schema.SCHEMA_VERSION = 1` is the single source of DDL. `init_schema()` writes
`INSERT OR REPLACE INTO meta('schema_version', ...)`, giving a migration anchor.
All DDL uses `CREATE TABLE IF NOT EXISTS`, so `init_schema()` is idempotent and
safe to call on an existing store.

## BR-U1-4 — Chunk identity + version history preserved (FR-1.3, FR-4, US-4.2, NFR-2.1)
`chunks` holds latest metadata + `latest_version`; full history lives in
`chunk_versions`. `upsert_new_version()` sets all prior version rows
`is_latest=0` before inserting the new row with `is_latest=1`, so exactly one
latest version exists per chunk and older versions are retained (reviewers see
latest, NFR-2.1). `ON DELETE CASCADE` keeps history consistent with identity.

## BR-U1-5 — Float32 packing for vectors (FR-3.1, FR-6.2)
Vectors persist as little-endian packed float32 via
`_pack = struct.pack("<{n}f", ...)` and are read back with `_unpack`. The
fallback `embeddings` table stores `dimension` alongside the BLOB so decoding is
self-describing.

## BR-U1-6 — Cosine fallback when sqlite-vec is absent (NFR-3.1, NFR-4)
`EmbeddingRepository` branches on `store.vec_enabled`. With vec: insert into the
`vec0` virtual table and query via `embedding MATCH ? ORDER BY distance`,
converting L2 distance to a descending similarity `1/(1+distance)`. Without vec:
brute-force `_cosine` over all stored BLOBs, sorted by score descending, sliced
to `limit`. Both paths return `list[SearchHit]` — callers are agnostic.

## BR-U1-7 — Foreign keys and single-connection ownership
`connect()` enables `PRAGMA foreign_keys = ON` and memoizes one connection per
store instance (`self._conn`). `_try_load_vec` degrades silently (returns False)
on any import/load failure, so a missing extension never aborts startup (NFR-4).

## BR-U1-8 — reindex() rebuilds indexes/statistics (US-8.4, NFR-2.1)
`reindex()` runs `REINDEX` + `ANALYZE` to resolve inconsistency after large
refactors/re-ingestion.

## Requirement coverage
FR-1.3, FR-4, FR-3.1, FR-6.1, FR-6.2, FR-8.2; NFR-2.1, NFR-3.1, NFR-4;
US-6.1, US-8.2, US-8.4.

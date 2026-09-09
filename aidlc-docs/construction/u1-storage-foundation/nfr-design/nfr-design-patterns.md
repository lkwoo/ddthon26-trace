# U1 Storage Foundation — NFR Design Patterns

## Repository pattern (SQL isolation)
Each table family is wrapped by a repository (`ChunkRepository`,
`GraphRepository`, `RelationshipRepository`, `EmbeddingRepository`,
`SummaryRepository`). SQL exists nowhere else (App Design Q4). Callers depend on
typed methods, not the DB. This localizes latency-sensitive query tuning and
makes the vec/fallback swap invisible upstream.

## Aggregate handle (Repositories facade)
`Repositories` bundles all five repositories behind one object constructed from a
single `KnowledgeStore`. Units receive this one handle rather than wiring each
repo, reducing coupling and giving a single injection point.

## Optional-dependency capability detection with graceful degradation
`KnowledgeStore._try_load_vec()` probes `sqlite-vec` at connect time and records
the capability in `vec_enabled`. `init_schema` and `EmbeddingRepository` branch
on that flag: native `vec0` path when present, pure-Python cosine over BLOBs
otherwise. Any failure degrades silently instead of aborting (NFR-4).

## Connection lifecycle / lazy singleton connection
`connect()` opens the connection once and memoizes it (`self._conn`); repeat
calls reuse it. Context-manager support (`__enter__`/`__exit__`) guarantees
commit + close. `foreign_keys` pragma set once at open.

## Idempotent, versioned schema migration
All DDL is `CREATE TABLE IF NOT EXISTS` and `schema_version` is written to
`meta`, so `init_schema()` is safe to re-run and provides a migration anchor
point for future versions.

## Typed-result contract (no-exception reads)
Reads return domain dataclasses or `None`; enum columns are (de)serialized via
`.value`. This keeps the persistence boundary predictable and token-efficient
for the MCP layer downstream.

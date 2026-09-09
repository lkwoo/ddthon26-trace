# U1 Storage Foundation — Tech Stack Decisions

## Storage engine: SQLite (stdlib `sqlite3`)
- **Decision**: embedded SQLite via the Python standard library.
- **Why**: zero-install, single-file DB under `<target>/.knowledge-store/`,
  matches requirements Q2 and NFR-4 (installability). No server process.
- **Config**: `row_factory = sqlite3.Row`, `PRAGMA foreign_keys = ON`, one
  memoized connection per `KnowledgeStore`.

## Vector index: sqlite-vec (optional extra)
- **Decision**: use the `vec0` virtual table when the `sqlite-vec` extension
  loads; otherwise fall back.
- **Why**: native L2 nearest-neighbour search for low latency (NFR-1), but kept
  optional so a bare install still works. Declared as optional extra `[vec]`
  (`sqlite-vec>=0.1.0`) in `pyproject.toml`; core `dependencies = []`.

## Vector serialization: struct-packed float32
- **Decision**: `struct.pack("<{n}f", *vector)` little-endian float32 BLOBs
  (`_pack`/`_unpack`).
- **Why**: compact, deterministic, and the exact byte layout sqlite-vec expects,
  so the same packing feeds both the `vec0` table and the fallback BLOB table.

## Fallback strategy (offline / dependency-light)
- When `import sqlite_vec` or extension load fails, `_try_load_vec` returns False
  and `init_schema` creates the plain `embeddings(ref_id, kind, dimension, vector)`
  BLOB table instead of the `vec0` table.
- `EmbeddingRepository.search` then brute-forces `_cosine` similarity in Python.
- **Rationale**: honours NFR-3 (offline, no external service) and NFR-4 (installs
  with stdlib only). Correctness is identical; only performance differs at scale.

## Test stack: pytest + Hypothesis (PBT-09)
- **Decision**: Hypothesis is the property-based testing framework for this
  Python project (recommended by PBT-09).
- **Why**: mature shrinking + seed-based reproducibility (PBT-08), supports
  custom strategies/generators (PBT-07), integrates with the pytest runner.
- **Dependency**: declared under the `[test]` extra (`pytest>=8.0`,
  `hypothesis>=6.100`). U1's pure candidates (float32 round-trip, `_cosine`
  invariants) are the PBT-eligible targets; DB-stateful behaviour is covered by
  example-based pipeline tests.

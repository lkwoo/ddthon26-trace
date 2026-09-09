# U1 Storage Foundation — NFR Requirements

Applicable NFRs and how the implemented code meets them.

## NFR-1 Performance / Latency (NFR-1.1 ~1s target)
- Embedded SQLite: no network round-trip, in-process queries.
- Indexes on the hot read paths: `idx_chunks_source`, `idx_versions_latest`,
  `idx_edges_src`, `idx_rel_src`. Latest-version read is a single indexed JOIN
  (`ChunkRepository.get`).
- Vector search uses sqlite-vec `vec0 MATCH ... ORDER BY distance LIMIT` when
  available (native ANN), keeping semantic queries fast. `reindex()` runs
  `REINDEX`+`ANALYZE` to keep the planner's statistics current.

## NFR-3 LLM-free / Offline (NFR-3.1)
- U1 makes no network calls and calls no external API. Persistence is purely
  local file I/O under `<target>/.knowledge-store/knowledge.db`. Vector storage
  and cosine fallback are computed locally.

## NFR-4 Dependency-light / Installability
- Core storage depends only on the Python stdlib (`sqlite3`, `struct`, `json`,
  `math`, `hashlib`). `sqlite-vec` is strictly optional: `_try_load_vec()`
  degrades to the pure-Python BLOB + cosine fallback when the extension is
  absent, so the store installs and runs with zero binary extras.
- `pyproject.toml` declares core `dependencies = []`; `sqlite-vec` is an
  optional extra (`[vec]`).

## NFR-2 Data Consistency
- `foreign_keys = ON` + `ON DELETE CASCADE` keep chunk history consistent.
- Single latest-version invariant maintained on every `upsert_new_version`.
- `reindex()` supports re-synchronization after large refactors (NFR-2.1).

## Marked N/A
- **Security Baseline** — extension OFF (Extension Configuration: Security = No).
  No auth/crypto/secret-handling requirements apply to a local embedded store.
- **Resiliency Baseline** — extension OFF (Resiliency = No). No ret/circuit-
  breaker/HA requirements; single-process local SQLite.

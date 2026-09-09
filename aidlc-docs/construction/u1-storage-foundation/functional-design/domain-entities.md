# U1 Storage Foundation — Domain Entities

Persistent tables (DDL in `knowledge_store/store/schema.py`) and the typed
objects (`knowledge_store/types/results.py`) they map to.

## Tables (relational, always created — CORE_DDL)

### meta
- `key TEXT PRIMARY KEY`, `value TEXT NOT NULL`. Holds `schema_version`.

### chunks (latest chunk metadata)
- `chunk_id TEXT PK`, `source_path TEXT`, `ordinal INTEGER`,
  `kind TEXT DEFAULT 'paragraph'`, `tags TEXT` (comma-separated),
  `metadata TEXT` (JSON), `latest_version INTEGER DEFAULT 1`,
  `created_at TEXT`. Index: `idx_chunks_source(source_path)`.
- Maps to `Chunk(id, text, source_path, ordinal, kind, tags, metadata)`.

### chunk_versions (full history, Epic 4)
- `chunk_id TEXT`, `version INTEGER`, `text TEXT`, `is_latest INTEGER`,
  `created_at TEXT`, `PK(chunk_id, version)`, FK -> `chunks` ON DELETE CASCADE.
  Index: `idx_versions_latest(chunk_id, is_latest)`.
- Maps to `ChunkVersion(chunk_id, version, text, is_latest)`.

### graph_nodes (FR-2)
- `id TEXT PK`, `name TEXT`, `kind TEXT`, `path TEXT`, `language TEXT`.
- Maps to `GraphNode(id, name, kind, path, language)`.

### graph_edges (FR-2.1)
- `src TEXT`, `dst TEXT`, `type TEXT`, `resolved INTEGER`,
  `PK(src, dst, type)`. Index: `idx_edges_src(src)`.
- Maps to `GraphEdge(src, dst, type: EdgeType, resolved)`.

### relationships (FR-3)
- `src_id TEXT`, `dst_id TEXT`, `type TEXT`, `score REAL DEFAULT 1.0`,
  `resolved INTEGER`, `PK(src_id, dst_id, type)`. Index: `idx_rel_src(src_id)`.
- Maps to `Relationship(src_id, dst_id, type: RelationType, score, resolved)`.

### summaries (FR-5)
- `chunk_id TEXT PK`, `text TEXT`.
- Maps to `Summary(chunk_id, text)`.

### embeddings (fallback BLOB table — FALLBACK_EMBEDDING_DDL)
- `ref_id TEXT PK`, `kind TEXT DEFAULT 'chunk'`, `dimension INTEGER`,
  `vector BLOB` (packed LE float32). Created only when sqlite-vec is unavailable.

### embeddings_vec (vec0 virtual table — vec_embedding_ddl)
- `ref_id TEXT PRIMARY KEY, embedding float[dimension]`. Created only when
  sqlite-vec is loaded and a dimension is known.
- Both embedding paths surface `SearchHit(ref_id, kind, score, preview)`.

## Enums (shared)
- `Status` (OK/UNSUPPORTED/UNRESOLVED/NOT_FOUND/SKIPPED/ERROR).
- `EdgeType` (define/call/depend/inherit/contain), `RelationType`
  (embedding/markdown_link/tag). Persisted as their string `.value`.

## Testable Properties (PBT-01)

| Property | Category | Target | Status under PBT Partial |
|---|---|---|---|
| `_unpack(_pack(v)) == v` for float32 vectors | Round-trip | `repositories._pack`/`_unpack` | Enforced-eligible (PBT-02) — pure serialization round-trip |
| `upsert_new_version` keeps exactly one `is_latest=1` per chunk | Invariant | `ChunkRepository` | Advisory (stateful DB write; PBT-06 not in Partial set) |
| `init_schema()` idempotent (repeat calls = same schema) | Idempotence | `KnowledgeStore.init_schema` | Advisory (PBT-04 not in Partial set) |
| `_cosine(a,a)==1.0` (normalized), symmetry `_cosine(a,b)==_cosine(b,a)` | Invariant | `repositories._cosine` | Enforced-eligible (PBT-03) — pure function |
| Enum value round-trips (write `.value` -> read `EnumType(value)`) | Round-trip | Graph/Relationship repos | Advisory (I/O-bound) |

Under PBT Partial (PBT-02/03/07/08/09), only the pure-function / serialization
round-trip properties are blocking-eligible. U1's unit-of-work entry marks U1
"N/A directly (schema/IO)"; the float32 round-trip and `_cosine` invariants are
the pure candidates carried forward. Stateful DB invariants are advisory and are
covered by example-based pipeline tests instead.

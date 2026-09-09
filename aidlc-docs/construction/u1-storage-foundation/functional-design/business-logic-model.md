# U1 Storage Foundation — Business Logic Model

**Unit**: u1-storage-foundation
**Bounded context**: Knowledge Persistence
**Components**: C14 KnowledgeStore, C15 Repositories
**Source**: `knowledge_store/store/{schema,store,repositories,__init__}.py`, `knowledge_store/types/results.py`

## Responsibilities

U1 is the foundation layer. It owns the embedded database and is the ONLY place
SQL is issued (Application Design Q4). Concretely it:

- Owns the SQLite connection and (optional) sqlite-vec extension loading
  (`KnowledgeStore`).
- Manages the centralized, versioned DDL schema and its migration entry point
  (`schema.py`, `KnowledgeStore.init_schema`, `KnowledgeStore.reindex`).
- Exposes all persistence through repository classes that return typed domain
  objects from `knowledge_store.types`, never raw rows and never exceptions for
  expected outcomes (Q7).
- Hides the vector-storage strategy (sqlite-vec `vec0` table vs. brute-force
  cosine over packed BLOBs) behind `EmbeddingRepository`.

## Key classes and methods

- `KnowledgeStore` — `connect()`, `_try_load_vec()`, `vec_enabled` (property),
  `init_schema(embedding_dimension=None)`, `reindex()`, `close()`, context-manager
  support (`__enter__`/`__exit__`).
- `Repositories` — aggregate handle bundling `chunks`, `graph`, `relationships`,
  `embeddings`, `summaries`.
- `ChunkRepository` — `upsert_new_version()`, `get()`, `latest_version()`,
  `history()`, `all_latest()`, `by_source()`.
- `GraphRepository` — `add_node()`, `add_edge()`, `commit()`, `nodes()`, `edges()`.
- `RelationshipRepository` — `add()`, `add_many()`, `for_source()`, `all()`.
- `EmbeddingRepository` — `upsert()`, `search()`, `count()` (vec/fallback split).
- `SummaryRepository` — `put()`, `get()`, `all()`.
- Module helpers: `_pack()`/`_unpack()` (float32 struct packing), `_cosine()`.

## Operation flow (write path used by ingestion)

1. Caller opens `KnowledgeStore(target_dir)` and calls `init_schema(dim)`.
2. `connect()` opens sqlite3, sets `row_factory=Row`, enables foreign keys, and
   probes sqlite-vec via `_try_load_vec()` -> sets `vec_enabled`.
3. `init_schema` runs `CORE_DDL`, then either the `vec0` virtual table (vec on +
   dimension known) or `FALLBACK_EMBEDDING_DDL`, then records `schema_version`.
4. Ingestion writes chunks through `ChunkRepository.upsert_new_version()` and
   vectors through `EmbeddingRepository.upsert()`; reads return typed objects.

## Component / interaction sketch (plain ASCII)

```
  Services / Engine units (U2..U6)
              |
              v
       Repositories (aggregate)
   +----------+-----------+------------+-----------+
   | Chunk    | Graph     | Relationship| Embedding | Summary
   | Repo     | Repo      | Repo        | Repo      | Repo
   +----------+-----------+------------+-----------+
              |  (all SQL isolated here)
              v
        KnowledgeStore.connect()
              |
              v
     sqlite3  ->  sqlite-vec extension (optional)
        |               |
   CORE_DDL tables   embeddings_vec (vec0)  OR  embeddings (BLOB fallback)
```

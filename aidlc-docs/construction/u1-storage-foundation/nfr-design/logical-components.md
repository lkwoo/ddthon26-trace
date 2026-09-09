# U1 Storage Foundation — Logical Components

Concrete classes/modules realizing the design, mapped to components.md.

| Class / module | File | Maps to | Role (one line) |
|---|---|---|---|
| `KnowledgeStore` | `store/store.py` | C14 KnowledgeStore | Owns the sqlite3 connection, loads optional sqlite-vec, manages schema lifecycle (`connect`/`init_schema`/`reindex`/`close`). |
| `schema` (module) | `store/schema.py` | C14 (schema/migrations) | Centralized versioned DDL: `CORE_DDL`, `FALLBACK_EMBEDDING_DDL`, `vec_embedding_ddl`, `SCHEMA_VERSION`. |
| `Repositories` | `store/repositories.py` | C15 Repositories | Aggregate facade bundling all repositories for one store. |
| `ChunkRepository` | `store/repositories.py` | C15 ChunkRepository | Chunk identity + version history CRUD (`chunks`, `chunk_versions`). |
| `GraphRepository` | `store/repositories.py` | C15 GraphRepository | Code-graph node/edge persistence (`graph_nodes`, `graph_edges`). |
| `RelationshipRepository` | `store/repositories.py` | C15 RelationshipRepository | Code<->chunk relationship persistence incl. unresolved refs. |
| `EmbeddingRepository` | `store/repositories.py` | C15 EmbeddingRepository | Vector upsert/search; vec0 vs. brute-force cosine fallback. |
| `SummaryRepository` | `store/repositories.py` | C15 SummaryRepository | Agent-authored summaries linked to chunks. |
| `_pack`/`_unpack`/`_cosine` | `store/repositories.py` | C15 (helpers) | Float32 struct packing + pure cosine similarity for fallback search. |
| typed dataclasses/enums | `types/results.py` | U-shared (Q7) | `Chunk`, `ChunkVersion`, `GraphNode`, `GraphEdge`, `Relationship`, `Summary`, `SearchHit`, `Status`, `EdgeType`, `RelationType`. |
| package exports | `store/__init__.py` | C14/C15 | Public surface: `KnowledgeStore`, `Repositories`, and each repository. |

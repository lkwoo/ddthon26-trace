"""SQLite schema DDL for the knowledge store (centralized, versioned).

The vector table is created conditionally: when the ``sqlite-vec`` extension is
available a ``vec0`` virtual table is used; otherwise embeddings fall back to a
plain BLOB table scanned in Python (brute-force cosine). Both paths are hidden
behind :class:`~knowledge_store.store.repositories.EmbeddingRepository`.
"""

from __future__ import annotations

SCHEMA_VERSION = 1

# Core relational schema (always created).
CORE_DDL = """
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Chunk identity + latest metadata. History lives in chunk_versions.
CREATE TABLE IF NOT EXISTS chunks (
    chunk_id      TEXT PRIMARY KEY,
    source_path   TEXT NOT NULL,
    ordinal       INTEGER NOT NULL,
    kind          TEXT NOT NULL DEFAULT 'paragraph',
    tags          TEXT NOT NULL DEFAULT '',          -- comma-separated
    metadata      TEXT NOT NULL DEFAULT '{}',        -- json
    latest_version INTEGER NOT NULL DEFAULT 1,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_path);

-- Full version history per chunk (Epic 4).
CREATE TABLE IF NOT EXISTS chunk_versions (
    chunk_id   TEXT NOT NULL,
    version    INTEGER NOT NULL,
    text       TEXT NOT NULL,
    is_latest  INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (chunk_id, version),
    FOREIGN KEY (chunk_id) REFERENCES chunks(chunk_id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_versions_latest ON chunk_versions(chunk_id, is_latest);

CREATE TABLE IF NOT EXISTS graph_nodes (
    id       TEXT PRIMARY KEY,
    name     TEXT NOT NULL,
    kind     TEXT NOT NULL,
    path     TEXT NOT NULL DEFAULT '',
    language TEXT NOT NULL DEFAULT ''
);

CREATE TABLE IF NOT EXISTS graph_edges (
    src      TEXT NOT NULL,
    dst      TEXT NOT NULL,
    type     TEXT NOT NULL,
    resolved INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (src, dst, type)
);
CREATE INDEX IF NOT EXISTS idx_edges_src ON graph_edges(src);

CREATE TABLE IF NOT EXISTS relationships (
    src_id   TEXT NOT NULL,
    dst_id   TEXT NOT NULL,
    type     TEXT NOT NULL,
    score    REAL NOT NULL DEFAULT 1.0,
    resolved INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (src_id, dst_id, type)
);
CREATE INDEX IF NOT EXISTS idx_rel_src ON relationships(src_id);

CREATE TABLE IF NOT EXISTS summaries (
    chunk_id TEXT PRIMARY KEY,
    text     TEXT NOT NULL
);
"""

# Fallback embedding table (used when sqlite-vec is unavailable).
FALLBACK_EMBEDDING_DDL = """
CREATE TABLE IF NOT EXISTS embeddings (
    ref_id    TEXT PRIMARY KEY,
    kind      TEXT NOT NULL DEFAULT 'chunk',
    dimension INTEGER NOT NULL,
    vector    BLOB NOT NULL       -- packed little-endian float32
);
"""


def vec_embedding_ddl(dimension: int) -> str:
    """DDL for the sqlite-vec ``vec0`` virtual table for a given dimension."""
    return (
        "CREATE VIRTUAL TABLE IF NOT EXISTS embeddings_vec USING vec0("
        f"ref_id TEXT PRIMARY KEY, embedding float[{dimension}]);"
    )

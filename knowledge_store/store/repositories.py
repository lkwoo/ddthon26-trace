"""Repositories — the only place SQL is issued (Application Design Q4).

Each repository wraps a table family and returns typed domain objects. The
:class:`Repositories` aggregate is the handle other units receive; they never
touch the ``sqlite3.Connection`` directly.
"""

from __future__ import annotations

import json
import math
import struct
from typing import Optional

from knowledge_store.store.store import KnowledgeStore
from knowledge_store.types import (
    Chunk,
    ChunkVersion,
    EdgeType,
    GraphEdge,
    GraphNode,
    Relationship,
    RelationType,
    SearchHit,
    Summary,
)


def _pack(vector: list[float]) -> bytes:
    return struct.pack(f"<{len(vector)}f", *vector)


def _unpack(blob: bytes) -> list[float]:
    return list(struct.unpack(f"<{len(blob) // 4}f", blob))


def _cosine(a: list[float], b: list[float]) -> float:
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return dot / (na * nb)


class ChunkRepository:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def _c(self):
        return self._store.connect()

    def upsert_new_version(self, chunk: Chunk, version: int) -> None:
        """Insert/refresh a chunk's latest metadata and append a version row."""
        c = self._c
        c.execute(
            "INSERT INTO chunks(chunk_id, source_path, ordinal, kind, tags, metadata, latest_version) "
            "VALUES (?,?,?,?,?,?,?) "
            "ON CONFLICT(chunk_id) DO UPDATE SET source_path=excluded.source_path, "
            "ordinal=excluded.ordinal, kind=excluded.kind, tags=excluded.tags, "
            "metadata=excluded.metadata, latest_version=excluded.latest_version",
            (chunk.id, chunk.source_path, chunk.ordinal, chunk.kind,
             ",".join(chunk.tags), json.dumps(chunk.metadata), version),
        )
        c.execute("UPDATE chunk_versions SET is_latest=0 WHERE chunk_id=?", (chunk.id,))
        c.execute(
            "INSERT OR REPLACE INTO chunk_versions(chunk_id, version, text, is_latest) "
            "VALUES (?,?,?,1)",
            (chunk.id, version, chunk.text),
        )
        c.commit()

    def get(self, chunk_id: str) -> Optional[Chunk]:
        row = self._c.execute(
            "SELECT c.*, v.text AS text FROM chunks c "
            "JOIN chunk_versions v ON v.chunk_id=c.chunk_id AND v.is_latest=1 "
            "WHERE c.chunk_id=?",
            (chunk_id,),
        ).fetchone()
        if row is None:
            return None
        return Chunk(
            id=row["chunk_id"], text=row["text"], source_path=row["source_path"],
            ordinal=row["ordinal"], kind=row["kind"],
            tags=tuple(t for t in row["tags"].split(",") if t),
            metadata=json.loads(row["metadata"]),
        )

    def latest_version(self, chunk_id: str) -> int:
        row = self._c.execute(
            "SELECT latest_version FROM chunks WHERE chunk_id=?", (chunk_id,)
        ).fetchone()
        return int(row["latest_version"]) if row else 0

    def history(self, chunk_id: str) -> list[ChunkVersion]:
        rows = self._c.execute(
            "SELECT chunk_id, version, text, is_latest FROM chunk_versions "
            "WHERE chunk_id=? ORDER BY version",
            (chunk_id,),
        ).fetchall()
        return [ChunkVersion(r["chunk_id"], r["version"], r["text"], bool(r["is_latest"]))
                for r in rows]

    def all_latest(self) -> list[Chunk]:
        rows = self._c.execute(
            "SELECT c.chunk_id FROM chunks c ORDER BY c.source_path, c.ordinal"
        ).fetchall()
        return [self.get(r["chunk_id"]) for r in rows]  # type: ignore[misc]

    def by_source(self, source_path: str) -> list[Chunk]:
        rows = self._c.execute(
            "SELECT chunk_id FROM chunks WHERE source_path=? ORDER BY ordinal",
            (source_path,),
        ).fetchall()
        return [self.get(r["chunk_id"]) for r in rows]  # type: ignore[misc]


class GraphRepository:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def _c(self):
        return self._store.connect()

    def add_node(self, node: GraphNode) -> None:
        self._c.execute(
            "INSERT OR REPLACE INTO graph_nodes(id, name, kind, path, language) VALUES (?,?,?,?,?)",
            (node.id, node.name, node.kind, node.path, node.language),
        )

    def add_edge(self, edge: GraphEdge) -> None:
        self._c.execute(
            "INSERT OR REPLACE INTO graph_edges(src, dst, type, resolved) VALUES (?,?,?,?)",
            (edge.src, edge.dst, edge.type.value, int(edge.resolved)),
        )

    def commit(self) -> None:
        self._c.commit()

    def nodes(self) -> list[GraphNode]:
        rows = self._c.execute("SELECT * FROM graph_nodes").fetchall()
        return [GraphNode(r["id"], r["name"], r["kind"], r["path"], r["language"]) for r in rows]

    def edges(self) -> list[GraphEdge]:
        rows = self._c.execute("SELECT * FROM graph_edges").fetchall()
        return [GraphEdge(r["src"], r["dst"], EdgeType(r["type"]), bool(r["resolved"])) for r in rows]


class RelationshipRepository:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def _c(self):
        return self._store.connect()

    def add(self, rel: Relationship) -> None:
        self._c.execute(
            "INSERT OR REPLACE INTO relationships(src_id, dst_id, type, score, resolved) "
            "VALUES (?,?,?,?,?)",
            (rel.src_id, rel.dst_id, rel.type.value, rel.score, int(rel.resolved)),
        )

    def add_many(self, rels: list[Relationship]) -> None:
        for r in rels:
            self.add(r)
        self._c.commit()

    def for_source(self, src_id: str) -> list[Relationship]:
        rows = self._c.execute(
            "SELECT * FROM relationships WHERE src_id=?", (src_id,)
        ).fetchall()
        return [Relationship(r["src_id"], r["dst_id"], RelationType(r["type"]),
                             r["score"], bool(r["resolved"])) for r in rows]

    def all(self) -> list[Relationship]:
        rows = self._c.execute("SELECT * FROM relationships").fetchall()
        return [Relationship(r["src_id"], r["dst_id"], RelationType(r["type"]),
                             r["score"], bool(r["resolved"])) for r in rows]


class EmbeddingRepository:
    """Stores/searches vectors via sqlite-vec when available, else brute force."""

    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def _c(self):
        return self._store.connect()

    def upsert(self, ref_id: str, vector: list[float], kind: str = "chunk") -> None:
        c = self._c
        if self._store.vec_enabled:
            c.execute("DELETE FROM embeddings_vec WHERE ref_id=?", (ref_id,))
            c.execute(
                "INSERT INTO embeddings_vec(ref_id, embedding) VALUES (?, ?)",
                (ref_id, _pack(vector)),
            )
        else:
            c.execute(
                "INSERT OR REPLACE INTO embeddings(ref_id, kind, dimension, vector) "
                "VALUES (?,?,?,?)",
                (ref_id, kind, len(vector), _pack(vector)),
            )
        c.commit()

    def search(self, query_vector: list[float], limit: int = 5) -> list[SearchHit]:
        c = self._c
        if self._store.vec_enabled:
            rows = c.execute(
                "SELECT ref_id, distance FROM embeddings_vec "
                "WHERE embedding MATCH ? ORDER BY distance LIMIT ?",
                (_pack(query_vector), limit),
            ).fetchall()
            # vec distance is L2; convert to a descending similarity score.
            return [SearchHit(ref_id=r["ref_id"], kind="chunk",
                              score=1.0 / (1.0 + float(r["distance"]))) for r in rows]
        # Fallback: brute-force cosine over stored blobs.
        rows = c.execute("SELECT ref_id, kind, vector FROM embeddings").fetchall()
        scored = [
            SearchHit(ref_id=r["ref_id"], kind=r["kind"],
                      score=_cosine(query_vector, _unpack(r["vector"])))
            for r in rows
        ]
        scored.sort(key=lambda h: h.score, reverse=True)
        return scored[:limit]

    def count(self) -> int:
        table = "embeddings_vec" if self._store.vec_enabled else "embeddings"
        return int(self._c.execute(f"SELECT COUNT(*) AS n FROM {table}").fetchone()["n"])


class SummaryRepository:
    def __init__(self, store: KnowledgeStore) -> None:
        self._store = store

    @property
    def _c(self):
        return self._store.connect()

    def put(self, chunk_id: str, text: str) -> None:
        self._c.execute(
            "INSERT OR REPLACE INTO summaries(chunk_id, text) VALUES (?, ?)",
            (chunk_id, text),
        )
        self._c.commit()

    def get(self, chunk_id: str) -> Optional[Summary]:
        row = self._c.execute(
            "SELECT chunk_id, text FROM summaries WHERE chunk_id=?", (chunk_id,)
        ).fetchone()
        return Summary(row["chunk_id"], row["text"]) if row else None

    def all(self) -> list[Summary]:
        rows = self._c.execute("SELECT chunk_id, text FROM summaries").fetchall()
        return [Summary(r["chunk_id"], r["text"]) for r in rows]


class Repositories:
    """Aggregate handle bundling all repositories for a store."""

    def __init__(self, store: KnowledgeStore) -> None:
        self.store = store
        self.chunks = ChunkRepository(store)
        self.graph = GraphRepository(store)
        self.relationships = RelationshipRepository(store)
        self.embeddings = EmbeddingRepository(store)
        self.summaries = SummaryRepository(store)

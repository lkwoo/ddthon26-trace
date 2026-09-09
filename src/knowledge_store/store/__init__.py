"""U1 — Storage Foundation.

Owns the SQLite (+ optional sqlite-vec) connection and schema, and exposes all
persistence through repository interfaces. No other unit issues SQL directly
(Application Design Q4).
"""

from knowledge_store.store.store import DEFAULT_STORE_DIRNAME, KnowledgeStore
from knowledge_store.store.repositories import (
    ChunkRepository,
    EmbeddingRepository,
    GraphRepository,
    RelationshipRepository,
    Repositories,
    SummaryRepository,
)

__all__ = [
    "KnowledgeStore",
    "DEFAULT_STORE_DIRNAME",
    "Repositories",
    "ChunkRepository",
    "GraphRepository",
    "RelationshipRepository",
    "EmbeddingRepository",
    "SummaryRepository",
]

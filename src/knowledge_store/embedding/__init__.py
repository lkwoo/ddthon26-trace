"""U2 — Embedding & Semantic Search.

Local, offline embeddings (NFR-3.1: no network / no external API) and
sqlite-vec-backed semantic search.
"""

from knowledge_store.embedding.provider import (
    EmbeddingProvider,
    HashingEmbeddingProvider,
    LocalEmbeddingProvider,
    get_default_provider,
)
from knowledge_store.embedding.search import SearchEngine

__all__ = [
    "EmbeddingProvider",
    "LocalEmbeddingProvider",
    "HashingEmbeddingProvider",
    "get_default_provider",
    "SearchEngine",
]

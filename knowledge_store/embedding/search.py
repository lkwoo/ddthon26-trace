"""SearchEngine — intent-based semantic search over embeddings (US-6.2, NFR-1).

Embeds an intent query with the local provider and ranks stored vectors via the
EmbeddingRepository (sqlite-vec or brute-force fallback). Also indexes text.
"""

from __future__ import annotations

from knowledge_store.embedding.provider import EmbeddingProvider, get_default_provider
from knowledge_store.store.repositories import Repositories
from knowledge_store.types import SearchHit


class SearchEngine:
    def __init__(self, repos: Repositories, provider: EmbeddingProvider | None = None) -> None:
        self._repos = repos
        self._provider = provider or get_default_provider()

    @property
    def provider(self) -> EmbeddingProvider:
        return self._provider

    def index(self, ref_id: str, text: str, kind: str = "chunk") -> None:
        """Embed and persist a single item's vector."""
        vector = self._provider.embed([text])[0]
        self._repos.embeddings.upsert(ref_id, vector, kind=kind)

    def index_many(self, items: list[tuple[str, str]], kind: str = "chunk") -> int:
        """Batch-embed ``(ref_id, text)`` pairs. Returns count indexed."""
        if not items:
            return 0
        vectors = self._provider.embed([t for _, t in items])
        for (ref_id, _), vector in zip(items, vectors):
            self._repos.embeddings.upsert(ref_id, vector, kind=kind)
        return len(items)

    def search(self, intent: str, limit: int = 5) -> list[SearchHit]:
        """Return the most semantically related items for an intent query."""
        if not intent.strip():
            return []
        query_vec = self._provider.embed([intent])[0]
        hits = self._repos.embeddings.search(query_vec, limit=limit)
        # Attach a short preview from the chunk store where possible (token-efficient).
        for hit in hits:
            chunk = self._repos.chunks.get(hit.ref_id)
            if chunk is not None:
                hit.preview = chunk.text[:160]
        return hits

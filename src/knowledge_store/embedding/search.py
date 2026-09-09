"""SearchEngine — hybrid intent search over embeddings + keywords (US-6.2, NFR-1).

Embeds an intent query with the local provider and ranks stored vectors via the
EmbeddingRepository (sqlite-vec or brute-force fallback), **and** ranks the same
chunk corpus with a code-aware BM25 keyword index. The two rankings are fused with
Reciprocal Rank Fusion (Increment 2, U-Hybrid / FR-H1.2) so exact identifier matches
and concept matches both surface — the "grep + concept understanding superset" goal.

Fusion is deterministic and score-scale-free (RRF over ranks), and the keyword index
adds no new dependency (pure-Python BM25). Setting ``hybrid=False`` restores the
pure-vector behaviour (used to reproduce the pre-U-Hybrid baseline in eval).
"""

from __future__ import annotations

from knowledge_store.embedding.keyword import BM25Index
from knowledge_store.embedding.provider import EmbeddingProvider, get_default_provider
from knowledge_store.store.repositories import Repositories
from knowledge_store.types import SearchHit

# RRF constant (standard default). Larger => flatter contribution of top ranks.
_RRF_K = 60


class SearchEngine:
    def __init__(self, repos: Repositories, provider: EmbeddingProvider | None = None,
                 hybrid: bool = True) -> None:
        self._repos = repos
        self._provider = provider or get_default_provider()
        self._hybrid = hybrid
        self._bm25 = BM25Index()
        self._bm25_key: frozenset[str] = frozenset()

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
        """Return the most related items for an intent query (hybrid by default)."""
        if not intent.strip():
            return []
        pool = max(limit, 50)
        query_vec = self._provider.embed([intent])[0]
        vector_hits = self._repos.embeddings.search(query_vec, limit=pool)

        if not self._hybrid:
            ranked = vector_hits[:limit]
        else:
            keyword_hits = self._keyword_search(intent, pool)
            ranked = self._fuse(vector_hits, keyword_hits, limit)

        # Attach a short preview from the chunk store where possible (token-efficient).
        for hit in ranked:
            chunk = self._repos.chunks.get(hit.ref_id)
            if chunk is not None:
                hit.preview = chunk.text[:160]
        return ranked

    # -- keyword + fusion --------------------------------------------------
    def _keyword_search(self, intent: str, limit: int) -> list[SearchHit]:
        self._ensure_bm25()
        return self._bm25.search(intent, limit=limit)

    def _ensure_bm25(self) -> None:
        """(Re)build the BM25 index if the latest-chunk set changed (deterministic)."""
        latest = self._repos.chunks.all_latest()
        key = frozenset(c.id for c in latest)
        if key != self._bm25_key:
            self._bm25.build([(c.id, c.text) for c in latest])
            self._bm25_key = key

    @staticmethod
    def _fuse(vector_hits: list[SearchHit], keyword_hits: list[SearchHit],
              limit: int) -> list[SearchHit]:
        """Reciprocal Rank Fusion; scores min-max normalised to (0, 1]."""
        fused: dict[str, float] = {}
        for lst in (vector_hits, keyword_hits):
            for rank, hit in enumerate(lst):
                fused[hit.ref_id] = fused.get(hit.ref_id, 0.0) + 1.0 / (_RRF_K + rank + 1)
        if not fused:
            return []
        top = max(fused.values())
        # Deterministic: fused score desc, then ref_id asc.
        order = sorted(fused.items(), key=lambda kv: (-kv[1], kv[0]))
        return [SearchHit(ref_id=ref, kind="chunk", score=(raw / top))
                for ref, raw in order[:limit]]

"""RelationshipBuilder + strategies — connect code symbols <-> doc chunks (FR-3).

Three pluggable strategies (Application Design C7):
* EmbeddingSimilarityStrategy (US-3.1) — local embedding similarity via SearchEngine.
* MarkdownLinkStrategy (US-3.2) — parse [[wikilink]] / links; broken -> unresolved.
* TagMatchStrategy (US-3.3) — connect items sharing a tag.

All strategies are deterministic and return typed :class:`Relationship` objects.
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from knowledge_store.embedding.search import SearchEngine
from knowledge_store.types import Chunk, Relationship, RelationType

_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_MDLINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


@runtime_checkable
class RelationStrategy(Protocol):
    def build(self, chunks: list[Chunk]) -> list[Relationship]: ...


class EmbeddingSimilarityStrategy:
    """Link each chunk to its top-K nearest neighbours by embedding similarity.

    Chunks are already embedded and indexed before relationship building runs, so
    this reuses each chunk's persisted vector via ``SearchEngine.neighbors_of``
    (pure-vector nearest neighbours) rather than re-embedding and re-running the
    full hybrid intent search per chunk — the same edges at a fraction of the cost.
    """

    def __init__(self, search: SearchEngine, top_k: int = 3, min_score: float = 0.3) -> None:
        self._search = search
        self._top_k = top_k
        self._min_score = min_score

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        rels: list[Relationship] = []
        for chunk in chunks:
            hits = self._search.neighbors_of(chunk.id, limit=self._top_k + 1)
            for hit in hits:
                if hit.ref_id == chunk.id or hit.score < self._min_score:
                    continue
                rels.append(Relationship(
                    src_id=chunk.id, dst_id=hit.ref_id,
                    type=RelationType.EMBEDDING, score=round(hit.score, 4),
                ))
        return rels


class MarkdownLinkStrategy:
    """Resolve explicit [[wikilink]] and markdown links against known chunks."""

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        # Build a title/source index for resolution.
        by_source: dict[str, str] = {}
        for chunk in chunks:
            stem = chunk.source_path.rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
            by_source.setdefault(stem, chunk.id)
        rels: list[Relationship] = []
        for chunk in chunks:
            targets = _WIKILINK_RE.findall(chunk.text) + _MDLINK_RE.findall(chunk.text)
            for raw in targets:
                key = raw.strip().rsplit("/", 1)[-1].rsplit(".", 1)[0].lower()
                dst = by_source.get(key)
                if dst is not None and dst != chunk.id:
                    rels.append(Relationship(chunk.id, dst, RelationType.MARKDOWN_LINK,
                                             score=1.0, resolved=True))
                else:
                    # Broken link recorded as unresolved (US-3.2 edge case).
                    rels.append(Relationship(chunk.id, raw.strip(), RelationType.MARKDOWN_LINK,
                                             score=0.0, resolved=False))
        return rels


class TagMatchStrategy:
    """Connect chunks that share substantive tags (US-3.3), weighted by selectivity.

    Tags are enriched at chunk time (see :class:`~knowledge_store.ingestion.tagging.
    TagEnricher`) with content facets — code symbols, link targets, salient keywords,
    and path/language/kind. A naive "share any tag -> link" would then connect every
    ``lang:python`` / ``kind:code`` chunk to every other (an O(n^2) flood of
    non-substantive edges). Instead each shared tag contributes a score that is:

    * **namespace-weighted** — a shared symbol or explicit link is a strong signal;
      a shared keyword weaker; broad facets (``lang:``/``kind:``) carry no relation
      signal at all (they remain on the chunk for search/filtering, just don't wire
      pairwise edges);
    * **selectivity-weighted** — the rarer a tag is across the corpus, the more it
      says about the pair that shares it (inverse document frequency).

    Per-pair scores accumulate across shared tags; only pairs clearing ``min_score``
    are emitted, in **both directions** so ``read_relationships`` surfaces the link
    from either endpoint. Everything is deterministic.
    """

    # Signal strength per tag namespace. Unprefixed (user #hashtag) -> strong (1.0).
    _NS_WEIGHT = {
        "sym": 1.0, "link": 1.0, "mod": 0.7, "kw": 0.6, "dir": 0.35,
        "lang": 0.0, "kind": 0.0,  # facet-only: kept on chunks, no pairwise edge
    }

    def __init__(self, max_group: int = 60, min_score: float = 0.1) -> None:
        self._max_group = max_group
        self._min_score = min_score

    def _weight(self, tag: str, df: int) -> float:
        ns = tag.split(":", 1)[0] if ":" in tag else ""
        base = self._NS_WEIGHT.get(ns, 1.0)
        if base <= 0.0:
            return 0.0
        idf = 1.0 / (df - 1)  # df=2 -> 1.0, df=3 -> 0.5, ... rarer shares weigh more
        return base * idf

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        by_tag: dict[str, list[str]] = {}
        for chunk in chunks:
            for tag in chunk.tags:
                by_tag.setdefault(tag, []).append(chunk.id)

        pair_score: dict[tuple[str, str], float] = {}
        for tag, ids in by_tag.items():
            ids = sorted(set(ids))
            df = len(ids)
            # df < 2: nothing to link. df > max_group: too broad to be substantive
            # (and O(df^2) to expand) — skip pairwise expansion.
            if df < 2 or df > self._max_group:
                continue
            weight = self._weight(tag, df)
            if weight <= 0.0:
                continue
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    pair_score[(a, b)] = pair_score.get((a, b), 0.0) + weight

        rels: list[Relationship] = []
        for (a, b), score in sorted(pair_score.items()):
            capped = round(min(1.0, score), 4)
            if capped < self._min_score:
                continue
            rels.append(Relationship(a, b, RelationType.TAG, score=capped))
            rels.append(Relationship(b, a, RelationType.TAG, score=capped))
        return rels


class RelationshipBuilder:
    def __init__(self, strategies: list[RelationStrategy]) -> None:
        self._strategies = strategies

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        rels: list[Relationship] = []
        for strategy in self._strategies:
            rels.extend(strategy.build(chunks))
        return rels

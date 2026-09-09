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
    """Link each chunk to its top-K nearest neighbours by embedding similarity."""

    def __init__(self, search: SearchEngine, top_k: int = 3, min_score: float = 0.3) -> None:
        self._search = search
        self._top_k = top_k
        self._min_score = min_score

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        rels: list[Relationship] = []
        for chunk in chunks:
            hits = self._search.search(chunk.text, limit=self._top_k + 1)
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
    """Connect chunks that share at least one tag (US-3.3)."""

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        by_tag: dict[str, list[str]] = {}
        for chunk in chunks:
            for tag in chunk.tags:
                by_tag.setdefault(tag, []).append(chunk.id)
        rels: list[Relationship] = []
        seen: set[tuple[str, str]] = set()
        for tag, ids in by_tag.items():
            ids = sorted(set(ids))
            for i, a in enumerate(ids):
                for b in ids[i + 1:]:
                    if (a, b) in seen:
                        continue
                    seen.add((a, b))
                    rels.append(Relationship(a, b, RelationType.TAG, score=1.0))
        return rels


class RelationshipBuilder:
    def __init__(self, strategies: list[RelationStrategy]) -> None:
        self._strategies = strategies

    def build(self, chunks: list[Chunk]) -> list[Relationship]:
        rels: list[Relationship] = []
        for strategy in self._strategies:
            rels.extend(strategy.build(chunks))
        return rels

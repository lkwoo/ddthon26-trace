"""Retrievers reduced to a common shape: intent -> ranked list of file paths.

Both retrievers return a ranked, de-duplicated list of *file paths* (relative to
the corpus root) so the semantic engine and the keyword/grep baseline can be
scored with the same file-level metrics and compared directly (Q4 A/B).

* :class:`SemanticRetriever` wraps the real ``QueryService.semantic_query`` and
  maps each chunk hit back to its source file via the chunk repository.
* :class:`GrepRetriever` is a dependency-free keyword baseline: it ranks files by
  how many of the query's identifier tokens they contain (a stand-in for what a
  developer would get from ``grep``). This is what a hybrid retriever must beat.
"""

from __future__ import annotations

import re
from typing import Callable, Protocol

from eval.metrics import dedup

_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")

# Very common English/query words that carry no retrieval signal for code search.
_STOPWORDS = frozenset(
    """a an the of to in on for and or is are how where what which does do we i
    it this that with as by from at be can code function method class handle
    handled used use where's whats""".split()
)


def _tokens(text: str) -> list[str]:
    return [t.lower() for t in _TOKEN_RE.findall(text)]


def _content_tokens(text: str) -> list[str]:
    return [t for t in _tokens(text) if t not in _STOPWORDS and len(t) > 1]


class Retriever(Protocol):
    name: str

    def retrieve(self, intent: str, limit: int) -> list[str]:
        """Return up to ``limit`` ranked, de-duplicated file paths."""
        ...


class SemanticRetriever:
    """Wraps ``QueryService.semantic_query`` and reduces chunk hits to files.

    ``pool`` chunk hits are requested and collapsed to unique files preserving
    rank order, so file-level recall@k has enough candidates for k up to 10.
    ``normalize`` maps a stored chunk ``source_path`` to the corpus-relative path
    used in gold labels.
    """

    name = "semantic"

    def __init__(self, query_service, chunk_repo, normalize: Callable[[str], str],
                 pool: int = 50) -> None:
        self._q = query_service
        self._chunks = chunk_repo
        self._normalize = normalize
        self._pool = pool

    def retrieve(self, intent: str, limit: int) -> list[str]:
        hits = self._q.semantic_query(intent, limit=self._pool)
        files: list[str] = []
        for hit in hits:
            chunk = self._chunks.get(hit.ref_id)
            if chunk is not None:
                files.append(self._normalize(chunk.source_path))
        return dedup(files)[:limit]


class GrepRetriever:
    """Keyword baseline: rank files by query-token frequency (a grep stand-in).

    Scoring: for each corpus file, sum the occurrences of each distinct content
    token from the query. Files with zero matches are dropped (grep would find
    nothing). Ties break by descending score then path for determinism.
    """

    name = "grep"

    def __init__(self, corpus: dict[str, str]) -> None:
        # Pre-tokenize each file once into a term-frequency map.
        self._tf: dict[str, dict[str, int]] = {}
        for path, text in corpus.items():
            tf: dict[str, int] = {}
            for tok in _tokens(text):
                tf[tok] = tf.get(tok, 0) + 1
            self._tf[path] = tf

    def retrieve(self, intent: str, limit: int) -> list[str]:
        query_terms = set(_content_tokens(intent))
        if not query_terms:
            return []
        scored: list[tuple[float, str]] = []
        for path, tf in self._tf.items():
            score = sum(tf.get(term, 0) for term in query_terms)
            if score > 0:
                scored.append((float(score), path))
        # Deterministic order: highest score first, then path ascending.
        scored.sort(key=lambda sp: (-sp[0], sp[1]))
        return [path for _, path in scored[:limit]]

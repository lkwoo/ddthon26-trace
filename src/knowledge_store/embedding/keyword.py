"""BM25Index — deterministic, dependency-free keyword ranking (Increment 2, U-Hybrid).

The keyword half of hybrid retrieval (FR-H1.1). Pure-Python **BM25 Okapi** over the
chunk corpus — deterministic and offline (NFR-E1/E2), unlike SQLite FTS5 whose bm25()
scoring varies across builds. For the corpus sizes here (tens–hundreds of chunks) a
Python scan is more than fast enough; FTS5 remains a future optimisation.

Tokenisation is **code-aware**: identifiers are split on ``_`` and camelCase
boundaries and *both* the whole identifier and its sub-words are indexed, so a query
"favorites count" matches a ``favoritesCount`` / ``favorites_count`` symbol — the
identifier-decomposition edge a naive grep lacks.
"""

from __future__ import annotations

import math
import re
from collections import Counter

from knowledge_store.types import SearchHit

_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
_CAMEL_RE = re.compile(r"[A-Z]+(?=[A-Z][a-z])|[A-Z]?[a-z]+|[A-Z]+|[0-9]+")


def tokenize(text: str) -> list[str]:
    """Code-aware tokens: whole identifiers plus camelCase/snake_case sub-words."""
    tokens: list[str] = []
    for word in _WORD_RE.findall(text):
        low = word.lower()
        tokens.append(low)
        parts = [p.lower() for seg in word.split("_") if seg
                 for p in _CAMEL_RE.findall(seg)]
        for p in parts:
            if p != low and len(p) > 1:
                tokens.append(p)
    return tokens


class BM25Index:
    """Okapi BM25 over ``(ref_id, text)`` documents. Rebuild is a pure function."""

    def __init__(self, k1: float = 1.5, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._ids: list[str] = []
        self._tf: list[Counter] = []
        self._len: list[int] = []
        self._df: Counter = Counter()
        self._idf: dict[str, float] = {}
        self._avgdl: float = 0.0

    @property
    def doc_ids(self) -> list[str]:
        return list(self._ids)

    def build(self, docs: list[tuple[str, str]]) -> None:
        self._ids, self._tf, self._len = [], [], []
        self._df = Counter()
        for ref_id, text in docs:
            toks = tokenize(text)
            tf = Counter(toks)
            self._ids.append(ref_id)
            self._tf.append(tf)
            self._len.append(len(toks))
            for term in tf:
                self._df[term] += 1
        n = len(self._ids)
        self._avgdl = (sum(self._len) / n) if n else 0.0
        # BM25+ idf (always positive), deterministic.
        self._idf = {t: math.log(1.0 + (n - df + 0.5) / (df + 0.5))
                     for t, df in self._df.items()}

    def search(self, query: str, limit: int) -> list[SearchHit]:
        if not self._ids:
            return []
        q_terms = set(tokenize(query))
        if not q_terms:
            return []
        scored: list[tuple[float, str]] = []
        for i, ref_id in enumerate(self._ids):
            tf = self._tf[i]
            dl = self._len[i]
            score = 0.0
            for term in q_terms:
                f = tf.get(term, 0)
                if not f:
                    continue
                idf = self._idf.get(term, 0.0)
                denom = f + self._k1 * (1.0 - self._b + self._b * dl / (self._avgdl or 1.0))
                score += idf * (f * (self._k1 + 1.0)) / (denom or 1.0)
            if score > 0.0:
                scored.append((score, ref_id))
        # Deterministic: score desc, then ref_id asc.
        scored.sort(key=lambda s: (-s[0], s[1]))
        return [SearchHit(ref_id=r, kind="chunk", score=s) for s, r in scored[:limit]]

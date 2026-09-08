"""Deterministic keyword + graph search (US-A2, NFR-C3).

Scoring is a deterministic weighted match (Q2=A / BR-15). Results are sorted by
score descending, then target ascending. No matches yields an empty list (BR-16).
"""

from __future__ import annotations

from dataclasses import dataclass

from ..domain.models import ModuleSummary, RelationshipGraph, SearchResult, Symbol

# Weights per match location (highest wins).
_W_NAME_EXACT = 1.0
_W_NAME_PARTIAL = 0.7
_W_SIGNATURE = 0.5
_W_DOC = 0.5
_W_BODY = 0.3


@dataclass(frozen=True)
class SearchIndex:
    """Lightweight in-memory index built at query time from stored artifacts."""

    symbols: tuple[Symbol, ...] = ()
    summaries: tuple[ModuleSummary, ...] = ()


def _tokenize(text: str) -> list[str]:
    return [t for t in text.lower().replace("\t", " ").split() if t]


def search_keyword(index: SearchIndex, query: str) -> list[SearchResult]:
    terms = _tokenize(query)
    if not terms:
        return []

    scored: dict[str, tuple[float, str]] = {}  # target -> (score, matched_on)

    def consider(target: str, score: float, matched_on: str) -> None:
        prev = scored.get(target)
        if prev is None or score > prev[0]:
            scored[target] = (score, matched_on)

    for sym in index.symbols:
        name_l = sym.name.lower()
        qname_l = sym.qualified_name.lower()
        for term in terms:
            if term == name_l or term == qname_l:
                consider(sym.id, _W_NAME_EXACT, "name")
            elif term in name_l or term in qname_l:
                consider(sym.id, _W_NAME_PARTIAL, "name")

    for summ in index.summaries:
        sig_blob = " ".join(summ.signatures).lower()
        doc_blob = " ".join(summ.docstrings).lower()
        body_blob = " ".join(summ.headings + summ.comments).lower()
        for term in terms:
            if term in sig_blob:
                consider(summ.target, _W_SIGNATURE, "signature")
            if term in doc_blob:
                consider(summ.target, _W_DOC, "doc")
            if term in body_blob:
                consider(summ.target, _W_BODY, "body")

    results = [
        SearchResult(target=t, score=s, kind="keyword", matched_on=m)  # type: ignore[arg-type]
        for t, (s, m) in scored.items()
    ]
    results.sort(key=lambda r: (-r.score, r.target))
    return results


def neighbors(
    graph: RelationshipGraph, symbol_id: str, direction: str = "callers"
) -> list[SearchResult]:
    """Return symbols adjacent to ``symbol_id`` in the given direction.

    direction: 'callers' (edges into), 'callees' (edges out of), 'deps' (out).
    """
    found: set[str] = set()
    for e in graph.edges:
        if direction == "callers" and e.dst == symbol_id:
            found.add(e.src)
        elif direction in ("callees", "deps") and e.src == symbol_id:
            found.add(e.dst)

    results = [
        SearchResult(target=t, score=1.0, kind="graph", matched_on="edge")
        for t in found
    ]
    results.sort(key=lambda r: (-r.score, r.target))
    return results

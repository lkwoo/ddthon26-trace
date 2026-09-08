"""QueryService — keyword/graph search over the knowledge base (US-A2)."""

from __future__ import annotations

from ..domain.models import SearchResult
from ..domain.query import SearchIndex, neighbors, search_keyword
from ..ports.store_port import KnowledgeStorePort
from .measurement import measure

_ID_HINT = "::"


class QueryService:
    def __init__(self, store: KnowledgeStorePort) -> None:
        self._store = store

    def query(self, text: str, mode: str = "auto") -> list[SearchResult]:
        with measure(f"query.{mode}"):
            if mode == "auto":
                mode = "graph" if _ID_HINT in text else "keyword"
            if mode == "graph":
                return self._graph_query(text)
            return self._keyword_query(text)

    def _keyword_query(self, text: str) -> list[SearchResult]:
        graph = self._store.load_graph()
        symbols = tuple(graph.nodes) if graph else ()
        index = SearchIndex(symbols=symbols, summaries=tuple(self._store.all_summaries()))
        return search_keyword(index, text)

    def _graph_query(self, symbol_id: str) -> list[SearchResult]:
        graph = self._store.load_graph()
        if graph is None:
            return []
        callers = neighbors(graph, symbol_id, "callers")
        callees = neighbors(graph, symbol_id, "callees")
        merged = {r.target: r for r in callers + callees}
        results = list(merged.values())
        results.sort(key=lambda r: (-r.score, r.target))
        return results

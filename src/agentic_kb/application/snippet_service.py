"""SnippetService — budget-aware code snippet extraction (US-A3, US-N2)."""

from __future__ import annotations

from ..domain.chunking import select_snippet
from ..domain.models import Snippet
from ..ports.source_port import FileSourcePort
from ..ports.store_port import KnowledgeStorePort
from .measurement import measure


class SnippetService:
    def __init__(self, store: KnowledgeStorePort, source: FileSourcePort) -> None:
        self._store = store
        self._source = source

    def snippet(self, target: str, token_budget: int) -> Snippet:
        with measure("snippet"):
            path, span = self._resolve(target)
            try:
                source_text = self._source.read(path)
            except (OSError, ValueError):
                return Snippet(text="", estimated_tokens=0, truncated=False)

            text = source_text
            if span is not None:
                lines = source_text.splitlines(keepends=True)
                text = "".join(lines[span[0] - 1 : span[1]])
            return select_snippet(text, token_budget)

    def _resolve(self, target: str) -> tuple[str, tuple[int, int] | None]:
        if "::" not in target:
            return target, None
        path = target.split("::", 1)[0]
        graph = self._store.load_graph()
        if graph is not None:
            for node in graph.nodes:
                if node.id == target:
                    return path, (node.location.start_line, node.location.end_line)
        return path, None

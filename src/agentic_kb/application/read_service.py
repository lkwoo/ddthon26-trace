"""KnowledgeReadService — structure/summary/relationship reads (US-A1, US-H1..H3).

Missing targets return None (BR-13). `get_summary` merges the engine summary with
agent notes, keeping provenance separate and engine-first (BR-14, Q5).
"""

from __future__ import annotations

from ..domain.models import MergedSummary, RelationshipGraph, StructureTree
from ..ports.store_port import KnowledgeStorePort
from .measurement import measure


class KnowledgeReadService:
    def __init__(self, store: KnowledgeStorePort) -> None:
        self._store = store

    def get_structure(self) -> StructureTree | None:
        with measure("read.structure"):
            return self._store.load_structure()

    def get_summary(self, target: str) -> MergedSummary | None:
        with measure("read.summary"):
            engine = self._store.load_summary(target)
            notes = tuple(self._store.load_agent_notes(target))
            if engine is None and not notes:
                return None
            return MergedSummary(
                target=target, engine=engine, agent_notes=notes, engine_first=True
            )

    def get_relationships(self, target: str | None = None) -> RelationshipGraph | None:
        with measure("read.relationships"):
            graph = self._store.load_graph()
            if graph is None or target is None:
                return graph
            keep = {
                e for e in graph.edges if e.src == target or e.dst == target
            }
            node_ids = {target} | {e.src for e in keep} | {e.dst for e in keep}
            nodes = tuple(n for n in graph.nodes if n.id in node_ids)
            return RelationshipGraph(nodes=nodes, edges=tuple(sorted(keep, key=lambda e: (e.src, e.dst, e.kind))))

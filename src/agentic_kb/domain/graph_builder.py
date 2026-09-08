"""Deterministic relationship-graph construction (US-E2, PBT-03).

Pure function: identical `ParsedUnit` inputs always yield an identical
`RelationshipGraph` (BR-6). Unresolved references are dropped (treated as
external/stdlib symbols).
"""

from __future__ import annotations

from ..domain.models import Edge, ParsedUnit, RelationshipGraph, Symbol


def build(units: list[ParsedUnit]) -> RelationshipGraph:
    # Collect + dedup nodes by id, sorted ascending (deterministic).
    nodes_by_id: dict[str, Symbol] = {}
    for unit in units:
        for sym in unit.symbols:
            nodes_by_id.setdefault(sym.id, sym)
    nodes = tuple(sorted(nodes_by_id.values(), key=lambda s: s.id))

    # Symbol table: name/qualified_name -> resolved symbol id.
    # On collision, prefer the lexicographically smallest id (stable).
    table: dict[str, str] = {}
    for sym in sorted(nodes_by_id.values(), key=lambda s: s.id):
        for key in (sym.qualified_name, sym.name):
            if key not in table:
                table[key] = sym.id

    edge_set: set[Edge] = set()
    for unit in units:
        for ref in unit.references:
            dst = table.get(ref.dst_name)
            if dst is None:
                continue  # unresolved -> drop
            if ref.src_symbol not in nodes_by_id:
                continue
            edge_set.add(Edge(src=ref.src_symbol, dst=dst, kind=ref.kind))

    edges = tuple(sorted(edge_set, key=lambda e: (e.src, e.dst, e.kind)))
    return RelationshipGraph(nodes=nodes, edges=edges)

# U4 Code Structure & Relationships — Domain Entities

Graph/relationship types in `knowledge_store/types/results.py`; `CodeUnit` in
`knowledge_store/codegraph/analyzer.py`.

## Entities / structures

- **`CodeUnit`** (dataclass, `analyzer.py`) — input: `path`, `language`, `text`.
- **`GraphNode`** — `id`, `name`, `kind` (`file|function|class|module`), `path`,
  `language`. Node id format `kind:path:name` (`_node_id`).
- **`GraphEdge`** — `src`, `dst`, `type: EdgeType`, `resolved: bool` (default True).
- **`GraphResult`** — `status`, `nodes: list[GraphNode]`, `edges: list[GraphEdge]`,
  `unresolved: list[str]` (references with no definition, US-2.2).
- **`Relationship`** — `src_id`, `dst_id`, `type: RelationType`, `score`,
  `resolved` (False for broken markdown links, US-3.2).
- **`EdgeType`** enum — `DEFINE`, `CALL`, `DEPEND`, `INHERIT`, `CONTAIN`.
- **`RelationType`** enum — `EMBEDDING`, `MARKDOWN_LINK`, `TAG`.

## Entity sketch

```
[ CodeUnit ] --analyze--> GraphResult { GraphNode*, GraphEdge*, unresolved[] }
                                            ^  edge.type in EdgeType
[ Chunk ] --RelationshipBuilder--> [ Relationship ] { type in RelationType, resolved }
```

## Testable Properties (PBT-01)

| ID | Property | Status |
|---|---|---|
| P-U4-1 | `analyze` is deterministic — identical node/edge sequence across runs | **Enforced (determinism, PBT-03 spirit)** — `test_deterministic_across_runs` |
| P-U4-2 | Defined functions and classes appear as nodes | Advisory — `test_defines_functions_and_classes` |
| P-U4-3 | A call to a known definition yields a resolved `CALL` edge | Advisory — `test_resolves_call_to_definition` |
| P-U4-4 | Unresolved call recorded in `unresolved`, `status` stays OK (non-fatal) | Advisory — `test_unresolved_call_is_recorded_not_fatal` |
| P-U4-5 | Cross-file inheritance edge resolves to the base node | Advisory — `test_inheritance_edge_resolves_cross_symbol` |
| P-U4-6 | Broken markdown link → `Relationship(resolved=False)`, processing continues | Advisory (implied by BR-U4-10) |

> U4 has no enforced serialization round-trip; its enforced PBT surface is the
> determinism guarantee. Round-trip (PBT-02) and hash determinism (PBT-03) are
> enforced in U3.

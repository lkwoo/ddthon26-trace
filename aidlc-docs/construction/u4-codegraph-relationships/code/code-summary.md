# U4 Code Structure & Relationships — Code Summary

**Status**: Code generation complete. All source and tests implemented and green.

## Files

| File | Description |
|---|---|
| `knowledge_store/codegraph/__init__.py` | Public exports for U4 (`CodeStructureAnalyzer`, `CodeUnit`, builder + strategies). |
| `knowledge_store/codegraph/analyzer.py` | `CodeStructureAnalyzer`, `CodeUnit`, regex extractors, cross-file resolution, inheritance re-resolution. |
| `knowledge_store/codegraph/relationships.py` | `RelationStrategy` Protocol, `RelationshipBuilder`, `EmbeddingSimilarityStrategy`, `MarkdownLinkStrategy`, `TagMatchStrategy`. |
| `knowledge_store/types/results.py` | Shared typed results: `GraphNode`, `GraphEdge`, `GraphResult`, `Relationship`, `EdgeType`, `RelationType`. |

## Key public API

- `CodeStructureAnalyzer.analyze(units: list[CodeUnit]) -> GraphResult`
- `RelationshipBuilder(strategies).build(chunks) -> list[Relationship]`
- `EmbeddingSimilarityStrategy(search, top_k, min_score).build(chunks)`
- `MarkdownLinkStrategy().build(chunks)`
- `TagMatchStrategy().build(chunks)`

## Tests exercising this unit (all passing)

- `tests/codegraph/test_analyzer.py` — defines functions/classes, resolves call
  to definition, unresolved call recorded not fatal (US-2.2), cross-symbol
  inheritance resolution, determinism across runs (US-2.1).

Whole suite = **36 tests green**; the shared Hypothesis PBT suite (in U3, using
`tests/generators.py`) runs 200–300 examples each (PBT-08 shrinking/
reproducibility, PBT-09 framework). U4's enforced property is analysis
determinism; round-trip (PBT-02) and hash determinism (PBT-03) are enforced in U3.

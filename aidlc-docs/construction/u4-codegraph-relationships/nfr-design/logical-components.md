# U4 Code Structure & Relationships — Logical Components

Concrete classes mapped to the components in `components.md`.

| Class (module) | Component | Role (one line) |
|---|---|---|
| `CodeStructureAnalyzer` — `analyzer.py` | C6 | Build code graph: symbols + define/call/depend/inherit/contain edges, cross-file resolution, unresolved marking. |
| `CodeUnit` — `analyzer.py` | C6 (input) | Analyzer input record (`path`, `language`, `text`). |
| `RelationStrategy` (Protocol) — `relationships.py` | C7 | Interface: `build(chunks) -> list[Relationship]`. |
| `RelationshipBuilder` — `relationships.py` | C7 | Runs configured strategies and aggregates their relationships. |
| `EmbeddingSimilarityStrategy` — `relationships.py` | C7 | Top-K nearest-neighbour links via local `SearchEngine` (US-3.1). |
| `MarkdownLinkStrategy` — `relationships.py` | C7 | Resolves `[[wikilink]]`/markdown links; broken → unresolved (US-3.2). |
| `TagMatchStrategy` — `relationships.py` | C7 | Connects chunks sharing a tag (US-3.3). |
| `GraphNode`, `GraphEdge`, `GraphResult`, `Relationship`, `EdgeType`, `RelationType` — `types/results.py` | shared (Q7) | Typed graph/relationship contracts. |

**Dependencies**: U1 (Graph/Relationship repos), U2 (`SearchEngine` /
`EmbeddingProvider` for the embedding strategy), U3 (extraction output as
`CodeUnit`/chunks). Downward-only, no peer/upward coupling.

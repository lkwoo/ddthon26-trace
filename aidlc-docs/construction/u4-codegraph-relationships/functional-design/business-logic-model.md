# U4 Code Structure & Relationships — Business Logic Model

**Unit**: `u4-codegraph-relationships` · **Package**: `knowledge_store/codegraph/`
**Components**: C6 CodeStructureAnalyzer, C7 RelationshipBuilder (+strategies)
**Stage**: CONSTRUCTION → Functional Design

## Responsibilities

1. **Build the code graph** — extract symbols (files, functions, classes) and
   edges (define / call / depend / inherit / contain), resolving cross-file
   symbols by name; unresolved references are recorded, not fatal (FR-2, US-2.1/2.2).
2. **Construct code↔chunk relationships** via three deterministic strategies —
   embedding similarity, markdown links, tag match (FR-3, US-3.1/3.2/3.3).

Both are deterministic and LLM-free (NFR-3.1).

## Key operations (real class/method names)

- `CodeStructureAnalyzer.analyze(units: list[CodeUnit]) -> GraphResult`
  - iterates `units` sorted by path (determinism); per unit calls
    `_extract_symbols`, `_imports`, `_calls`.
  - emits `CONTAIN` (file→symbol) and `DEFINE` (symbol→file) edges; records each
    symbol name → node id in `defined` (last-definition-wins).
  - after all units: resolves call sites (`CALL` resolved or `resolved=False` +
    appended to `unresolved`); re-resolves `INHERIT` placeholders against
    `defined`; sorts `unresolved`.
- `RelationshipBuilder.build(chunks) -> list[Relationship]` — runs each
  configured strategy and concatenates results.
- `EmbeddingSimilarityStrategy.build` — top-K nearest neighbours via
  `SearchEngine.search`, filtered by `min_score`, `RelationType.EMBEDDING`.
- `MarkdownLinkStrategy.build` — resolves `[[wikilink]]`/`[..](..)` targets
  against a source-stem index; unresolved → `resolved=False`.
- `TagMatchStrategy.build` — connects chunk pairs sharing a tag (`RelationType.TAG`).

## Operation flow

```
[ CodeUnit ] (sorted by path)
     |
     v
CodeStructureAnalyzer.analyze
   symbols -> GraphNode + CONTAIN/DEFINE edges; defined[name]=id
   calls   -> deferred call_sites
   imports -> DEPEND (resolved=False)
     |
     v
cross-file resolution:
   call -> defined? CALL(resolved) : CALL(unresolved) + unresolved += name
   INHERIT placeholder -> re-point to defined[base] if known
     |
     v
GraphResult(nodes, edges, unresolved sorted)

chunks --> RelationshipBuilder.build
              -> EmbeddingSimilarity + MarkdownLink + TagMatch
              -> [ Relationship ]  (resolved flag marks broken links)
```

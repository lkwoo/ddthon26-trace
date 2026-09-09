# U4 Code Structure & Relationships — Business Rules

Rules enforced by `knowledge_store/codegraph/analyzer.py` and
`relationships.py`. Each cites the requirement/story satisfied.

## Code graph (C6 CodeStructureAnalyzer)

- **BR-U4-1** Symbol extraction is deterministic and LLM-free; Python uses
  dedicated regexes, other languages a generic function/class regex fallback
  (FR-2.1, US-2.1). tree-sitter is optional; the regex analyzer is the guaranteed
  path.
- **BR-U4-2** Each file becomes a `file` node; every symbol gets a `CONTAIN`
  edge (file→symbol) and a `DEFINE` edge (symbol→file) (FR-2.1).
- **BR-U4-3** **Cross-file symbol resolution by name**: a call/inherit target is
  matched to any known definition in `defined` (name → node id) regardless of
  file (FR-2.2, US-2.2).
- **BR-U4-4** Units are processed **sorted by path**, and calls/imports are
  sorted+de-duped, so node/edge order is identical across runs (US-2.1
  determinism).
- **BR-U4-5** An **unresolved reference is recorded, not fatal**: the `CALL`
  edge is kept with `resolved=False` and the name is appended to
  `GraphResult.unresolved`; `status` stays `OK` (US-2.2 edge case).
- **BR-U4-6** **Inheritance re-resolution**: `INHERIT` edges are first emitted as
  placeholders (`resolved=False` to the base *name*), then re-pointed to the
  base's node id if it becomes known (FR-2.2, US-2.2).
- **BR-U4-7** Keyword-like call tokens (`if`, `for`, `return`, `print`, …) are
  excluded from call edges to avoid false symbols.
- **BR-U4-8** `unresolved` is emitted as a **sorted, de-duplicated** list.

## Relationships (C7 RelationshipBuilder + strategies)

- **BR-U4-9** Embedding strategy links a chunk to top-K neighbours above
  `min_score`, skipping self; scores rounded (deterministic) (FR-3.1, US-3.1).
- **BR-U4-10** Markdown-link strategy resolves `[[wikilink]]`/markdown links
  against a source-stem index; a resolvable target → `resolved=True` (score 1.0),
  a **broken link → `resolved=False`** and processing continues (FR-3.2, US-3.2).
- **BR-U4-11** Tag strategy connects each unordered pair of chunks sharing a tag
  exactly once (`seen` set), sorted ids for determinism (FR-3.3, US-3.3).
- **BR-U4-12** All strategies are deterministic and return typed `Relationship`
  objects with a `resolved` flag (App Design Q7).

**Cited requirements/stories**: FR-2.1, FR-2.2, FR-3.1–3.3; US-2.1, US-2.2,
US-3.1, US-3.2, US-3.3; NFR-3.1 (LLM-free).

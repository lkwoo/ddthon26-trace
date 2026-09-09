# U4 Code Structure & Relationships — NFR Design Patterns

## Strategy pattern for relationship construction (App Design C7)

`RelationshipBuilder` holds a list of objects satisfying the `RelationStrategy`
Protocol (`build(chunks) -> list[Relationship]`) and simply concatenates their
output. The three strategies — `EmbeddingSimilarityStrategy`,
`MarkdownLinkStrategy`, `TagMatchStrategy` — are independent and swappable, so a
new relationship source is added without changing the builder or callers
(FR-3.1–3.3). Each returns typed `Relationship` objects carrying a `resolved`
flag.

## Deterministic pure-function design (enables PBT)

- `CodeStructureAnalyzer.analyze` sorts units by path and sorts/de-dups calls and
  imports, so node and edge sequences are byte-stable across runs
  (`test_deterministic_across_runs`). No clocks, randomness, or I/O in analysis.
- Tag pairing uses a `seen` set over sorted ids; embedding scores are rounded.
  These make the strategies reproducible under Hypothesis (PBT-08).

## Graceful optional-dependency degradation

tree-sitter is optional; the module falls back to deterministic regex analyzers
(Python-specific + a generic function/class/interface regex). Analysis therefore
succeeds with stdlib only, matching NFR-4 and U3's optional-parser philosophy.

## Non-fatal typed status (App Design Q7)

Unresolved symbols and broken markdown links do not raise: they are captured as
`resolved=False` edges/relationships and (for symbols) appended to
`GraphResult.unresolved`, while `status` stays `OK`. The graph is always
returned, keeping the ingestion pipeline resilient (US-2.2, US-3.2).

## Downward-only dependency

U4 depends downward on U1 (Graph/Relationship repos) and U2
(`SearchEngine`/`EmbeddingProvider`) and consumes U3's extraction output — no
peer-to-peer or upward coupling.

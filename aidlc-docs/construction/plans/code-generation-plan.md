# Construction — Code Generation Plan (all 8 units)

**Mode**: auto-adopt (recommended options taken automatically per user directive).
**Order**: dependency build order U1 → U2 → U3 → U4 → U5 → U7 → U6 → U8
(single sanctioned cross-orchestration edge U6→U7 handled by assembly).
**Status**: COMPLETE — all steps executed; full test suite green (36 passed).

Shared foundation (built first): `knowledge_store/types/` typed contracts
(`Status`, `Chunk`, `ExtractionResult`, `GraphNode/Edge/Result`, `Relationship`,
`MatchResult`, `VersionResult`, `SearchHit`, `SnippetResult`, `Summary`,
`Content`, `ToolResult`, `IngestionReport`, `InstallReport`, `ExportResult`).
- [x] Shared types package

## U1 — Storage Foundation
- [x] `store/schema.py` — SCHEMA_VERSION, core DDL, fallback + vec0 embedding DDL
- [x] `store/store.py` — KnowledgeStore (connect, optional sqlite-vec load, init_schema, reindex)
- [x] `store/repositories.py` — Chunk/Graph/Relationship/Embedding/Summary repos (all SQL isolated here)

## U2 — Embedding & Semantic Search
- [x] `embedding/provider.py` — EmbeddingProvider protocol, HashingEmbeddingProvider (deterministic), LocalEmbeddingProvider (fastembed optional), default singleton
- [x] `embedding/search.py` — SearchEngine (index/index_many/search with previews)

## U3 — Ingestion & Chunking
- [x] `ingestion/extractors.py` — registry + Markdown/Code/Spreadsheet/PDF extractors (typed UNSUPPORTED)
- [x] `ingestion/chunker.py` — deterministic chunking + serialize/deserialize round-trip (PBT-02)
- [x] `ingestion/versioner.py` — MinHash signatures + ChunkVersioner match/apply_version (PBT-03)

## U4 — Code Structure & Relationships
- [x] `codegraph/analyzer.py` — CodeStructureAnalyzer (regex fallback; tree-sitter optional); cross-file resolution
- [x] `codegraph/relationships.py` — RelationshipBuilder + Embedding/MarkdownLink/Tag strategies

## U5 — Retrieval & Summarization
- [x] `retrieval/tokens.py` — TokenEstimator (monotonic invariant, PBT-03)
- [x] `retrieval/snippet.py` — SnippetBuilder (token-budget invariant, PBT-03)
- [x] `retrieval/summary_store.py` — SummaryStore (agent-driven; server never authors summaries)

## U6 — Service Orchestration & MCP Server
- [x] `services/system.py` — KnowledgeSystem composition root
- [x] `services/services.py` — Ingestion/Query/Summarization/WikiExport services (orchestration only)
- [x] `mcp/tools.py` — self-describing ToolRegistry (9 tools, "when to use" guidance)
- [x] `mcp/server.py` — thin stdio adapter (mcp optional; `--manifest` fallback)

## U7 — Wiki Export & Web Viewer
- [x] `wiki/exporter.py` — WikiExporter (structure/relationships/wiki JSON + asset copy)
- [x] `viewer/index.html`, `viewer/styles.css`, `viewer/app.js` — static D3 viewer (tree/graph/wiki)

## U8 — Installer & Packaging
- [x] `install/service.py` — InstallService (isolated store, client detect/merge, manual snippet)
- [x] `install/cli.py` — `knowledge-store` CLI (install/init/ingest/manifest)
- [x] `pyproject.toml` — metadata, optional extras, console_scripts entry points

## Cross-cutting artifacts
- [x] `tests/` — mirror layout; PBT (Hypothesis) + example-based; 36 passed
- [x] `README.md` (agent-readable install, US-8.4)
- [x] `LICENSE` (Apache-2.0), `NOTICE` (Graphify Apache-2.0 + obsidian-wiki MIT, NFR-7)
- [x] `.gitignore`

# Unit of Work — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Units Generation (Part 2)
**Decomposition approach** (from approved `unit-of-work-plan.md`): group by **pipeline capability + build layer**; **8 logical units (modules)** within a **single installable Python package**; in-process interface calls, downward-only; store owned by Storage Foundation and accessed via repositories only.

> Deployment model: one Python package (local, LLM-free, embedded SQLite + sqlite-vec). Units are **logical modules**, not independently deployed services. The Web Viewer is the only non-Python artifact (static HTML + D3), decoupled via the static-export contract.

---

## Code Organization Strategy (Greenfield)

```
ddthon26-trace/                      # workspace root (application code here)
├── pyproject.toml                   # package metadata, deps, entry points (mcp server, installer CLI)
├── README.md                        # Agent-readable usage + manual MCP config fallback (US-8.3/9.4)
├── NOTICE / LICENSE                 # preserve Graphify & obsidian-wiki notices (NFR-7)
├── knowledge_store/                 # main package
│   ├── types/                       # U-shared: typed result objects, enums, dataclasses (App Design Q7)
│   ├── store/                       # U1 Storage Foundation: KnowledgeStore + repositories + schema/migrations
│   ├── embedding/                   # U2 Embedding & Search: EmbeddingProvider, SearchEngine
│   ├── ingestion/                   # U3 Ingestion & Chunking: ExtractorRegistry, extractors, Chunker, ChunkVersioner
│   ├── codegraph/                   # U4 Code Structure & Relationships: CodeStructureAnalyzer, RelationshipBuilder(+strategies)
│   ├── retrieval/                   # U5 Retrieval & Summarization: SnippetBuilder, TokenEstimator, SummaryStore
│   ├── services/                    # U6: IngestionService, QueryService, SummarizationService, WikiExportService
│   ├── mcp/                         # U6: McpServer thin adapter (stdio), tool/resource registration
│   ├── wiki/                        # U7 Wiki Export: WikiExporter (static JSON/HTML export)
│   └── install/                     # U8 Installer: InstallService + CLI
├── viewer/                          # U7 Web Viewer: static HTML + D3 assets (no build step) — non-Python
└── tests/                           # mirrors package layout; Hypothesis PBT for U1/U3 (PBT Partial)
    ├── store/ embedding/ ingestion/ codegraph/ retrieval/ services/ mcp/ wiki/ install/
```

Shared `knowledge_store/types/` holds typed result objects (`ExtractionResult`, `Chunk`, `GraphResult`, `Relationship`, `MatchResult`/`VersionResult`, `SearchHit`, `SnippetResult`, `ToolResult`, `IngestionReport`, `InstallReport`, status enums) so units depend on contracts, not each other's internals.

---

## Unit Definitions

### U1 — Storage Foundation
- **Bounded context**: Knowledge Persistence.
- **Components**: C14 KnowledgeStore (SQLite connection, sqlite-vec load, schema/migrations for `<target>/.knowledge-store/`), C15 Repositories (Chunk, Graph, Relationship, Embedding, Summary).
- **Responsibilities**: own the DB connection + schema; centralize all SQL; expose repository interfaces returning typed results; `init_schema()`/`reindex()`.
- **Dependencies**: none (foundation).
- **Stories**: US-6.1 (resource persistence), US-8.2 (store init), all persistence.
- **FR/NFR**: FR-6.1, FR-8.2; NFR-3 (local).
- **PBT**: N/A directly (schema/IO).

### U2 — Embedding & Semantic Search
- **Bounded context**: Semantic Retrieval (vector layer).
- **Components**: C11 EmbeddingProvider (LocalEmbeddingProvider, offline), C9 SearchEngine (sqlite-vec vector search, ranking).
- **Responsibilities**: local/offline embedding (`embed`, `dimension`); index vectors via EmbeddingRepository; intent-based semantic search + ranking.
- **Dependencies**: U1 (EmbeddingRepository).
- **Stories**: US-3.1 (embedding infra), US-6.2 (semantic query).
- **FR/NFR**: FR-3.1, FR-6.2; NFR-1 (latency), NFR-3.1 (LLM-free/no network).

### U3 — Ingestion & Chunking
- **Bounded context**: Content Ingestion.
- **Components**: C4 ExtractorRegistry + Extractors (Markdown, PDF, Spreadsheet, Code/tree-sitter), C5 Chunker, C8 ChunkVersioner.
- **Responsibilities**: resolve file→extractor (unsupported = typed status, not exception); deterministic semantic chunking + serialize/deserialize round-trip; chunk-level versioning via similarity/hash (MinHash/edit distance), preserve history.
- **Dependencies**: U1 (ChunkRepository); Code extractor output consumed by U4.
- **Stories**: US-1.1, US-1.2, US-1.3, US-4.1, US-4.2.
- **FR/NFR**: FR-1.1–1.3, FR-4; NFR-2.2, **NFR-8.2 (PBT: chunk serialize round-trip; versioner signature determinism)**.
- **PBT (enforced)**: PBT-02/03/07/08/09 targets — Chunker round-trip invariance, ChunkVersioner deterministic signatures, extractor/parse purity.

### U4 — Code Structure & Relationships
- **Bounded context**: Code Graph & Relationships.
- **Components**: C6 CodeStructureAnalyzer (symbols + define/call/depend/inherit-contain edges, cross-file resolution, unresolved marked), C7 RelationshipBuilder + strategies (EmbeddingSimilarity, MarkdownLink, TagMatch).
- **Responsibilities**: deterministic/LLM-free code graph; connect code symbols ↔ doc chunks via 3 strategies; broken links → unresolved status.
- **Dependencies**: U1 (Graph/Relationship repos), U2 (embedding-similarity strategy + SearchEngine), U3 (extraction results / code units).
- **Stories**: US-2.1, US-2.2, US-3.1, US-3.2, US-3.3.
- **FR/NFR**: FR-2.1, FR-2.2, FR-3.1–3.3; NFR-3.1.

### U5 — Retrieval & Summarization
- **Bounded context**: Summarization + token-efficient retrieval.
- **Components**: C10 SnippetBuilder + TokenEstimator, C12 SummaryStore.
- **Responsibilities**: token-budget-aware smart-snippet scope cutting preserving semantic boundaries; estimate tokens; return content-to-summarize and persist/retrieve Agent-authored summaries (server never calls an LLM).
- **Dependencies**: U1 (Chunk/Summary repos), U3 (chunks/semantic units), U4 (symbol scopes for snippets).
- **Stories**: US-5.1, US-5.2, US-6.3, US-9.3.
- **FR/NFR**: FR-5, FR-6.2 (smart snippet); NFR-1.2 (token efficiency).

### U6 — Service Orchestration & MCP Server
- **Bounded context**: Agent Interface (MCP).
- **Components**: IngestionService, QueryService, SummarizationService, WikiExportService (orchestrators, `services/`); C1 McpServer thin stdio adapter (`mcp/`).
- **Responsibilities**: sequence pipeline components + repositories into service operations (typed reports); register self-describing MCP Resources (Structure/Summary/Relationship) + Tools (Semantic Query, Smart Snippet, Ingestion/Update, Summarize/Store/Get-summary); serialize typed results → token-efficient `ToolResult`. WikiExportService orchestrates U7's WikiExporter (post-ingestion regenerate).
- **Dependencies**: U1–U5 (all engine components + repos), U7 (WikiExporter interface, single sanctioned cross-unit call).
- **Stories**: US-6.1, US-6.2, US-6.3, US-6.4, US-9.1, US-9.2, plus orchestration of US-1.x–US-5.x.
- **FR/NFR**: FR-5, FR-6; NFR-1 (latency), NFR-5 (discoverability).

### U7 — Wiki Export & Web Viewer
- **Bounded context**: Human Wiki.
- **Components**: C13 WikiExporter (Python — static JSON/HTML export), C2 Web Viewer (static HTML + D3: TreeView, DependencyGraph, WikiContentViewer — non-Python).
- **Responsibilities**: serialize structure/graph/relationship/wiki data to static files under `<store>/wiki/` per the export contract; viewer loads via `file://`, renders tree/graph/markdown, shows latest chunk versions. No runtime server.
- **Dependencies**: U1 (read repos) for exporter; viewer depends only on the export-file contract (decoupled).
- **Stories**: US-7.1, US-7.2, US-7.3, US-7.4.
- **FR/NFR**: FR-7; NFR-2.1 (reviewers see latest).

### U8 — Installer & Packaging
- **Bounded context**: Installation.
- **Components**: C3 Installer CLI, InstallService.
- **Responsibilities**: copy system into target project; init `.knowledge-store/`; detect Claude Code (`.mcp.json`)/opencode and auto-add stdio MCP entry, else emit README manual snippet; verify prerequisites; preserve ported-code NOTICE/LICENSE.
- **Dependencies**: U1 (KnowledgeStore.init_schema), U6 (MCP server entry point referenced in config).
- **Stories**: US-8.1, US-8.2, US-8.3, US-8.4, US-9.4.
- **FR/NFR**: FR-8; NFR-4 (installability), NFR-7 (license preservation).

---

## Story coverage summary
All 28 stories across 9 Epics are assigned (see `unit-of-work-story-map.md` for the full matrix). No story is unassigned; no unit is empty.

## Build order (see `unit-of-work-dependency.md` for the matrix)
U1 → U2 → U3 → U4 → U5 → U7 (exporter core) → U6 (services + MCP, wires U7) → U8. Viewer front-end (U7) can be built any time after the export contract is fixed.

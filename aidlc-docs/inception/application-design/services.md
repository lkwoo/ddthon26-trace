# Services — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Application Design
**Design decision (Q3)**: **Dedicated orchestrator services** are the single entry point for MCP tools (and the Installer CLI). Services sequence pipeline components and repositories; they hold **orchestration** logic only — domain rules live in components, SQL lives in repositories.

---

## Service inventory

| Service | Responsibility | Primary consumers | Stories |
|---|---|---|---|
| **IngestionService** | Orchestrate ingest → chunk → version → (code) structure → relationships → embed → persist → trigger wiki export | MCP Ingestion/Update tools | US-1.x, US-2.x, US-3.x, US-4.x, US-6.4 |
| **QueryService** | Semantic query, smart snippet, resource reads | MCP Semantic Query / Smart Snippet tools + Resources | US-6.1, US-6.2, US-6.3, US-9.2, US-9.3 |
| **SummarizationService** | Provide content-to-summarize; persist/retrieve Agent summaries | MCP summarize/store/get-summary tools | US-5.1, US-5.2 |
| **WikiExportService** | Regenerate static viewer artifacts after updates | IngestionService (post-step) + explicit tool | US-7.1–7.4 |
| **InstallService** | Copy system, init store, auto-configure MCP clients | Installer CLI | US-8.1–8.4, US-9.4 |

---

## IngestionService (interactive, Agent-driven)

**Purpose**: Deterministic server-side pipeline for adding/updating knowledge; summary text is **delegated to the Agent** (server never calls an LLM — FR-5, CQ2).

**Orchestration (`ingest(paths, options) → IngestionReport`)**:
1. `ExtractorRegistry.resolve()` + `Extractor.extract()` per file → `ExtractionResult` (unsupported files reported, skipped).
2. `Chunker.chunk()` → chunks.
3. `ChunkVersioner.match()` + `apply_version()` → new vs. updated chunk versions.
4. If code: `CodeStructureAnalyzer.analyze()` + `resolve_symbols()` → graph (`GraphRepository`).
5. `EmbeddingProvider.embed()` → `EmbeddingRepository`/`SearchEngine.index()`.
6. `RelationshipBuilder.build()` (embedding + markdown-link + tag strategies) → `RelationshipRepository`.
7. Persist chunks via `ChunkRepository`.
8. Call **WikiExportService.regenerate()** so reviewers see latest (NFR-2.1).
9. Return an `IngestionReport` summarizing counts, unsupported/unresolved items, and any chunks awaiting Agent summaries.

**Boundaries**: no SQL (uses repositories); no LLM calls; deterministic given same input (US-2.1).

---

## QueryService

**Purpose**: Serve low-latency, token-efficient reads to the Agent (NFR-1.1 ≤1s target, NFR-1.2).

**Operations**:
- `semantic_query(intent, limit) → list[SearchHit]` — delegates to `SearchEngine` (US-6.2).
- `smart_snippet(target_id, token_budget) → SnippetResult` — delegates to `SnippetBuilder` (US-6.3).
- `read_structure(uri)` / `read_summary(uri)` / `read_relationships(uri)` — resource reads via `GraphRepository`/`SummaryRepository`/`RelationshipRepository` (US-6.1).

**Boundaries**: read-only; returns chunk/summary/scope-limited content (never full raw dumps) for token efficiency (US-9.3).

---

## SummarizationService

**Purpose**: Enable Agent-driven summaries without server LLM use (FR-5).

**Operations**:
- `get_content_to_summarize(id) → Content` (US-5.1).
- `store_summary(chunk_id, text)` → `SummaryRepository` (US-5.2).
- `get_summary(chunk_id) → str|None` (US-5.2).

---

## WikiExportService

**Purpose**: Produce the **pre-generated static export** (Q8) consumed by the Web Viewer via `file://`.

**Operations**:
- `regenerate(export_dir=<store>/wiki) → ExportResult` — calls `WikiExporter.export()` to write structure/graph/relationship/wiki JSON+HTML artifacts; invoked after each ingestion/update and on demand (US-7.4, NFR-2.1).

---

## InstallService

**Purpose**: Script-level installation (NFR-4 installability).

**Operations (`run(target_dir, options) → InstallReport`)**:
1. Copy system files into `target_dir` (US-8.1).
2. `KnowledgeStore.init_schema()` in `<target>/.knowledge-store/` (US-8.2).
3. Detect Claude Code (`.mcp.json`) / opencode → add stdio MCP server entry; if none detected, emit README manual snippet (US-8.3).
4. Verify minimal prerequisites; report next steps (US-8.4, US-9.4).

**Boundaries**: runs as a CLI outside the MCP server process; preserves ported-code NOTICE/LICENSE (NFR-7).

---

## Orchestration principles
- **Single entry point**: MCP tools/resources map 1:1 to service operations; the MCP layer stays thin (Q2).
- **Downward-only calls**: Services → components → repositories → KnowledgeStore. No upward or peer-service coupling except the explicit `IngestionService → WikiExportService` post-step.
- **Typed results end-to-end**: services return typed reports/results (Q7); the MCP layer serializes them into token-efficient `ToolResult` envelopes.
- **LLM-free server**: no service calls an external LLM/embedding API; embeddings are local (NFR-3.1).

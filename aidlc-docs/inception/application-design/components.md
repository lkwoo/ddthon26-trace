# Components — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Application Design
**Design decisions applied**: pipeline-stage components (Q1), thin MCP adapter (Q2), dedicated orchestrator services (Q3), repository components (Q4), pluggable extractor registry (Q5), `EmbeddingProvider` interface (Q6), typed result objects (Q7), pre-generated static viewer export (Q8).

> Scope note: This document defines **components, responsibilities, and interfaces** only. Detailed business rules (chunk-boundary heuristics, symbol-resolution rules, similarity thresholds, token-budget cutting) are deferred to **per-unit Functional Design**.

---

## Layered Overview

```
[ Agent (MCP client, stdio) ]        [ Reviewer (browser, file://) ]        [ Installer (CLI) ]
            |                                     |                                  |
   +--------v---------+                  +--------v--------+                +--------v--------+
   |  MCP Server      |  (thin adapter)  |  Web Viewer     | (static HTML)  |  Installer      |
   |  Resources/Tools |                  |  D3 assets      |                |  CLI/script     |
   +--------+---------+                  +--------+--------+                +--------+--------+
            |                                     ^                                  |
            v                                     | (static export files)            v
   +-------------------------- Service Layer (orchestrators) --------------------------+
   | IngestionService | QueryService | SummarizationService | WikiExportService | InstallService |
   +-------------------------------------+---------------------------------------------+
                                         |
                        +----------------v-----------------+  (in-process calls)
                        |     Knowledge Engine components   |
                        | ExtractorRegistry(+Extractors)    |
                        | Chunker | CodeStructureAnalyzer   |
                        | RelationshipBuilder(+Strategies)  |
                        | ChunkVersioner | SearchEngine     |
                        | SnippetBuilder | TokenEstimator   |
                        | EmbeddingProvider(iface)          |
                        +----------------+------------------+
                                         |
                        +----------------v------------------+
                        | Repositories                      |
                        | Chunk / Graph / Relationship /    |
                        | Embedding / Summary               |
                        +----------------+------------------+
                                         |
                        +----------------v------------------+
                        | KnowledgeStore (SQLite + sqlite-vec|
                        | in <target>/.knowledge-store/)    |
                        +-----------------------------------+
```

---

## 1. Interface / Boundary Components

### C1. McpServer  *(thin adapter — Q2)*
- **Purpose**: Expose the system to Agents as MCP Resources + Tools over **stdio**; contains no business logic.
- **Responsibilities**:
  - Register Resources (Structure, Summary, Relationship) as URIs (FR-6.1).
  - Register Tools (Semantic Query, Smart Snippet, Ingestion/Update, Summarize-content, Store/Get-summary) (FR-6.2).
  - Provide **self-describing** descriptions/input schemas/usage-timing for every Tool/Resource (FR-6.3, NFR-5 discoverability, US-9.1).
  - Deserialize tool inputs → call the appropriate **Service** → serialize typed results to token-efficient responses (NFR-1.2).
- **Interface (inbound)**: MCP protocol over stdio. **Outbound**: Service-layer method calls.

### C2. Web Viewer (static HTML + D3 assets)  *(client-side, non-Python)*
- **Purpose**: Human interface for P2 Reviewer.
- **Sub-components**:
  - **TreeView** — collapsible directory/logical dependency tree (FR-7.1, US-7.1; Graphify `tree_html.py` style).
  - **DependencyGraph** — D3 node/edge relationship graph (FR-7.2, US-7.2).
  - **WikiContentViewer** — renders Markdown wiki content to HTML (FR-7.3, US-7.3); shows latest chunk versions for review (FR-7.4, US-7.4).
- **Interface (inbound)**: loads **pre-generated static export artifacts** (JSON + HTML) via `file://` (Q8). No runtime server dependency.

### C3. Installer (CLI/script)
- **Purpose**: Copy the system into a target project and configure it (P3 Installer).
- **Responsibilities**:
  - Copy system files into the target project (FR-8.1, US-8.1).
  - Initialize `<target>/.knowledge-store/` (FR-8.2, US-8.2).
  - Detect Claude Code / opencode and auto-add MCP (stdio) config; else emit README manual snippet (FR-8.3, US-8.3).
  - Verify/document minimal prerequisites (FR-8.4, NFR-4, US-8.4/US-9.4).
- **Interface**: shell entry point; delegates to `InstallService`.

---

## 2. Knowledge Engine Components (pipeline stages — Q1)

### C4. ExtractorRegistry + Extractor interface  *(pluggable registry — Q5)*
- **Purpose**: Resolve a file to the correct extractor by format/language and produce raw structured content.
- **Responsibilities**:
  - Maintain a `format/language → Extractor` registry; select by extension/detection.
  - Report **unsupported** formats as a status (typed result), not an exception (Q7; US-1.1 "unsupported" scenario).
- **Concrete extractors** (each implements `Extractor`):
  - **MarkdownExtractor** (text + wikilinks/links), **PdfExtractor** (text + tables, FR-1.2), **SpreadsheetExtractor** (xlsx/csv sheets/tables, FR-1.2), **CodeExtractor** (tree-sitter multi-language, FR-2.1; Graphify extractor logic, NFR-7).
- **Interface**: `ExtractionResult extract(file_path)`.

### C5. Chunker
- **Purpose**: Split extracted content into semantic-unit chunks (section/paragraph/table) with stable identity + source metadata (FR-1.3, US-1.3).
- **Responsibilities**: deterministic chunking; serialization round-trip invariance (PBT target, NFR-8.2/US-1.3).
- **Interface**: `list[Chunk] chunk(ExtractionResult)`; `bytes serialize(chunks)` / `list[Chunk] deserialize(bytes)`.

### C6. CodeStructureAnalyzer
- **Purpose**: Build the code graph — extract symbols and relations (define/call/depend/inherit-contain) and resolve cross-file symbols (FR-2.1, FR-2.2, US-2.1, US-2.2).
- **Responsibilities**: deterministic/LLM-free extraction; mark unresolved symbols without aborting the graph (US-2.2 edge case, Q7 status field).
- **Interface**: `GraphResult analyze(code_units)` → nodes + edges (+ unresolved list).

### C7. RelationshipBuilder + RelationStrategy interface
- **Purpose**: Connect code symbols ↔ document chunks via three strategies (FR-3, Epic 3).
- **Strategies** (each implements `RelationStrategy`):
  - **EmbeddingSimilarityStrategy** (FR-3.1, US-3.1) — uses `SearchEngine`/`EmbeddingProvider` + sqlite-vec.
  - **MarkdownLinkStrategy** (FR-3.2, US-3.2) — parses `[[wikilink]]`/links; broken links → unresolved status.
  - **TagMatchStrategy** (FR-3.3, US-3.3).
- **Interface**: `list[Relationship] build(items)`.

### C8. ChunkVersioner
- **Purpose**: Chunk-level version management via text-similarity/hash matching (MinHash/edit distance) (FR-4, Epic 4).
- **Responsibilities**: deterministic signature/matching (PBT target, US-4.1 determinism); update matched OLD chunk to NEW version preserving history; unmatched → new version 1 (US-4.2).
- **Interface**: `MatchResult match(new_chunk, candidates)`; `VersionResult apply_version(match)`.

### C9. SearchEngine
- **Purpose**: Intent-based semantic search over embeddings via sqlite-vec (FR-6.2 Semantic Query, US-6.2, NFR-1).
- **Responsibilities**: embed query via `EmbeddingProvider`, run vector similarity, rank results.
- **Interface**: `list[SearchHit] search(intent, limit)`.

### C10. SnippetBuilder + TokenEstimator
- **Purpose**: Token-budget-aware "smart snippet" scope cutting (FR-6.2 Smart Snippet, US-6.3, NFR-1.2).
- **Responsibilities**: cut the most relevant minimal scope not exceeding a token budget while preserving semantic-unit boundaries; `TokenEstimator` estimates token counts.
- **Interface**: `SnippetResult build(symbol_or_chunk, token_budget)`.

### C11. EmbeddingProvider interface  *(Q6)*
- **Purpose**: Abstraction over the local, offline embedding model (NFR-3.1 LLM-free/no network).
- **Concrete**: **LocalEmbeddingProvider** (fastembed/sentence-transformers small offline).
- **Interface**: `list[Vector] embed(list[str] texts)`; `int dimension`.

### C12. SummaryStore (content extraction + summary persistence helper)
- **Purpose**: Support Agent-driven summarization (FR-5, Epic 5) — server never calls an LLM.
- **Responsibilities**: return content-to-summarize for a chunk/symbol (US-5.1); persist/retrieve Agent-authored summaries linked to chunks (US-5.2).
- **Interface**: `Content extract_for_summary(id)`; delegates persistence to `SummaryRepository`.

### C13. WikiExporter
- **Purpose**: Generate the **static export artifacts** the Web Viewer consumes (Q8; FR-7).
- **Responsibilities**: serialize structure/graph/relationship/wiki(markdown) data into JSON/HTML files under the export directory; regenerate on ingestion/update so reviewers see latest versions (US-7.4, NFR-2.1).
- **Interface**: `ExportResult export(export_dir)`.

---

## 3. Persistence Components (repositories — Q4)

### C14. KnowledgeStore (connection/schema manager)
- **Purpose**: Own the SQLite connection, load the **sqlite-vec** extension, and manage schema/migrations for `<target>/.knowledge-store/` (FR-8.2).
- **Interface**: `Connection connect()`, `init_schema()`, `reindex()` support.

### C15. Repositories *(all SQL isolated here — Q4)*
- **ChunkRepository** — chunks + chunk versions/history (FR-1.3, FR-4).
- **GraphRepository** — code graph nodes/edges (FR-2).
- **RelationshipRepository** — code↔chunk relationships incl. unresolved refs (FR-3).
- **EmbeddingRepository** — vectors via sqlite-vec (FR-3.1, FR-6.2).
- **SummaryRepository** — Agent-authored summaries linked to chunks (FR-5).
- **Rule**: no other component issues SQL directly; all persistence flows through repositories.

---

## Story / Requirement coverage map (component level)

| Component(s) | Stories | FR/NFR |
|---|---|---|
| C4 ExtractorRegistry+Extractors | US-1.1, US-1.2, US-2.1 | FR-1.1, FR-1.2, FR-2.1 |
| C5 Chunker | US-1.3 | FR-1.3, NFR-8.2 |
| C6 CodeStructureAnalyzer | US-2.1, US-2.2 | FR-2.1, FR-2.2 |
| C7 RelationshipBuilder | US-3.1, US-3.2, US-3.3 | FR-3.1–3.3 |
| C8 ChunkVersioner | US-4.1, US-4.2 | FR-4, NFR-2.2, NFR-8.2 |
| C9 SearchEngine | US-6.2 | FR-6.2, NFR-1 |
| C10 SnippetBuilder/TokenEstimator | US-6.3, US-9.3 | FR-6.2, NFR-1.2 |
| C11 EmbeddingProvider | US-3.1 | FR-3.1, NFR-3.1 |
| C12 SummaryStore | US-5.1, US-5.2 | FR-5 |
| C13 WikiExporter | US-7.1–7.4 | FR-7, NFR-2.1 |
| C14/C15 Store + Repositories | US-6.1, US-8.2, all persistence | FR-6.1, FR-8.2 |
| C1 McpServer | US-6.1–6.4, US-9.1 | FR-6, NFR-5 |
| C2 Web Viewer | US-7.1–7.4 | FR-7 |
| C3 Installer | US-8.1–8.4, US-9.4 | FR-8, NFR-4 |

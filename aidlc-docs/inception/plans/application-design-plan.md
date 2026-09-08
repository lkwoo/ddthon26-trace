# Application Design Plan — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Application Design
**Inputs**: `requirements.md`, `stories.md` (9 Epics / 28 stories), `personas.md` (P1 Agent, P2 Reviewer, P3 Installer), `execution-plan.md`
**Goal of this stage**: High-level component identification and service-layer design (interfaces & orchestration, **not** detailed business logic — that comes in per-unit Functional Design).

> **How to use this file**: Please answer every **[Answer]:** tag below by writing the letter of your choice (e.g. `[Answer]: A`). Each question lists a **Recommended** default derived from the confirmed requirements — you can simply confirm the recommendation or pick another option. If none fit, choose the **Other** option and describe. When all tags are filled, tell me you're done and I'll analyze the answers (adding follow-ups only if anything is ambiguous) before generating the design artifacts.

---

## Part A — Execution Checklist (tracked)

### A1. Context Analysis
- [x] Read requirements.md, stories.md, personas.md
- [x] Identify key business capabilities / functional areas
- [x] Determine design scope & complexity

### A2. Collect Design Decisions
- [x] Author context-appropriate questions (Part B below)
- [x] Collect all [Answer]: responses
- [x] Analyze answers for vagueness / contradiction / missing detail — all 8 = option A, coherent, no ambiguity
- [x] Add follow-up questions if ambiguity found; resolve before proceeding — none needed

### A3. Generate Mandatory Design Artifacts (after answers approved)
- [x] `application-design/components.md` — component definitions, responsibilities, interfaces
- [x] `application-design/component-methods.md` — method signatures, purpose, I/O types
- [x] `application-design/services.md` — service definitions, responsibilities, orchestration
- [x] `application-design/component-dependency.md` — dependency matrix, communication patterns, data-flow diagram
- [x] `application-design/application-design.md` — consolidated design document
- [x] Validate design completeness & consistency (content-validation rules)

---

## Part B — Design Decision Questions

The system is confirmed as: **Python**, **LLM-free server** with a **local embedding model**, **SQLite + sqlite-vec** store in `<target>/.knowledge-store/`, **MCP over stdio**, **static HTML + D3** viewer, and a **copy-style installer**. These questions resolve the remaining *structural* design decisions.

### Question 1 — Knowledge Engine decomposition (Component boundaries)
How should the core Knowledge Engine be decomposed into components?

A) **Pipeline-stage components** — one component per capability: Ingestion/Extraction, Chunking, Code Structure/Graph, Relationship Construction, Chunk Versioning, Embedding/Search, Summarization Store. (**Recommended** — matches FR-1…FR-5 boundaries and the likely units of work.)

B) **Two coarse components** — one "Document pipeline" and one "Code pipeline", each internally handling its own extraction/chunking/relationships.

C) **Single monolithic engine module** with internal functions, no separate components.

D) Other (please describe after [Answer]: tag below)

[Answer]: **Pipeline-stage components** — one component per capability: Ingestion/Extraction, Chunking, Code Structure/Graph, Relationship Construction, Chunk Versioning, Embedding/Search, Summarization Store. (**Recommended** — matches FR-1…FR-5 boundaries and the likely units of work.)

### Question 2 — MCP Server layering (Component boundaries)
How should the MCP Server relate to the engine logic?

A) **Thin MCP adapter** — the MCP Server only exposes Resources/Tools and delegates to an internal service/application API; no business logic in the MCP layer. (**Recommended** — keeps tools testable and lets the same core power ingestion, viewer export, and tests.)

B) **MCP Server contains orchestration** — tools call engine components directly with coordination logic inside the handlers.

C) Other (please describe after [Answer]: tag below)

[Answer]: **Thin MCP adapter** — the MCP Server only exposes Resources/Tools and delegates to an internal service/application API; no business logic in the MCP layer. (**Recommended** — keeps tools testable and lets the same core power ingestion, viewer export, and tests.)

### Question 3 — Service layer / orchestration (Service design)
How should multi-step operations (ingest → chunk → structure → relate → version → embed → wiki-reflect) be orchestrated?

A) **Dedicated orchestrator services** — e.g. `IngestionService`, `QueryService`, `WikiExportService`, `InstallService` — that sequence the pipeline components and are the single entry point for MCP tools. (**Recommended**.)

B) **One master service facade** that exposes every operation as a method.

C) **No service layer** — MCP tool handlers orchestrate components directly.

D) Other (please describe after [Answer]: tag below)

[Answer]: **Dedicated orchestrator services** — e.g. `IngestionService`, `QueryService`, `WikiExportService`, `InstallService` — that sequence the pipeline components and are the single entry point for MCP tools. (**Recommended**.)

### Question 4 — Data access to the Knowledge Store (Component boundaries / patterns)
How should components read/write SQLite + sqlite-vec?

A) **Repository components** — typed repositories (e.g. `ChunkRepository`, `GraphRepository`, `RelationshipRepository`, `EmbeddingRepository`, `SummaryRepository`) wrap all SQL; other components never touch SQL directly. (**Recommended** — isolates schema and eases testing/versioning.)

B) **Single DataStore/DAO component** exposing all persistence methods.

C) **Direct SQLite access** from each component as needed.

D) Other (please describe after [Answer]: tag below)

[Answer]: **Repository components** — typed repositories (e.g. `ChunkRepository`, `GraphRepository`, `RelationshipRepository`, `EmbeddingRepository`, `SummaryRepository`) wrap all SQL; other components never touch SQL directly. (**Recommended** — isolates schema and eases testing/versioning.)

### Question 5 — Parser / extractor extensibility (Design pattern)
Ingestion must handle many code languages (tree-sitter) plus Markdown/PDF/xlsx/csv. How should extractors be organized?

A) **Registry of pluggable extractors** — a format/language → extractor lookup implementing a common `Extractor` interface, so new formats/languages are added without touching the pipeline. (**Recommended** — supports FR-1.1/FR-2.1 multi-format/multi-language.)

B) **Fixed set of extractor functions** selected by a switch on file type.

C) Other (please describe after [Answer]: tag below)

[Answer]: **Registry of pluggable extractors** — a format/language → extractor lookup implementing a common `Extractor` interface, so new formats/languages are added without touching the pipeline. (**Recommended** — supports FR-1.1/FR-2.1 multi-format/multi-language.)

### Question 6 — Local embedding model abstraction (Component interface)
How should the local embedding model be represented in the design?

A) **`EmbeddingProvider` interface** with a concrete offline implementation (e.g. fastembed/sentence-transformers), so the model is swappable and mockable in tests. (**Recommended** — keeps LLM-free/local constraint behind a boundary.)

B) **Concrete embedding component** directly bound to one library, no interface.

C) Other (please describe after [Answer]: tag below)

[Answer]: **`EmbeddingProvider` interface** with a concrete offline implementation (e.g. fastembed/sentence-transformers), so the model is swappable and mockable in tests. (**Recommended** — keeps LLM-free/local constraint behind a boundary.)

### Question 7 — Method return / result style (Method contracts)
What convention should component method signatures follow for results and expected error cases (e.g. unsupported format, unresolved symbol, broken link)?

A) **Typed result objects / dataclasses**, with expected non-fatal outcomes represented as status fields on the result (e.g. `unsupported`, `unresolved`) rather than exceptions; exceptions reserved for truly unexpected failures. (**Recommended** — matches the "respond as unsupported and continue" acceptance criteria in US-1.1/US-2.2/US-3.2.)

B) **Plain dicts/tuples** as return values; errors via exceptions.

C) **Exceptions for all error/edge cases**, plain values on success.

D) Other (please describe after [Answer]: tag below)

[Answer]: **Typed result objects / dataclasses**, with expected non-fatal outcomes represented as status fields on the result (e.g. `unsupported`, `unresolved`) rather than exceptions; exceptions reserved for truly unexpected failures. (**Recommended** — matches the "respond as unsupported and continue" acceptance criteria in US-1.1/US-2.2/US-3.2.)

### Question 8 — Web Viewer data feed (Component dependency / communication)
How should the static HTML + D3 viewer obtain structure/relationship/wiki data (P2 Reviewer, Epic 7)?

A) **Pre-generated static export** — a `WikiExport` component writes JSON/HTML artifacts into `.knowledge-store/` (or a `wiki/` output dir) that the static viewer loads via `file://`; regenerated on ingestion/update. (**Recommended** — no runtime server needed, matches "static HTML + D3, no build tools".)

B) **Live query** — the viewer calls a small local HTTP endpoint that queries SQLite at load time.

C) Other (please describe after [Answer]: tag below)

[Answer]: **Pre-generated static export** — a `WikiExport` component writes JSON/HTML artifacts into `.knowledge-store/` (or a `wiki/` output dir) that the static viewer loads via `file://`; regenerated on ingestion/update. (**Recommended** — no runtime server needed, matches "static HTML + D3, no build tools".)

---

## Part C — Notes / Constraints already fixed (no question needed)
- Language/runtime: **Python**; store: **SQLite + sqlite-vec**; embeddings: **local offline model**; server: **LLM-free** (summaries authored by the Agent).
- MCP transport: **stdio**; clients auto-configured: **Claude Code (`.mcp.json`)** and **opencode**.
- Store location: `<target>/.knowledge-store/`.
- Licensing: preserve Graphify (Apache-2.0) / obsidian-wiki (MIT) NOTICE/LICENSE for ported logic (NFR-7).
- Testing: **PBT Partial** (Hypothesis) on chunking/serialization/parsing/hash-matching (NFR-8).
- Detailed business rules (chunk boundaries, symbol resolution, similarity thresholds, token-budget snippet cutting) are **deferred to per-unit Functional Design**, not decided here.

# Application Design (Consolidated) — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Application Design
**Sources**: `requirements.md`, `stories.md` (9 Epics / 28 stories), `personas.md` (P1 Agent, P2 Reviewer, P3 Installer), `application-design-plan.md` (answered)
**Companion docs**: [`components.md`](components.md), [`component-methods.md`](component-methods.md), [`services.md`](services.md), [`component-dependency.md`](component-dependency.md)

> This is the consolidated overview. It records the confirmed design decisions and links the detailed artifacts. Detailed business rules are **deferred to per-unit Functional Design** (CONSTRUCTION phase).

---

## 1. Confirmed design decisions (from answered plan)

| # | Decision | Choice |
|---|---|---|
| Q1 | Knowledge Engine decomposition | **Pipeline-stage components** (one per capability) |
| Q2 | MCP Server layering | **Thin MCP adapter** over an internal service API |
| Q3 | Service layer / orchestration | **Dedicated orchestrator services** (single entry point) |
| Q4 | Data access | **Repository components** (all SQL isolated) |
| Q5 | Parser/extractor extensibility | **Pluggable extractor registry** (`Extractor` interface) |
| Q6 | Embedding model | **`EmbeddingProvider` interface** + local offline impl |
| Q7 | Method return/error style | **Typed result objects** with status fields |
| Q8 | Web Viewer data feed | **Pre-generated static export** (loaded via `file://`) |

Pre-fixed constraints: Python, SQLite + sqlite-vec, LLM-free server, local embedding, MCP over stdio, static HTML + D3 viewer, copy-style installer, `.knowledge-store/` location, Graphify/obsidian-wiki NOTICE/LICENSE preservation, PBT Partial (Hypothesis).

---

## 2. Architecture summary

Three interfaces share one embedded knowledge store:
- **P1 Agent** → **McpServer** (thin adapter, stdio) → **Services** → **Engine components** → **Repositories** → **SQLite+sqlite-vec**.
- **P2 Reviewer** → **Web Viewer** (static D3) → reads **pre-generated export files** (decoupled from the engine).
- **P3 Installer** → **Installer CLI** → **InstallService** (copy + store init + MCP client auto-config).

The server is **deterministic and LLM-free**; summaries are authored by the Agent via tools (interactive ingestion).

(See `component-dependency.md` for the full data-flow diagram and text alternative.)

---

## 3. Component roster (see `components.md` for detail)

- **Interfaces**: C1 McpServer · C2 Web Viewer (TreeView / DependencyGraph / WikiContentViewer) · C3 Installer.
- **Engine (pipeline)**: C4 ExtractorRegistry+Extractors · C5 Chunker · C6 CodeStructureAnalyzer · C7 RelationshipBuilder(+strategies) · C8 ChunkVersioner · C9 SearchEngine · C10 SnippetBuilder/TokenEstimator · C11 EmbeddingProvider · C12 SummaryStore · C13 WikiExporter.
- **Persistence**: C14 KnowledgeStore · C15 Repositories (Chunk/Graph/Relationship/Embedding/Summary).

## 4. Service roster (see `services.md` for detail)

IngestionService · QueryService · SummarizationService · WikiExportService · InstallService.

---

## 5. Requirement / story coverage

- **FR-1 Ingestion & Chunking** → Extractors + Chunker (US-1.1/1.2/1.3).
- **FR-2 Code structure** → CodeStructureAnalyzer (US-2.1/2.2).
- **FR-3 Relationships** → RelationshipBuilder strategies (US-3.1/3.2/3.3).
- **FR-4 Versioning** → ChunkVersioner (US-4.1/4.2).
- **FR-5 Summarization (Agent-driven)** → SummaryStore + SummarizationService (US-5.1/5.2).
- **FR-6 MCP interface** → McpServer + QueryService (US-6.1–6.4, US-9.1).
- **FR-7 Web viewer** → WikiExporter + Web Viewer (US-7.1–7.4).
- **FR-8 Deployment/install** → Installer + InstallService (US-8.1–8.4).
- **NFR-1 latency/token** → QueryService, SnippetBuilder, TokenEstimator (US-9.2/9.3).
- **NFR-3 LLM-free/local** → EmbeddingProvider, no external API (US-3.1).
- **NFR-5 discoverability** → self-describing MCP tools/resources (US-9.1).
- **NFR-8 PBT Partial** → Chunker (serialize round-trip), ChunkVersioner (signature determinism), extractor/parsing purity → targeted in Functional Design/testing.

Full traceability tables live in `components.md` and `stories.md`.

---

## 6. Extension compliance summary (this stage)

| Extension | Status at Application Design | Rationale |
|---|---|---|
| Security Baseline | **Disabled** | Opted out at Requirements Analysis; not enforced. |
| Property-Based Testing (Partial) | **Enabled — noted, N/A to enforce here** | Application Design defines interfaces, not tests/code. PBT round-trip/determinism obligations recorded against Chunker (C5) and ChunkVersioner (C8) as design intent; PBT-02/03/07/08/09 are enforced in NFR/Code/Test stages, not this one. |
| Resiliency Baseline | **Disabled** | Opted out at Requirements Analysis; not enforced. |

No blocking findings: the only enabled extension (PBT Partial) is not applicable to interface/service design and is deferred to the stages where tests/code are produced. Typed-result design (Q7) and deterministic components (Chunker/ChunkVersioner) are structured to make the PBT obligations satisfiable downstream.

---

## 7. Handoff to Units Generation
The pipeline-stage components, repositories, and services map cleanly to candidate units of work; a dependency-respecting build order is proposed at the end of `component-dependency.md`. Units Generation will formalize units, dependencies, and story-to-unit mapping.

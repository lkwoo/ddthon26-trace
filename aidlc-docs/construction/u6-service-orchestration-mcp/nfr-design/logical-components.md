# U6 Service Orchestration & MCP Server — Logical Components

**Stage**: CONSTRUCTION → NFR Design
**Unit**: `u6-service-orchestration-mcp`

Concrete classes mapped to `components.md` (C1) and `services.md` orchestrators.

---

| Class / function (file) | Component / service | Role (one line) |
|---|---|---|
| `KnowledgeSystem` (`services/system.py`) | composition root | Wires store, repositories, and all engine components for one target. |
| `IngestionService` (`services/services.py`) | IngestionService | Orchestrates extract→chunk→version→graph→embed→relate→persist→export; returns `IngestionReport`. |
| `QueryService` (`services/services.py`) | QueryService | Read-only: `semantic_query`, `smart_snippet`, `read_structure`, `read_relationships`, `read_summary`. |
| `SummarizationService` (`services/services.py`) | SummarizationService | Agent-driven summaries: content-to-summarize, store, get (no server LLM). |
| `WikiExportService` (`services/services.py`) | WikiExportService | Regenerates static viewer artifacts via `WikiExporter` (sanctioned post-ingest edge). |
| `ToolSpec` (`mcp/tools.py`) | C1 (self-describing tool) | Name + description + when_to_use + input_schema + handler; `manifest()`. |
| `ToolRegistry` (`mcp/tools.py`) | C1 | Holds ToolSpecs; `names`/`manifest`/`get`/`call` with typed `ToolResult` dispatch. |
| `build_registry(system)` (`mcp/tools.py`) | C1 | Instantiates the 4 services and 9 tool specs. |
| `main` / `_run_stdio` (`mcp/server.py`) | C1 McpServer (thin adapter) | stdio entry point; maps ToolSpecs to MCP tools or prints manifest if `mcp` absent. |

## Tools registered (9)
`ingest`, `semantic_query`, `smart_snippet`, `get_content_to_summarize`,
`store_summary`, `get_summary`, `read_structure`, `read_relationships`,
`regenerate_wiki`.

## Collaborators (downward)
| Collaborator | Unit | Used by |
|---|---|---|
| ExtractorRegistry, Chunker, ChunkVersioner | U3 | IngestionService |
| CodeStructureAnalyzer, RelationshipBuilder(+strategies) | U4 | IngestionService |
| SearchEngine, EmbeddingProvider | U2 | Ingestion/QueryService |
| SnippetBuilder, TokenEstimator, SummaryStore | U5 | Query/SummarizationService |
| Repositories, KnowledgeStore | U1 | all services (read/write) |
| WikiExporter | U7 | WikiExportService (single sanctioned edge) |

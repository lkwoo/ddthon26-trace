# U6 Service Orchestration & MCP Server — Business Logic Model

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u6-service-orchestration-mcp`
**Packages**: `knowledge_store/services/`, `knowledge_store/mcp/`
**Components**: IngestionService, QueryService, SummarizationService,
WikiExportService (orchestrators, Q3); C1 McpServer thin adapter (Q2);
ToolRegistry / ToolSpec self-describing registry.

---

## Responsibilities

U6 is the agent interface. It **orchestrates** engine components (U1–U5, U7)
into service operations returning typed reports, and exposes them as
self-describing MCP tools over stdio. It holds no domain rules, no SQL, and no
LLM calls.

1. **KnowledgeSystem** — composition root. Constructs the store, repositories,
   engine components (registry, chunker, versioner, search, analyzer,
   token estimator, snippet builder, summary store, exporter, relationship
   builder) once, sizing the sqlite-vec table to `provider.dimension`.
2. **IngestionService.ingest(paths, export=True)** — deterministic pipeline:
   resolve+extract → chunk → version → (code) graph → embed all latest →
   build relationships → collect pending summaries/unresolved → optional wiki
   regenerate. Returns `IngestionReport`.
3. **QueryService** — `semantic_query`, `smart_snippet`, `read_structure`,
   `read_relationships`, `read_summary`. Read-only, token-efficient.
4. **SummarizationService** — `get_content_to_summarize`, `store_summary`,
   `get_summary`; server never authors summary text (FR-5).
5. **WikiExportService.regenerate** — delegates to `WikiExporter.export`; the
   single sanctioned cross-orchestration call is `IngestionService → WikiExportService`.
6. **ToolRegistry / ToolSpec** — each tool carries description + `when_to_use` +
   `input_schema` + handler; `call` dispatches to services and returns typed
   `ToolResult`.
7. **stdio server (`mcp/server.py`)** — thin adapter: maps each ToolSpec to an
   MCP tool when `mcp` is installed, else prints the manifest.

---

## Flow — Ingestion pipeline

```
ingest(paths)
  for each path:
    exists? --no--> report.unsupported += "path (not found)"
    registry.extract(path)
       UNSUPPORTED/ERROR --> report.unsupported ; continue
       OK: ingested_files++ ; if is_code -> collect CodeUnit
           chunker.chunk -> versioner.match/apply_version -> chunks_new/updated
  if code_units: analyzer.analyze -> graph.add_node/add_edge/commit ; unresolved+
  search.index_many(all_latest)             # embed
  relationship_builder.build(all_latest) -> relationships.add_many ; unresolved+
  report.pending_summaries = summary_store.pending()
  if export: WikiExportService.regenerate()   # sanctioned cross-orchestration edge
  return IngestionReport
```

## Flow — MCP tool call (thin adapter)

```
Agent --stdio--> server.call_tool(name, arguments)
                     |
              ToolRegistry.call(name, args)
                 |            |
        unknown --+           +-- ToolSpec.handler(args)
        ToolResult(NOT_FOUND)      |  validate required args -> ERROR if missing
                                   |  Service.<op>(...) -> typed result
                                   v
                          ToolResult(status, data) --to_json--> TextContent
```

## Flow — Composition root

```
KnowledgeSystem(target_dir)
  provider = get_default_provider()
  store.connect(); store.init_schema(embedding_dimension=provider.dimension)
  repos = Repositories(store)
  build engine components + relationship strategies
build_registry(system) -> instantiates the 4 services + 9 ToolSpecs
```

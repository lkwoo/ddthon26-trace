# U6 Service Orchestration & MCP Server — NFR Design Patterns

**Stage**: CONSTRUCTION → NFR Design
**Unit**: `u6-service-orchestration-mcp`

---

## Patterns applied

### 1. Thin adapter (App Design Q2)
`mcp/server.py` contains no business logic. `_run_stdio` maps each ToolSpec to
an MCP `Tool` and forwards `call_tool` → `registry.call` → `ToolResult.to_json`.
The `mcp` package is optional: `ImportError` or `--manifest` prints the JSON
manifest and returns 0 (graceful degradation, manual-config fallback).

### 2. Dedicated orchestrator services (Q3)
`IngestionService`, `QueryService`, `SummarizationService`, `WikiExportService`
are the single entry point for tools. Each sequences components/repositories and
returns typed reports; domain rules stay in components, SQL in repositories.

### 3. Assembly / composition root
`KnowledgeSystem` constructs the store, repositories, and every engine component
once, sizing sqlite-vec to `provider.dimension`. Services and the registry take
the system by injection — one consistent wiring for server and installer.

### 4. Self-describing tool registry with "when to use" guidance
`ToolSpec` bundles `description` + `when_to_use` + `input_schema`; `ToolRegistry`
exposes `names`, `manifest`, `get`, `call`. This realizes NFR-5 / FR-6.3 /
US-9.1 discoverability so agents self-select and time tools.

### 5. Typed result envelopes (Q7)
All operations return dataclasses with explicit `Status`. `ToolResult` wraps
them; `to_json` compactly serializes any typed payload (NFR-1.2). Unknown tool →
`NOT_FOUND`, missing arg → `ERROR`, unknown target → `NOT_FOUND`.

### 6. Single sanctioned cross-orchestration edge
`IngestionService → WikiExportService.regenerate()` post-ingestion is the only
peer-service call (NFR-2.1 reviewers see latest); all other flow is downward.

---

## NFR mechanism map

| NFR | Mechanism |
|---|---|
| NFR-1.2 token efficiency | scope-limited reads + compact `ToolResult.to_json` |
| NFR-3.1 LLM-free | no service/adapter LLM calls; Agent-authored summaries |
| NFR-5 discoverability | self-describing `ToolSpec` manifest (printable w/o `mcp`) |

Security / Resiliency design patterns: **N/A** (local stdio, offline, single
process; typed `Status` instead of exception/retry surfaces).

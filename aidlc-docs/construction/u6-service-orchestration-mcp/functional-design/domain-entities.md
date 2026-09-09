# U6 Service Orchestration & MCP Server — Domain Entities

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u6-service-orchestration-mcp`

U6 defines the MCP-facing envelopes and consumes the shared typed contracts from
`knowledge_store/types/results.py` (App Design Q7). It persists no schema of its
own.

---

## Entities

### ToolResult (envelope returned by every tool)
| Field | Type | Notes |
|---|---|---|
| `status` | `Status` | `OK` / `NOT_FOUND` / `ERROR` / … |
| `data` | `Any` | typed result (report/hit/snippet/content/summary/dict) |
| `message` | `str` | error/diagnostic text |

`to_json()` emits compact JSON (`separators=(",",":")`) via `_jsonable`
(recurses dataclasses / `to_dict`) for token efficiency (NFR-1.2).

### ToolSpec (self-describing tool descriptor — `mcp/tools.py`)
| Field | Type | Notes |
|---|---|---|
| `name` | `str` | tool id |
| `description` | `str` | what it does |
| `when_to_use` | `str` | usage-timing guidance (FR-6.3, US-9.1) |
| `input_schema` | `dict` | JSON schema of arguments |
| `handler` | `Callable[[dict], ToolResult]` | dispatch target (not in manifest) |

`manifest()` exposes name/description/when_to_use/inputSchema.

### IngestionReport (produced by IngestionService.ingest)
| Field | Type | Notes |
|---|---|---|
| `status` | `Status` | pipeline outcome |
| `ingested_files` | `int` | OK extractions |
| `chunks_new` / `chunks_updated` | `int` | version accounting |
| `unsupported` | `list[str]` | skipped/missing/unsupported paths |
| `unresolved` | `list[str]` | unresolved symbols/relationships (sorted, unique) |
| `pending_summaries` | `list[str]` | chunk ids awaiting Agent summaries |

### Consumed contracts
`SearchHit`, `SnippetResult`, `Content`, `Summary`, `ExportResult`, `Status`,
`EdgeType`, `RelationType`, `CodeUnit` (from `codegraph.analyzer`).

---

## Testable Properties (PBT-01)

| ID | Property | Where | Status |
|---|---|---|---|
| PBT-03 | monotonic estimate; snippet `estimated_tokens <= budget` | owned by **U5** (`TokenEstimator`/`SnippetBuilder`) | **Enforced** — U5 PBT tests; surfaced via U6 `smart_snippet` |
| PBT (adv.) | unknown tool ⇒ `NOT_FOUND`; missing required arg ⇒ `ERROR` | `ToolRegistry.call` | Advisory — `tests/mcp/test_tools.py` |
| PBT (adv.) | manifest self-describing (desc + when_to_use + object schema) | `ToolRegistry.manifest` | Advisory — `tests/mcp/test_tools.py` |
| PBT (adv.) | re-ingest identical content bumps version, no duplicate | `IngestionService.ingest` | Advisory — `tests/services/test_pipeline.py` |
| PBT (adv.) | every `ToolResult.to_json()` is valid JSON | `ToolResult` | Advisory — `tests/mcp/test_tools.py` |

Enforced PBT-03 monotonicity + budget invariants live in U5. Security /
Resiliency properties: **N/A** for this unit.

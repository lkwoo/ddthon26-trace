# U6 Service Orchestration & MCP Server — NFR Requirements

**Stage**: CONSTRUCTION → NFR Requirements
**Unit**: `u6-service-orchestration-mcp`

---

## Applicable NFRs

### NFR-1 Performance (latency & token efficiency)
- **NFR-1.1** Core read tools (`semantic_query`, `smart_snippet`,
  `read_structure`, `read_relationships`, `read_summary`) are in-process,
  single-call orchestrations targeting ≤ 1 s. Ingestion may be heavier but is
  explicit and agent-triggered.
- **NFR-1.2** `ToolResult.to_json` uses compact separators; results are
  scope-limited (snippets, ranked previews, typed reports) rather than raw
  dumps (US-9.3).

### NFR-3 Cost & Resources (LLM-free)
- **NFR-3.1** No service or the MCP adapter calls an external LLM / embedding /
  network API. Embeddings are local (via U2 provider); summaries are
  Agent-authored (FR-5). Fully offline over stdio.

### NFR-5 Discoverability (self-describing tools)
- **NFR-5.1 / FR-6.3 / US-9.1** Every tool exposes `description`, `when_to_use`,
  and `input_schema` via the registry manifest, so agents autonomously discover
  and correctly time tool calls without manual setup. The manifest is printable
  even without the `mcp` package (manual-config fallback).

---

## Non-applicable NFRs

| NFR | Determination | Rationale |
|---|---|---|
| Security extension | **N/A** | Local stdio, single process, no auth/secrets/network exposure; runs inside the user's trusted project. |
| Resiliency extension | **N/A** | No remote dependencies; expected outcomes returned as typed `Status` (NOT_FOUND/ERROR/UNSUPPORTED) rather than exceptions; `mcp` absence handled gracefully. |

## PBT (Partial ON)
- Enforced PBT-03 invariants are owned by U5; U6 is validated by end-to-end
  pipeline and registry tests (advisory PBT-10 style).

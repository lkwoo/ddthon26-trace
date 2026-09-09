# U6 Service Orchestration & MCP Server — Business Rules

**Stage**: CONSTRUCTION → Functional Design
**Unit**: `u6-service-orchestration-mcp`

Rules as implemented in `services/system.py`, `services/services.py`,
`mcp/tools.py`, `mcp/server.py`. Traceability: FR-5, FR-6, US-6.2, US-6.3,
US-9.1, US-9.3, NFR-1.2, NFR-3.1, NFR-5.

---

## Orchestration boundaries

- **R6-1** Services perform **orchestration only** — they sequence engine
  components and repositories and return typed reports. **No SQL** (all
  persistence via repositories, Q4) and **no LLM/network calls** (NFR-3.1).
- **R6-2 (FR-5)** The server **never generates summary text**.
  `SummarizationService.get_content_to_summarize` returns raw `Content`;
  `store_summary` persists only Agent-authored text.
- **R6-3** Calls are **downward-only** (services → components → repositories).
  The **single sanctioned cross-orchestration edge** is
  `IngestionService → WikiExportService` as a post-ingestion step (NFR-2.1); no
  other peer-service coupling exists.
- **R6-4** `KnowledgeSystem` is the **single composition root**; the sqlite-vec
  embedding table is sized to `provider.dimension` so index and provider match.

## Ingestion rules

- **R6-5** A missing path is reported in `IngestionReport.unsupported` as
  `"path (not found)"` and skipped — not raised.
- **R6-6** `Status.UNSUPPORTED` / `Status.ERROR` extractions are recorded in
  `unsupported` and skipped; only `OK` extractions increment `ingested_files`.
- **R6-7** Each chunk is matched against same-source candidates; `is_new`
  increments `chunks_new`, otherwise `chunks_updated` (re-ingesting identical
  content bumps version, never duplicates — US-4.x).
- **R6-8** Unresolved graph symbols and unresolved relationships are aggregated,
  de-duplicated and sorted (`unresolved = sorted(set(...))`).
- **R6-9** `pending_summaries` is populated from `SummaryStore.pending()` so the
  Agent knows which chunks await summaries.
- **R6-10** Wiki export runs only when `export=True` (default), keeping tests and
  batch ingests fast.

## Query rules

- **R6-11 (US-9.3, NFR-1.2)** Reads are token-efficient: `smart_snippet` returns
  a budget-bounded scope; `semantic_query` returns ranked hits with short
  previews — never full raw dumps.
- **R6-12** `smart_snippet` on an unknown `target_id` returns
  `SnippetResult(status=NOT_FOUND)`; it does not raise.

## MCP tool / adapter rules

- **R6-13 (FR-6.3, US-9.1, NFR-5)** Every tool is **self-describing**: each
  `ToolSpec` carries `description`, `when_to_use`, and `input_schema`; the
  manifest exposes all three so agents discover and time calls without manual
  instructions.
- **R6-14** Tools return typed `ToolResult` envelopes serialized via `to_json`
  (compact separators) for token efficiency (NFR-1.2).
- **R6-15** Unknown tool name ⇒ `ToolResult(status=NOT_FOUND)`; missing required
  argument (e.g. `intent`, `target_id`, `paths/path`) ⇒
  `ToolResult(status=ERROR)`.
- **R6-16** The stdio server is a **thin adapter** (Q2): no business logic; it
  maps ToolSpecs to MCP tools and delegates to `registry.call`.
- **R6-17** The `mcp` package is **optional**: if absent (`ImportError`) or with
  `--manifest`, `main` prints the JSON tool manifest and returns 0, so the
  interface stays inspectable for manual configuration.

## Extension compliance (PBT Partial ON)
- PBT enforcement for U6 is at the **end-to-end pipeline** level
  (`tests/services/test_pipeline.py`, `tests/mcp/test_tools.py`); U5 owns the
  PBT-03 property invariants. Security / Resiliency: **N/A** (local stdio,
  offline, LLM-free; typed `Status` replaces exception-based error handling).

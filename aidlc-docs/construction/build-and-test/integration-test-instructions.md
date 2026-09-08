# Integration Test Instructions

## Purpose
Verify the four units interoperate through the assembled composition root (U4):
ingestion feeds the engine (U1), and both the MCP surface (U2) and web viewer
(U3) read/merge that knowledge consistently.

## Test Scenarios (implemented in `tests/integration/test_end_to_end.py`)

### Scenario 1: U4 → U1 ingest → U2 MCP resources
- **Description**: After `sync.run(full)`, MCP `structure`/`summary/{target}`/`relationships` resources resolve.
- **Setup**: assemble app on a temp project with a `.py` (with call edges) + `.md`.
- **Expected**: non-empty structure; summary target matches; relationship graph has nodes.

### Scenario 2: U2 MCP tools over U1
- **Description**: `query` (keyword) and `snippet` (token budget) tools return valid, budget-respecting results.
- **Expected**: query results non-empty; `estimated_tokens ≤ budget`.

### Scenario 3: U2 update_note → U3 web viewer (engine-first merge)
- **Description**: A note submitted via the MCP `update_note` tool appears in the U3 `/summary/{target}` page alongside the engine section.
- **Expected**: HTTP 200; note body and engine badge both present in HTML.

### Scenario 4: Re-sync preserves agent notes (US-E5 / BR-9)
- **Description**: After a note is added, a full re-sync regenerates the engine summary but keeps the agent note.
- **Expected**: `merged.engine` present; note body still in `merged.agent_notes`.

### Scenario 5: U3 tree + graph render after ingest
- **Description**: `/` renders the file in the tree; `/graph` renders the dependency graph.
- **Expected**: HTTP 200; file path in tree; "Dependency Graph" heading present.

## Setup Integration Test Environment
No external services, containers, or databases. Tests use `tmp_path` projects and
a file-based store; the web viewer is exercised via `WebApp.handle(path)` (no live
socket needed).

## Run Integration Tests
```bash
.venv/bin/python -m pytest -q tests/integration
```

### Verify Service Interactions
- **Expected Results**: all integration scenarios pass (5 tests), 0 failures.
- **Logs Location**: pytest stdout; `measure()` emits elapsed-ms logs via stdlib logging.

### Cleanup
None required — `tmp_path` fixtures are auto-removed by pytest.

## Manual live-server smoke (optional)
```bash
agentic-kb ingest --project <path> --store /tmp/kb
agentic-kb serve-web --project <path> --store /tmp/kb --port 8080   # open http://127.0.0.1:8080
agentic-kb serve-mcp --project <path> --store /tmp/kb               # requires [mcp] extra; wire into an MCP client
```

# Integration Test Instructions

Integration here means exercising **multiple units together** through the
orchestrator services and the two external interfaces (MCP tools, static wiki
export). These are covered by `tests/services/test_pipeline.py` and
`tests/mcp/test_tools.py`, plus a manual end-to-end check below.

## Automated integration (part of `pytest`)
- **Full ingest pipeline** (U1+U2+U3+U4+U5+U6+U7): `test_full_ingest_and_query`
  writes a small project (markdown with `[[wikilink]]` + `#tags`, Python with a
  class/inheritance/calls), ingests it, and asserts:
  - status OK, files ingested, chunks created;
  - `semantic_query` returns a ranked list;
  - `read_structure` contains the expected code symbols.
- **Typed error paths**: `test_unsupported_and_missing_files_are_reported`
  (missing file + unsupported extension → typed report, no exception).
- **Versioning across re-ingest** (U3↔U1): `test_reingest_bumps_version_not_duplicate`
  (identical content → updated, not duplicated).
- **Agent-driven summarization** (U5↔U6, FR-5): `test_summarization_is_agent_driven`
  (server returns content to summarize; agent stores summary; retrieval works).
- **MCP tool surface** (U6): `test_manifest_is_self_describing`,
  typed NOT_FOUND / ERROR paths, JSON serialization of `ToolResult`.

Run just the integration-style tests:
```bash
.venv/bin/python -m pytest tests/services tests/mcp -q
```

## Manual end-to-end (both interfaces)
```bash
# 1) init an isolated store in a scratch project
knowledge-store install /tmp/ks_demo

# 2) ingest some files
knowledge-store ingest /tmp/ks_demo/*.md /tmp/ks_demo/*.py --target /tmp/ks_demo

# 3) Agent interface: inspect the self-describing tools
knowledge-store-mcp --manifest       # KNOWLEDGE_STORE_TARGET=/tmp/ks_demo

# 4) Human interface: the static wiki was exported under the store dir
ls /tmp/ks_demo/.knowledge-store/wiki   # structure.json, relationships.json, wiki.json, index.html, app.js, styles.css
python -m http.server -d /tmp/ks_demo/.knowledge-store/wiki
# open http://localhost:8000 → Structure Tree / Dependency Graph / Wiki tabs
```

## Cross-unit contracts verified
- Storage repositories are the only SQL boundary (U1) — all other units use them.
- The single sanctioned cross-orchestration edge `IngestionService → WikiExporter`
  (U6→U7) refreshes the viewer after ingest.
- Static-export contract (U7) decouples Python from the D3 viewer (no server).

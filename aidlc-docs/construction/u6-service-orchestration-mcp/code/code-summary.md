# U6 Service Orchestration & MCP Server — Code Summary

**Stage**: CONSTRUCTION → Code Generation
**Unit**: `u6-service-orchestration-mcp`
**Status**: Code generation complete (code already written and tested).

---

## Files

| File | Description |
|---|---|
| `knowledge_store/services/system.py` | `KnowledgeSystem` — composition root wiring store, repositories, and all engine components; sizes sqlite-vec to `provider.dimension`. |
| `knowledge_store/services/services.py` | `WikiExportService`, `IngestionService`, `QueryService`, `SummarizationService` orchestrators. |
| `knowledge_store/services/__init__.py` | Exports the composition root and four services. |
| `knowledge_store/mcp/tools.py` | `ToolSpec`, `ToolRegistry`, `build_registry` — 9 self-describing tools dispatching to services, returning `ToolResult`. |
| `knowledge_store/mcp/server.py` | `main` / `_run_stdio` — thin stdio adapter; prints manifest if `mcp` absent or `--manifest`. |
| `knowledge_store/mcp/__init__.py` | Exports `ToolRegistry`, `ToolSpec`, `build_registry`. |

## Key public API

```python
KnowledgeSystem(target_dir, *, in_memory=False)     # .close(), .wiki_dir
IngestionService(system).ingest(paths, *, export=True) -> IngestionReport
QueryService(system).semantic_query(intent, limit=5) -> list[SearchHit]
QueryService(system).smart_snippet(target_id, token_budget) -> SnippetResult
QueryService(system).read_structure() / read_relationships(src_id) / read_summary(chunk_id)
SummarizationService(system).get_content_to_summarize/store_summary/get_summary
WikiExportService(system).regenerate(export_dir=None) -> ExportResult
build_registry(system) -> ToolRegistry            # .names/.manifest/.get/.call
knowledge_store.mcp.server.main(argv) -> int      # stdio or manifest
```

## Tests exercising this unit

| Test | What it covers | Result |
|---|---|---|
| `tests/services/test_pipeline.py::test_full_ingest_and_query` | end-to-end ingest→graph→query (PBT-10 style) | pass |
| `...::test_unsupported_and_missing_files_are_reported` | typed unsupported/missing handling | pass |
| `...::test_reingest_bumps_version_not_duplicate` | version bump, no duplicate | pass |
| `...::test_summarization_is_agent_driven` | FR-5 Agent-authored summary flow | pass |
| `tests/mcp/test_tools.py::test_manifest_is_self_describing` | FR-6.3/US-9.1 discoverability | pass |
| `...::test_unknown_tool_returns_typed_not_found` | unknown tool → NOT_FOUND | pass |
| `...::test_missing_required_arg_is_typed_error` | missing arg → ERROR | pass |
| `...::test_read_structure_on_empty_store` | OK on empty store | pass |
| `...::test_result_serializes_to_json` | `ToolResult.to_json` valid JSON | pass |

Whole suite: **36 tests green** (including Hypothesis PBT owned by U5). Code
generation for U6 is complete; no changes required.

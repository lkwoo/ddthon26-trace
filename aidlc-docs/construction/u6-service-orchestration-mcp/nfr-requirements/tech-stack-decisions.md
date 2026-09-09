# U6 Service Orchestration & MCP Server — Tech Stack Decisions

**Stage**: CONSTRUCTION → NFR Requirements
**Unit**: `u6-service-orchestration-mcp`

---

## Decisions

| Concern | Decision | Rationale |
|---|---|---|
| Orchestration | **Plain Python service classes** over a composition root (`KnowledgeSystem`) | Deterministic, dependency-injected wiring (Q3); no framework overhead; testable with `tmp_path` stores. |
| Tool registry | **In-house `ToolRegistry` / `ToolSpec` dataclasses**, independent of `mcp` | Self-describing manifest (FR-6.3) and dispatch are unit-testable without the transport; keeps the adapter thin (Q2). |
| MCP transport | **Optional `mcp` package over stdio** (`pip install 'knowledge-store[mcp]'`) | Local, offline agent interface; when absent, `main` prints the manifest so the interface stays inspectable (graceful degradation). |
| Result serialization | **`ToolResult.to_json` with compact separators** + recursive `_jsonable` | Token-efficient envelopes (NFR-1.2); handles dataclasses/enums/`to_dict` uniformly. |
| Error handling | **Typed `Status`** (NOT_FOUND / ERROR / UNSUPPORTED) not exceptions | Expected outcomes are data, not failures (Q7). |
| Embedding sizing | **`init_schema(embedding_dimension=provider.dimension)`** | sqlite-vec table matches the local provider (NFR-3.1 local embeddings). |
| Async | **`asyncio.run` only inside `_run_stdio`** | Async confined to the transport edge; services stay synchronous and simple. |
| Testing | **pytest** with `tmp_path` fixtures; whole suite 36 tests | Fast, hermetic, offline; PBT-09 property tests owned by U5 run in the same suite. |

## Justification — LLM-free stdio server (NFR-3.1)
The server exposes retrieval/summarization capabilities but delegates all
summary *authoring* to the calling agent (FR-5). This removes API cost and
network latency and keeps the whole system runnable offline. The `mcp` package
is the only optional runtime dependency; core logic and tests run without it.

## Dependencies
- Runtime (core): Python stdlib + internal units U1–U5, U7.
- Runtime (optional): `mcp` (stdio transport).
- Test-only: `pytest`, `hypothesis` (shared suite).

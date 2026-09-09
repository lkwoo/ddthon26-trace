# U8 — Installer & Packaging · Business Logic Model

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u8-installer-packaging`
**Components documented**: C3 Installer CLI, InstallService; packaging (`pyproject.toml`)

> Scope: copy-style installation. Initialize the isolated `.knowledge-store/`,
> auto-detect Claude Code / opencode and merge a stdio MCP entry, else emit a
> README manual snippet. Console-script entry points + optional extras keep the
> package dependency-light (Epic 8, NFR-4).

---

## 1. Responsibilities

### InstallService (`knowledge_store/install/service.py`)
- `run(target_dir, *, init_store=True) -> InstallReport`:
  1. Resolve + `mkdir` the target; build an `InstallReport(status=OK)`.
  2. **Init store** (US-8.2): `KnowledgeStore(target).connect() → init_schema() →
     close()`; record `store_dir = <target>/.knowledge-store/`.
  3. **Detect + configure clients** (US-8.3): if `_is_claude` merge into
     `.mcp.json`; if `_is_opencode` merge into `opencode.json`/`.opencode.json`.
  4. **Fallback**: if no client configured, set `manual_snippet` + guidance
     `message`; else set a "Configured MCP clients: …" message.
- `manual_snippet(target)` — standalone helper returning the README fallback
  JSON (`mcpServers.knowledge-store` stdio entry).
- Config merge helpers `_load`/`_save` read-modify-write JSON, using
  `setdefault` so unrelated entries are preserved (BR).

### Installer CLI (`knowledge_store/install/cli.py`)
Argparse `knowledge-store` with 4 subcommands:
- `install [TARGET] [--no-store]` → `InstallService.run`, prints report + snippet.
- `init [TARGET]` → store init only.
- `ingest PATH... [--target]` → `IngestionService.ingest`, prints JSON report.
- `manifest [--target]` → prints self-describing MCP tool manifest (in-memory).

### Packaging (`pyproject.toml`)
- setuptools/pyproject build; `dependencies = []` (core deps empty).
- Optional extras: `mcp`, `embeddings`, `vec`, `code`, `docs`, `test`, `all`.
- `console_scripts`: `knowledge-store` (CLI) and `knowledge-store-mcp` (server).

---

## 2. Flow

```
$ knowledge-store install <target>
        |
        v
InstallService.run(target)
   mkdir target
   init_store? --yes--> KnowledgeStore(target).init_schema()  -> store_dir set
        |
        v
   _is_claude(target)?  (.mcp.json | .claude)   --yes--> _configure_claude  (merge mcpServers)
   _is_opencode(target)? (opencode.json|...)    --yes--> _configure_opencode(merge mcp)
        |
        +-- any configured? --no--> report.manual_snippet = manual_snippet(target)
        |                            report.message = "add manual snippet (README)"
        +-- yes -------------------> report.message = "Configured MCP clients: ..."
        v
InstallReport(status, target_dir, store_dir, configured_clients, manual_snippet, message)
        |
        v
CLI prints target / store / message / (manual snippet if present)
```

---

## 3. ASCII sketch (real names)

```
knowledge_store/install/service.py
  InstallService.run(target_dir, init_store=True) -> InstallReport
     KnowledgeStore.init_schema()            # US-8.2
     _is_claude / _is_opencode               # US-8.3 detection
     _configure_claude  -> .mcp.json  {"mcpServers":{"knowledge-store": _server_entry}}
     _configure_opencode-> opencode.json {"mcp":{"knowledge-store": {type:"local",...}}}
     _load / _save (merge, never clobber)
  manual_snippet(target) -> README fallback JSON

knowledge_store/install/cli.py
  main -> build_parser -> {install, init, ingest, manifest}

pyproject.toml
  [project.scripts] knowledge-store, knowledge-store-mcp
  [optional-dependencies] mcp/embeddings/vec/code/docs/test/all
```

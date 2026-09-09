# U8 — Installer & Packaging · Code Summary

**Stage**: CONSTRUCTION → Code Generation (per-unit)
**Unit**: `u8-installer-packaging`
**Status**: Code generation complete (documenting existing, tested code).

---

## Files

| File | Description |
|---|---|
| `knowledge_store/install/service.py` | `InstallService.run` — resolves target, inits `.knowledge-store/`, detects Claude Code / opencode, merges MCP entry or emits `manual_snippet`; returns `InstallReport`. Merge helpers `_load`/`_save` preserve unrelated entries. |
| `knowledge_store/install/cli.py` | `knowledge-store` argparse CLI: subcommands `install`, `init`, `ingest`, `manifest`; `main` dispatches to handlers. |
| `knowledge_store/install/__init__.py` | Package init; exports `InstallService`, `manual_snippet`. |
| `pyproject.toml` (root) | setuptools/pyproject metadata; `dependencies = []`; optional extras (`mcp`, `embeddings`, `vec`, `code`, `docs`, `test`, `all`); `console_scripts` `knowledge-store` + `knowledge-store-mcp`; package-data `viewer/**/*`. |

## Key public API

- `InstallService().run(target_dir: str, *, init_store: bool = True) -> InstallReport`
- `manual_snippet(target: str) -> str` (README fallback JSON)
- CLI `main(argv=None) -> int`; subcommands `install [TARGET] [--no-store]`,
  `init [TARGET]`, `ingest PATH... [--target]`, `manifest [--target]`.
- Entry points: `knowledge-store` → `install.cli:main`; `knowledge-store-mcp` →
  `mcp.server:main`.

## Tests exercising the unit

`tests/install/test_install.py` — **5 tests, all passing**:
- `test_install_initializes_isolated_store` — `.knowledge-store/` created, status OK.
- `test_no_client_detected_yields_manual_snippet` — empty `configured_clients`,
  valid `manual_snippet` JSON.
- `test_detects_and_configures_claude` — `.mcp.json` gains `knowledge-store` with
  command `knowledge-store-mcp`.
- `test_configure_preserves_existing_entries` — pre-existing `mcpServers.other`
  survives while `knowledge-store` is added (merge/idempotence).
- `test_manual_snippet_is_valid_json` — snippet embeds `KNOWLEDGE_STORE_TARGET`.

(Module header labels these "PBT-10" but they are example-based; genuine
Hypothesis PBT targets live in U3/U5 — see functional-design/domain-entities.md.)

## Suite status
Whole suite = **36 tests, all green** (store/ingestion/codegraph/retrieval/
services/mcp/install). U8 code generation complete; no failing/pending items.

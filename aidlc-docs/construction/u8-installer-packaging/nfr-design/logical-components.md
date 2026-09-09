# U8 — Installer & Packaging · Logical Components

**Stage**: CONSTRUCTION → NFR Design (per-unit)
**Unit**: `u8-installer-packaging`

Concrete classes/assets mapped to `components.md` / `services.md`.

| Component (design) | Concrete artifact | Role (one line) |
|---|---|---|
| InstallService | `knowledge_store/install/service.py :: InstallService` | Orchestrate install: init store, detect + configure clients, fallback snippet |
| InstallService | `InstallService.run(target_dir, init_store=True)` | Entry point; returns `InstallReport` |
| InstallService | `_is_claude` / `_is_opencode` | Filesystem detection of MCP clients |
| InstallService | `_configure_claude` / `_configure_opencode` | Merge `knowledge-store` entry into client config |
| InstallService | `_load` / `_save` | Tolerant JSON read-modify-write (merge, never clobber) |
| (module) | `service.py :: manual_snippet` / `_server_entry` | README fallback JSON + shared stdio entry builder |
| C3 Installer CLI | `knowledge_store/install/cli.py :: main` / `build_parser` | argparse dispatch for subcommands |
| C3 Installer CLI | `_cmd_install` / `_cmd_init` / `_cmd_ingest` / `_cmd_manifest` | Subcommand handlers |
| (package) | `knowledge_store/install/__init__.py` | Exports `InstallService`, `manual_snippet` |
| Packaging | `pyproject.toml` (root) | Metadata, empty core deps, optional extras, `console_scripts`, package-data |

**Dependencies (downward-only)**: `InstallService` → `KnowledgeStore` /
`DEFAULT_STORE_DIRNAME` (U1), `knowledge_store.types` (`InstallReport`,
`Status`); CLI → `InstallService`, and lazily `IngestionService`/`KnowledgeSystem`
(U6) for `ingest`, `mcp.tools.build_registry` for `manifest`.

**Consumers**: the P3 Installer runs the `knowledge-store` CLI; the written
config lets an MCP client launch `knowledge-store-mcp` (U6 server).

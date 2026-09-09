# U8 — Installer & Packaging · Tech Stack Decisions

**Stage**: CONSTRUCTION → NFR Requirements (per-unit)
**Unit**: `u8-installer-packaging`

---

## Decisions

| Concern | Choice | Rationale |
|---|---|---|
| CLI parsing | **stdlib `argparse`** | zero deps, standard, subcommand dispatch (NFR-4) |
| Config read/write | **stdlib `json`** | client configs are JSON (`.mcp.json`, `opencode.json`) |
| Path handling | **stdlib `pathlib`** | portable target resolution + detection |
| Build backend | **setuptools + `pyproject.toml`** (`setuptools>=68`, wheel) | standard PEP 517/518 packaging |
| Dependency strategy | **empty core deps + optional extras** | dependency-light install (NFR-3/NFR-4) |
| Entry points | **`console_scripts`**: `knowledge-store`, `knowledge-store-mcp` | shell-level install + MCP command referenced in config |
| Store init | **`KnowledgeStore.init_schema()`** (U1) | isolated `.knowledge-store/` (US-8.2) |

## Justifications

### Copy-style install (NFR-4)
Installation is a single `argparse` CLI backed by `InstallService`, using only
stdlib for IO. `run()` creates the target, initializes the isolated store, and
merges an MCP entry into whatever client it detects — no bespoke installer
framework, no network fetch. When nothing is detected it prints a manual JSON
snippet, so the flow never dead-ends. This satisfies "script-level install with
minimal, documented prerequisites" (US-8.1, US-9.4).

### Dependency-light packaging (NFR-3 / NFR-4)
`[project] dependencies = []` keeps a bare install importable and lets the
deterministic core test suite run without heavy native deps. Capability groups
are opt-in extras:

| Extra | Enables |
|---|---|
| `mcp` | MCP server SDK |
| `embeddings` | fastembed (local embeddings) |
| `vec` | sqlite-vec vector search |
| `code` | tree-sitter + language pack |
| `docs` | pypdf + openpyxl (PDF/xlsx) |
| `test` | pytest + hypothesis |
| `all` | everything above |

### Entry-point consistency
The installer writes `knowledge-store-mcp` as the client MCP command, which is
exactly the `console_scripts` entry point (`mcp.server:main`) — so a detected
client can launch the server immediately after install.

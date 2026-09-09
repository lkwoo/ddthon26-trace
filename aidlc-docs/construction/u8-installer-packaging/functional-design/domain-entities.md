# U8 — Installer & Packaging · Domain Entities

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u8-installer-packaging`

---

## Entities

### InstallReport (`knowledge_store/types/results.py`)
Typed return of `InstallService.run()`.

| Field | Type | Meaning |
|---|---|---|
| `status` | `Status` | `OK` on success |
| `target_dir` | `str` | resolved install target |
| `store_dir` | `str` | `<target>/.knowledge-store/` (empty if `init_store=False`) |
| `configured_clients` | `list[str]` | e.g. `["claude-code", "opencode"]` |
| `manual_snippet` | `str` | README fallback JSON when no client detected |
| `message` | `str` | human-readable next-step guidance |

### MCP config entries (JSON, written into client files)
- Claude `.mcp.json`: `{"mcpServers": {"knowledge-store": {"command":
  "knowledge-store-mcp", "args": [], "env": {"KNOWLEDGE_STORE_TARGET": <target>}}}}`
- opencode `opencode.json`: `{"mcp": {"knowledge-store": {"type": "local",
  "command": ["knowledge-store-mcp"], "environment": {"KNOWLEDGE_STORE_TARGET":
  <target>}}}}`
- `manual_snippet(target)`: same shape as the Claude `mcpServers` entry.

### Packaging metadata (`pyproject.toml`)
- Project: `name`, `version 0.1.0`, `requires-python >=3.10`, `license MIT`,
  `dependencies = []`.
- Optional extras: `mcp`, `embeddings`, `vec`, `code`, `docs`, `test`, `all`.
- Console scripts: `knowledge-store`, `knowledge-store-mcp`.
- Package data: `viewer/**/*` (U7 assets).

---

## Testable Properties (PBT-01)

**Honest assessment:** U8 is **packaging + filesystem IO** (dir creation, schema
init, JSON read-modify-write, argparse). The enforced **PBT Partial** rules —
**PBT-02** (round-trip), **PBT-03** (invariant), **PBT-07/08/09** (generators /
shrinking / framework) — apply to **pure functions**, whose targets live in
**U3** (Chunker serialize round-trip, ChunkVersioner signature determinism) and
**U5** (token estimation). **Most PBT rules are N/A for U8.**

Instead, U8 is covered by **example-based tests** (`tests/install/test_install.py`):
- store initialization creates the isolated `.knowledge-store/` dir.
- no client detected ⇒ valid `manual_snippet` JSON with the `knowledge-store` server.
- Claude detected ⇒ `.mcp.json` gets the `knowledge-store-mcp` command.
- **config-merge preservation / idempotence** — pre-existing `mcpServers.other`
  survives while `knowledge-store` is added (closest analogue to a PBT invariant;
  here it is an example-based assertion, not a Hypothesis property).
- `manual_snippet` embeds `KNOWLEDGE_STORE_TARGET`.

> Note the test module header says "PBT-10" but the assertions are example-based;
> genuine Hypothesis PBT targets (PBT-02/03) live in U3/U5.

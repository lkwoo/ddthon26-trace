# U8 — Installer & Packaging · Business Rules

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u8-installer-packaging`
**Traceability**: FR-8 (US-8.1–8.4, US-9.4), NFR-4, NFR-7

---

## Installation rules

- **BR-U8-1 — Data isolation in `.knowledge-store/`.** The store is always
  initialized under `<target>/.knowledge-store/` (`DEFAULT_STORE_DIRNAME`),
  keeping knowledge data separate from project source (FR-8.2, US-8.2).
  `InstallReport.store_dir` records the location.

- **BR-U8-2 — Optional store init.** `run(..., init_store=False)` (CLI
  `--no-store`) skips schema creation for copy-only installs; store_dir stays
  empty.

- **BR-U8-3 — Client detection is filesystem-based.**
  - Claude Code ⇐ presence of `.mcp.json` **or** `.claude` (`_is_claude`).
  - opencode ⇐ presence of `opencode.json`, `.opencode.json`, **or** `.opencode`
    (`_is_opencode`).
  Both may match; each detected client is configured (FR-8.3, US-8.3).

- **BR-U8-4 — Config merge never clobbers unrelated entries.** `_load` reads
  existing JSON (empty dict on missing/invalid), `setdefault` obtains the
  `mcpServers` / `mcp` map, and only the `knowledge-store` key is written.
  Pre-existing servers/keys are preserved (US-8.3). Re-running is **idempotent**
  for the `knowledge-store` entry.

- **BR-U8-5 — Client-specific entry shape.**
  - Claude `.mcp.json`: `mcpServers["knowledge-store"] = {command:
    "knowledge-store-mcp", args: [], env: {KNOWLEDGE_STORE_TARGET: <target>}}`.
  - opencode `opencode.json`: `mcp["knowledge-store"] = {type: "local", command:
    ["knowledge-store-mcp"], environment: {KNOWLEDGE_STORE_TARGET: <target>}}`.

- **BR-U8-6 — Manual-snippet fallback.** When no client is detected,
  `InstallReport.manual_snippet` = `manual_snippet(target)` and the message
  directs the user to the README (FR-8.3/8.4, US-8.3/8.4). The snippet is valid
  JSON carrying the same stdio server entry.

- **BR-U8-7 — Malformed config tolerance.** `_load` returns `{}` on
  `JSONDecodeError`/`OSError`, so a corrupt existing config does not abort the
  install (it is rebuilt with the knowledge-store entry).

- **BR-U8-8 — Typed report, no exceptions on the happy path.** `run` returns an
  `InstallReport` with `status`, `target_dir`, `store_dir`,
  `configured_clients`, `manual_snippet`, `message`; the CLI maps `status` →
  exit code.

## Packaging rules

- **BR-U8-9 — Dependency-light core.** `[project] dependencies = []`; heavy
  integrations (`mcp`, `fastembed`, `sqlite-vec`, `tree-sitter`, `pypdf`/
  `openpyxl`) are **optional extras** so the package imports and core
  deterministic tests run without them (NFR-3, NFR-4).

- **BR-U8-10 — Console-script entry points.** `knowledge-store` →
  `install.cli:main`; `knowledge-store-mcp` → `mcp.server:main`. The installer
  writes `knowledge-store-mcp` as the MCP command (matches BR-U8-5).

- **BR-U8-11 — Preserve ported-code notices.** Graphify (Apache-2.0) and
  obsidian-wiki (MIT) notices are retained via root `NOTICE` + `LICENSE`; the
  installer/packaging must not drop them (FR/NFR-7).

---

## Requirement traceability

| Rule | FR / NFR | Story |
|---|---|---|
| BR-U8-1, BR-U8-2 | FR-8.2 | US-8.2 |
| BR-U8-3, BR-U8-4, BR-U8-5, BR-U8-6, BR-U8-7 | FR-8.3, NFR-5.1 | US-8.3 |
| BR-U8-6, BR-U8-8 | FR-8.4, NFR-4.2 | US-8.4, US-9.4 |
| BR-U8-9, BR-U8-10 | FR-8.1, NFR-4.1 | US-8.1, US-9.4 |
| BR-U8-11 | NFR-7 | (licensing) |

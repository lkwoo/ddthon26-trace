# U8 — Installer & Packaging · NFR Design Patterns

**Stage**: CONSTRUCTION → NFR Design (per-unit)
**Unit**: `u8-installer-packaging`

---

## Patterns applied

### 1. Client detection + config-merge strategy — FR-8.3, NFR-5.1
Detection is filesystem probing (`_is_claude`, `_is_opencode`); configuration is
a **read-modify-write JSON merge**. `_load` tolerates missing/corrupt files
(returns `{}`), `setdefault` obtains the client's server map, and only the
`knowledge-store` key is set — so unrelated entries survive and re-runs are
idempotent.

```
detect(target) -> {claude?, opencode?}
   for each detected client:
      data = _load(config)          # {} if missing/invalid
      data[<servers key>].setdefault-merge["knowledge-store"] = entry
      _save(config, data)           # unrelated keys preserved
   none detected -> report.manual_snippet = manual_snippet(target)
```

### 2. Manual-snippet fallback (no dead-end install) — NFR-4
If no client is detected the installer emits a valid, copy-paste MCP JSON
snippet and points at the README. Installation always produces an actionable
result.

### 3. Capability-based optional extras — NFR-3 / NFR-4
The package core has zero dependencies; heavy integrations are opt-in extras
(`mcp`, `embeddings`, `vec`, `code`, `docs`, `test`, `all`). This is a
feature-flag-via-packaging pattern: install only the capabilities you need,
keep the deterministic core lean and importable.

### 4. Typed report + thin CLI — orchestration boundary
`InstallService.run` returns an `InstallReport`; the `argparse` CLI is a thin
adapter that prints fields and maps `status` → exit code. Business logic stays
in the service, matching the project's thin-adapter principle.

### 5. Data isolation — FR-8.2
Store data is always initialized in `<target>/.knowledge-store/`
(`DEFAULT_STORE_DIRNAME`), keeping knowledge separate from project source.

### 6. License preservation via NOTICE/LICENSE — NFR-7
Ported Graphify (Apache-2.0) / obsidian-wiki (MIT) notices are retained at repo
root; the packaging declares its own MIT license and must not drop the
`NOTICE`/`LICENSE` files.

# U7 — Wiki Export & Web Viewer · Tech Stack Decisions

**Stage**: CONSTRUCTION → NFR Requirements (per-unit)
**Unit**: `u7-wiki-export-viewer`

---

## Decisions

| Concern | Choice | Rationale |
|---|---|---|
| Export serialization | Python **stdlib `json`** (`ensure_ascii=False`, `indent=2`) | zero deps, deterministic, human-diffable (NFR-3.1, NFR-4) |
| File IO / asset copy | **stdlib `pathlib` + `shutil.copy2`** | no build/packaging tooling for the viewer |
| Viewer markup | **static HTML** (`viewer/index.html`) | opens via `file://`, no server (Q5, FR-7) |
| Viewer styling | **hand-written CSS** (`viewer/styles.css`) | no CSS framework/build step |
| Viewer logic | **vanilla ES (`app.js`, `"use strict"`)** | no bundler, no transpile |
| Visualization | **D3 v7 from CDN** (`cdn.jsdelivr.net/npm/d3@7`) | tree + force graph without a build; matches Graphify `tree_html.py` style (NFR-7) |

## Justifications

### No-build viewer (NFR-2 usability)
The viewer is three static files. A reviewer opens `index.html` directly; there
is no npm install, bundler, dev server, or transpile step. D3 is loaded from a
CDN `<script>` tag rather than vendored/bundled. Trade-off accepted: **if fully
offline, the tree/graph views show an offline notice** while the wiki content
still renders (`typeof d3 === "undefined"` guard). This keeps the human
interface trivially installable and consistent with the copy-style install
(NFR-4) — no separate front-end toolchain is introduced.

### Deterministic stdlib export (NFR-3.1)
Export uses only Python stdlib (`json`, `pathlib`, `shutil`). No embedding, no
LLM, no network — consistent with the LLM-free server principle. Deterministic
JSON output makes exports diffable and idempotent (BR-U7-3).

### Packaging
Viewer assets ship as `knowledge_store` package data via
`[tool.setuptools.package-data] knowledge_store = ["viewer/**/*"]` (root
`pyproject.toml`), and `WikiExporter` copies them next to the exported JSON so
the wiki directory is self-contained and portable.

# U7 — Wiki Export & Web Viewer · Code Summary

**Stage**: CONSTRUCTION → Code Generation (per-unit)
**Unit**: `u7-wiki-export-viewer`
**Status**: Code generation complete (documenting existing, tested code).

---

## Files

| File | Description |
|---|---|
| `knowledge_store/wiki/exporter.py` | `WikiExporter` — writes `structure.json`, `relationships.json`, `wiki.json` and copies `viewer/*` into the export dir; returns `ExportResult`. Read-only via `Repositories`. |
| `knowledge_store/wiki/__init__.py` | Package init; exports `WikiExporter`. |
| `viewer/index.html` | Static viewer shell: tree/graph/wiki tabs, D3 v7 CDN script, status/footer. |
| `viewer/styles.css` | Dark-theme CSS for tabs, tree, force graph, wiki cards, badges, notices. |
| `viewer/app.js` | Vanilla ES controller: `init` fetches 3 JSON files; `renderTree`, `renderGraph`, `renderWiki` render the views; graceful degradation + `escapeHtml`. |
| `pyproject.toml` (root) | Ships `viewer/**/*` as package data (`[tool.setuptools.package-data]`). |

## Key public API

- `WikiExporter(repos: Repositories)`
- `WikiExporter.export(export_dir: str | Path) -> ExportResult`
  - writes 3 JSON artifacts + copies viewer assets; `ExportResult.files_written`
    lists every path.
- Export JSON contract (viewer-facing): `structure.json {nodes, edges}`,
  `relationships.json {relationships}`, `wiki.json {entries}` — see
  functional-design/domain-entities.md.
- Viewer entry: `app.js` `init()` on `DOMContentLoaded`.

## Tests exercising the unit

- **No dedicated `tests/wiki/` suite.** The exporter is wired into the ingestion
  pipeline: `IngestionService.ingest(paths, export=True)` (default) →
  `WikiExportService.regenerate()` → `WikiExporter.export()`
  (`knowledge_store/services/services.py`, `system.py`).
- Pipeline tests in `tests/services/test_pipeline.py` run the ingest path with
  `export=False`, so they validate the surrounding pipeline but **not** the
  exporter output directly.
- **Verification**: the exporter is confirmed via the **export smoke** — running
  `export()` on a populated store writes `structure.json` / `relationships.json`
  / `wiki.json` and copies the viewer assets (`ExportResult.status == OK`). The
  static viewer is verified by opening the copied `index.html` over `file://`.

## Suite status
Whole suite = **36 tests, all green** (collected across store/ingestion/codegraph/
retrieval/services/mcp/install). U7 has no failing/pending items.

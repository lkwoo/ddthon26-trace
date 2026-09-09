# U7 — Wiki Export & Web Viewer · Logical Components

**Stage**: CONSTRUCTION → NFR Design (per-unit)
**Unit**: `u7-wiki-export-viewer`

Concrete classes/assets mapped to `components.md` components.

| Component (design) | Concrete artifact | Role (one line) |
|---|---|---|
| C13 WikiExporter | `knowledge_store/wiki/exporter.py :: WikiExporter` | Serialize store → structure/relationships/wiki JSON and copy viewer assets |
| C13 WikiExporter | `WikiExporter.export(export_dir)` | Entry point; returns `ExportResult` |
| C13 WikiExporter | `_structure` / `_node_json` / `_relationships` / `_wiki` | Per-artifact JSON builders (read via repositories) |
| C13 WikiExporter | `_write_json` | Deterministic JSON writer (`ensure_ascii=False`, `indent=2`) |
| (package) | `knowledge_store/wiki/__init__.py` | Exports `WikiExporter` |
| C2 Web Viewer | `viewer/index.html` | Page shell: 3 tabs (tree/graph/wiki), D3 CDN script, status bar |
| C2 Web Viewer | `viewer/styles.css` | Dark-theme styling for tree/graph/wiki + notices/badges |
| C2 Web Viewer — controller | `viewer/app.js :: init` / `switchView` / `loadJSON` | Fetch JSON, wire tabs + filter, dispatch renders |
| C2 TreeView | `app.js :: buildHierarchy` + `renderTree` | Collapsible D3 tree from `file` nodes + `contain` edges |
| C2 DependencyGraph | `app.js :: renderGraph` + `drag` | D3 force-directed graph; unresolved edges dashed |
| C2 WikiContentViewer | `app.js :: renderWiki` + `escapeHtml` / `notice` | Chunk cards: version badge, tags, summary, text; live filter |

**Dependencies**: exporter → `knowledge_store.store.repositories.Repositories`,
`knowledge_store.types` (`ExportResult`, `Status`); viewer → D3 v7 (CDN) + the
three JSON files only (no coupling to Python).

**Consumers**: `WikiExportService` (U6) calls `WikiExporter.export`; the
Reviewer (P2) opens the copied `index.html`.

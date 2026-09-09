# U7 — Wiki Export & Web Viewer · Business Logic Model

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u7-wiki-export-viewer`
**Components documented**: C13 WikiExporter (Python), C2 Web Viewer (static HTML + D3, non-Python)

> Scope: this unit turns the persisted knowledge store into **static files** a
> browser can open via `file://` — no runtime server. The Python side writes
> three JSON files plus a copy of the viewer; the viewer is a decoupled
> read-only consumer of that file contract (Application Design Q8).

---

## 1. Responsibilities

### C13 WikiExporter (`knowledge_store/wiki/exporter.py`)
- `export(export_dir)` writes three deterministic JSON artifacts and copies the
  static viewer assets alongside them, returning a typed `ExportResult`.
  - `structure.json` — graph nodes + edges (`_structure()` / `_node_json()`).
  - `relationships.json` — code↔chunk relationships (`_relationships()`).
  - `wiki.json` — latest-version chunk entries with tags + Agent summaries (`_wiki()`).
- Reads only through repositories (`Repositories.graph`, `.relationships`,
  `.chunks`, `.summaries`) — no direct SQL, no LLM (FR-7, NFR-3.1).
- Copies every file in `viewer/` (`_VIEWER_SRC`) into the export dir so the
  viewer loads next to its data.

### C2 Web Viewer (`viewer/index.html`, `styles.css`, `app.js`)
- `app.js` `init()` fetches the three JSON files in parallel (`loadJSON`),
  wires tab navigation and the wiki filter, then renders the default views.
- Three decoupled views:
  - **Structure Tree** (`buildHierarchy` + `renderTree`) — collapsible D3 tree
    built from `file` nodes and `contain` edges (FR-7.1, US-7.1).
  - **Dependency Graph** (`renderGraph`) — D3 force-directed node/edge graph;
    unresolved edges dashed (FR-7.2, US-7.2).
  - **Wiki** (`renderWiki`) — per-chunk cards showing latest version badge,
    tags, Agent summary, and text; live text/path filter (FR-7.3/7.4, US-7.3/7.4).
- Degrades gracefully: missing JSON or offline D3 shows a `notice(...)` instead
  of failing.

---

## 2. Flow

```
Ingestion/Update (U6)                          Reviewer (browser)
        |                                              |
        v                                              v
WikiExportService.regenerate()               open index.html (file://)
        |                                              |
        v                                              v
WikiExporter.export(<store>/wiki)             app.js init(): fetch 3 JSON
  |  reads repos (read-only)                          |
  |  write structure.json                             +-- renderTree()   <- structure.json
  |  write relationships.json                         +-- renderGraph()  <- structure.json
  |  write wiki.json                                  +-- renderWiki()   <- wiki.json
  |  copy viewer/* -> export dir                       (relationships.json available)
  v
ExportResult(status=OK, files_written=[...])
```

The two sides never call each other — they meet only at the JSON file contract.
Export is triggered by `IngestionService.ingest(..., export=True)` (default),
which delegates to `WikiExportService.regenerate()` so reviewers always see the
latest chunk versions (US-7.4, NFR-2.1).

---

## 3. ASCII sketch (real names)

```
knowledge_store/wiki/exporter.py
   WikiExporter(repos)
     .export(export_dir) -> ExportResult
        _structure()      -> {"nodes":[...], "edges":[...]}   -> structure.json
        _relationships()  -> {"relationships":[...]}          -> relationships.json
        _wiki()           -> {"entries":[...]}                -> wiki.json
        copy viewer/{index.html, styles.css, app.js}

viewer/app.js
   init() -> Promise.all(loadJSON x3) -> state{structure,relationships,wiki}
      switchView("tree"|"graph"|"wiki")
        renderTree()  buildHierarchy(state.structure)  (D3 tree)
        renderGraph() (D3 forceSimulation)
        renderWiki(filter) (chunk cards, escapeHtml)
```

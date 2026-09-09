# U7 — Wiki Export & Web Viewer · NFR Design Patterns

**Stage**: CONSTRUCTION → NFR Design (per-unit)
**Unit**: `u7-wiki-export-viewer`

---

## Patterns applied

### 1. Static-export contract (decoupling) — NFR-2, Q8
The Python exporter and the browser viewer are decoupled by a **file contract**
(three JSON documents), not by an API or process boundary. Either side can be
reimplemented independently as long as the JSON shapes hold. This removes the
runtime-server dependency and lets reviewers use `file://`.

```
Producer (Python)                Contract                 Consumer (browser)
WikiExporter.export  --writes-->  structure.json    --fetch-->  renderTree/renderGraph
                                  relationships.json --fetch-->  (relationships state)
                                  wiki.json          --fetch-->  renderWiki
```

### 2. Latest-version projection — NFR-2.1
`_wiki()` projects only `chunks.all_latest()` and stamps `latest_version`, so
the human view is always the current state. Export is re-run after each
ingestion (`WikiExportService.regenerate`) to keep the projection fresh.

### 3. Graceful degradation — usability
The viewer treats missing data and missing D3 as first-class states via
`loadJSON` returning `null` and the `typeof d3 === "undefined"` guard, rendering
a `notice(...)` rather than throwing. An empty or offline store still opens.

### 4. Self-contained portable bundle — NFR-4
`export()` copies `viewer/*` next to the JSON, producing a directory that can be
zipped/moved and opened anywhere. Assets are shipped as package data.

### 5. License preservation — NFR-7
Ported presentation logic (Graphify Apache-2.0 tree style, obsidian-wiki MIT
wiki rendering) is acknowledged via the repo-root `NOTICE` and `LICENSE`, which
this unit must not remove.

### 6. Output escaping (defensive) — robustness
All store-derived strings rendered into the DOM pass through `escapeHtml`;
wiki body text renders inside `<pre>` in the MVP viewer.

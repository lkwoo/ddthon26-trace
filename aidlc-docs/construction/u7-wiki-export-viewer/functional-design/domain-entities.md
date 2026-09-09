# U7 — Wiki Export & Web Viewer · Domain Entities

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u7-wiki-export-viewer`

---

## Entities

### ExportResult (`knowledge_store/types/results.py`)
Typed return of `WikiExporter.export()`.

| Field | Type | Meaning |
|---|---|---|
| `status` | `Status` | `OK` on success |
| `export_dir` | `str` | absolute export directory (`<store>/wiki`) |
| `files_written` | `list[str]` | every JSON + copied asset path written |
| `message` | `str` | optional note |

### Export JSON schema (the viewer contract)
Written by the exporter, consumed by `app.js`.

- **structure.json** — `{ "nodes": [...], "edges": [...] }`
  - node: `{id, name, kind, path, language}` (from `_node_json`)
  - edge: `{src, dst, type, resolved}` (`type` = graph edge value, e.g. `contain`, `call`)
- **relationships.json** — `{ "relationships": [ {src, dst, type, score, resolved} ] }`
- **wiki.json** — `{ "entries": [ {id, source_path, kind, ordinal, tags[],
  latest_version, text, summary} ] }`

### Viewer state (client-side, `app.js`)
In-memory only: `state = { structure, relationships, wiki }` populated by
`loadJSON`. Not persisted; rebuilt on every page load.

---

## Testable Properties (PBT-01)

**Honest assessment:** U7 is almost entirely **IO + static-asset** work (JSON
serialization to disk, file copy, DOM rendering). The enforced PBT rules under
this project's **PBT Partial** mode — **PBT-02** (serialize round-trip),
**PBT-03** (invariants), **PBT-07/08/09** (generator quality / shrinking /
framework) — target **pure functions**. Their concrete homes are the
**Chunker** and **ChunkVersioner** in **U3** and the snippet/token estimators in
**U5**, not this unit. For U7 most PBT rules are **N/A**.

- **PBT-02 (round-trip)** — N/A here directly. The chunk serialization
  round-trip property lives in U3 (`tests/ingestion/test_chunker_pbt.py`). U7
  merely re-serializes already-persisted rows to JSON.
- **PBT-03 (invariant)** — a candidate invariant for U7 would be "export is
  idempotent for a fixed store state" (BR-U7-3), but this is best covered by an
  **example-based** smoke test (no meaningful input space to generate over).
- **PBT-07/08/09** — N/A (no Hypothesis generators/strategies in this unit).

**Example-based coverage that applies here** (candidate, IO-shaped):
- export of an empty store writes three valid JSON files + copies assets
  (`ExportResult.status == OK`, `files_written` non-empty).
- viewer degradation: `renderTree`/`renderGraph`/`renderWiki` emit a `notice`
  when data is null/empty (verifiable via DOM assertions).

> The exporter path is exercised indirectly by the ingestion pipeline
> (`IngestionService.ingest(..., export=True)` default → `WikiExportService.regenerate`
> → `WikiExporter.export`); see `code/code-summary.md`.

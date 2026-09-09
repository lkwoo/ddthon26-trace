# U7 — Wiki Export & Web Viewer · Business Rules

**Stage**: CONSTRUCTION → Functional Design (per-unit)
**Unit**: `u7-wiki-export-viewer`
**Traceability**: FR-7 (US-7.1–7.4), NFR-2.1

---

## Export contract rules (C13 WikiExporter)

- **BR-U7-1 — Static-export decoupling.** The exporter's only obligation is to
  write a fixed set of files; Python never serves or knows about the viewer's
  rendering logic. The viewer depends only on the JSON file contract, not on
  Python internals (Q8, FR-7). *(structure.json / relationships.json / wiki.json)*

- **BR-U7-2 — No runtime server.** Artifacts are written to `<store>/wiki/` and
  opened via `file://`; there is no HTTP server, socket, or process dependency
  at view time (FR-7, NFR-2.1).

- **BR-U7-3 — Deterministic JSON.** For a given store state `export()` produces
  the same JSON: fixed key order from the builders, `ensure_ascii=False`,
  `indent=2`. No timestamps, no randomness, no network (NFR-3.1). Re-running
  export overwrites the files idempotently.

- **BR-U7-4 — Latest versions only in the wiki.** `_wiki()` iterates
  `chunks.all_latest()` and records `latest_version` per chunk so reviewers see
  the current content of every chunk (FR-7.4, US-7.4, NFR-2.1). Version history
  is not dumped into the wiki file.

- **BR-U7-5 — Summaries are joined, never generated.** `_wiki()` attaches
  Agent-authored summaries via `summaries.all()` keyed by `chunk_id`; missing
  summaries default to `""`. The exporter never calls an LLM (FR-5 boundary,
  NFR-3.1).

- **BR-U7-6 — Assets travel with data.** Every file under `viewer/` is copied
  next to the JSON so the export dir is self-contained and portable; if
  `viewer/` is absent the JSON is still written (partial-but-valid export).

- **BR-U7-7 — Read-only through repositories.** The exporter issues no SQL and
  performs no writes to the store; all reads flow through `Repositories`
  (`graph`, `relationships`, `chunks`, `summaries`).

## Viewer rules (C2 Web Viewer)

- **BR-U7-8 — Graceful degradation.** Missing/unfetchable JSON (`loadJSON`
  returns `null`) and offline D3 (`typeof d3 === "undefined"`) render a `notice`
  message instead of erroring, so an empty or offline store still opens.

- **BR-U7-9 — Tree from `contain` edges.** `buildHierarchy` roots on `file`
  nodes and nests children via `type === "contain"` edges only (FR-7.1).

- **BR-U7-10 — Unresolved edges are visually distinct.** Graph edges with
  `resolved === false` get the `unresolved` class (dashed) so reviewers can see
  unresolved references without the graph breaking (mirrors US-2.2 semantics).

- **BR-U7-11 — Output escaping.** All store-derived text rendered into the wiki
  DOM passes through `escapeHtml` (defense against malformed content in the
  local file). Wiki text is shown in `<pre>` (Markdown-as-text in the MVP
  viewer; FR-7.3).

---

## Requirement traceability

| Rule | FR / NFR | Story |
|---|---|---|
| BR-U7-1, BR-U7-2, BR-U7-6 | FR-7 | US-7.1–7.4 |
| BR-U7-3, BR-U7-7 | NFR-3.1 | US-7.x |
| BR-U7-4, BR-U7-5 | FR-7.4, NFR-2.1 | US-7.4 |
| BR-U7-9 | FR-7.1 | US-7.1 |
| BR-U7-10 | FR-7.2 | US-7.2 |
| BR-U7-11, BR-U7-8 | FR-7.3 | US-7.3 |

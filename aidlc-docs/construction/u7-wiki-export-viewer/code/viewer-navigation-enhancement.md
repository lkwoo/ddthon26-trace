# U7 — Viewer Navigation Enhancement · Change Note

**Stage**: CONSTRUCTION → Code Generation (per-unit, follow-up change)
**Unit**: `u7-wiki-export-viewer`
**Date**: 2026-09-09
**Scope**: Client-side viewer only (`viewer/`). No change to the Python
exporter, the export JSON contract, or the store.

---

## Motivation

The original viewer rendered the **Wiki** tab as a single flat, scrolling list
of entry cards with only a text filter — there was no table of contents and no
per-page navigation. The **Structure Tree** and **Dependency Graph** showed
nodes but were inert: nodes were not clickable and did not link to any content.

Requested improvements:

1. The wiki's first screen should be a **full table-of-contents page**, and the
   wiki should be **navigable like a real web wiki** (browse into pages, follow
   cross-links, use back/forward).
2. Structure-tree and dependency-graph nodes should be **reactive** — clicking a
   node should show related information or navigate to the relevant wiki page.

## What changed

### 1. Wiki as a navigable website

- **Default view is now Wiki**, and its landing state is a **Table of Contents**
  (`renderWikiHome`) listing every page grouped by top-level directory, with
  section counts and kind.
- **Page model** (`buildPages`): latest chunks are grouped by `source_path` into
  "pages"; each page's chunks are ordered by `ordinal` into "sections", so a
  file/document reads top-to-bottom like an article. Tags and the max version
  are aggregated per page.
- **Two-pane layout**: a left **sidebar TOC** (`renderWikiNav`, grouped +
  searchable) and a right **article pane** (`openWikiPage`).
- **Article pane** shows a breadcrumb (`⌂ Contents / <group>`), page header
  (title, path, version + tag badges), each section (optional summary + text),
  and a **"Related pages"** block linking to structurally connected pages
  (`relatedPages`, computed from code-graph edges).
- **Hash routing** (`routeFromHash`): `#page=<encoded source_path>` deep-links a
  page; empty hash shows the TOC. Browser back/forward and direct links work.
- The existing search input now filters the sidebar TOC (`renderWikiNav`)
  instead of a flat list.

### 2. Interactive tree & graph nodes

- **Structure Tree** (`renderTree`): non-root nodes are clickable
  (`navigateToNode`). `buildHierarchy` now carries each node's `id` and `path`.
  Nodes backed by a wiki page are visually emphasized (`.has-page`). Clicking a
  node with a page switches to the Wiki view and opens it; otherwise a node-info
  panel is shown.
- **Dependency Graph** (`renderGraph`): nodes are clickable. Clicking
  **highlights the node's neighbourhood** (connected nodes/edges emphasized,
  the rest dimmed) and opens a floating **node-info panel** (`showNodeInfo`)
  listing kind, path, and connected nodes as chips. If the node has a wiki page,
  an **"Open wiki page"** button appears; connected-node chips that have their
  own page are clickable to navigate. Clicking empty canvas clears the
  selection. Nodes remain draggable.
- **Join key**: graph/tree node `path` ↔ wiki entry `source_path`. Graph node
  ids are code-graph ids (not chunk ids), so navigation matches on file path.

## Data / contract impact

- **None.** All required fields already existed in the export:
  `wiki.json` entries carry `source_path`, `ordinal`, `kind`, `tags`,
  `latest_version`; `structure.json` nodes carry `id`, `name`, `kind`, `path`.
- The exporter still copies `viewer/*` verbatim into
  `<project>/.knowledge-store/wiki/` on every ingest / `regenerate_wiki`, so the
  updated UI propagates on the next regeneration — no build step.

## Files touched

| File | Change |
|---|---|
| `viewer/index.html` | Wiki tab is default; wiki sidebar (`.wiki-toc`) + content (`.wiki-content`) layout; per-view node-info panel elements (`#tree-info`, `#graph-info`). `data-testid` values preserved. |
| `viewer/app.js` | Added `buildPages`, `pageTitle`/`pageGroup`/`groupedPages`, `relatedPages`, `renderWikiNav`, `renderWikiHome`, `openWikiPage`, hash routing (`routeFromHash`/`pageHash`), `navigateToNode`/`showNodeInfo`/`nodeNeighbors`; extended `buildHierarchy`/`renderTree`/`renderGraph` with click handlers and page emphasis; removed the old flat `renderWiki`. |
| `viewer/styles.css` | Wiki two-pane layout, TOC/home, article page, related-page chips, floating node-info panel, graph highlight/dim + clickable cursors, `.has-page` emphasis. |

## Verification

- `tests/wiki/test_exporter.py` — **2 passed** (export contract + viewer assets
  copied). No exporter behavior changed.
- `viewer/app.js` bracket balance checked; manual review of hash-routing
  idempotency. (No `node` runtime available locally for `node --check`; run
  `node --check viewer/app.js` where available.)

## How to preview

```bash
# after re-ingest or MCP regenerate_wiki (copies viewer/* into the store)
python -m http.server -d <project>/.knowledge-store/wiki
```

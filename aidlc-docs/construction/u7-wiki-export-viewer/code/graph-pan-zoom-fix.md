# U7 — Dependency Graph Pan/Zoom Fix · Change Note

**Stage**: CONSTRUCTION → Code Generation (per-unit, follow-up bug fix)
**Unit**: `u7-wiki-export-viewer`
**Date**: 2026-09-09
**Branch**: `shortFix1`
**Scope**: Client-side viewer only (`src/viewer/app.js`). No change to the Python
exporter, the export JSON contract, or the store.

---

## Problem

In the wiki viewer's **Dependency Graph** tab, users could not pan the canvas
with a mouse drag, so nodes that the force simulation pushed outside the initial
viewport were invisible and unreachable ("볼 수 없는 내용들이 많아").

## Root cause

`renderGraph` (`src/viewer/app.js`) drew the graph into an SVG with a **fixed
`viewBox`** (`[0, 0, width, height]`) and attached `d3.drag` **only to individual
nodes**. There was no `d3.zoom` behavior on the canvas, so there was no way to
pan or zoom the whole graph — only reposition one node at a time.

## What changed

- Wrapped the three drawable groups (edges, nodes, labels) in a single
  container `<g>` (previously each was appended directly to the `svg`).
- Attached `d3.zoom` to the `svg`, applying `event.transform` to the container
  `<g>` on `zoom`. Result:
  - **Drag empty canvas → pan.**
  - **Wheel / double-click → zoom** (`scaleExtent([0.1, 8])`).
  - Cursor switches `grab` ↔ `grabbing` for affordance.
- **Node drag still works**: each node's drag container now sits inside the
  transformed container `<g>`, so `d3.pointer` accounts for the zoom transform
  via `getScreenCTM` and `d.fx`/`d.fy` stay in simulation coordinates.
- Node click (neighbourhood highlight + node-info panel) and background-click
  clear are unchanged — `d3.zoom` uses namespaced handlers
  (`mousedown.zoom`, etc.), which do not conflict with the plain `click`
  listener.

## Data / contract impact

- **None.** Pure client-side rendering change.
- The exporter still copies `src/viewer/*` verbatim into
  `<project>/.knowledge-store/wiki/` on every ingest / `regenerate_wiki`, so the
  fix propagates on the next regeneration — no build step, no separate build
  copy to sync.

## Files touched

| File | Change |
|---|---|
| `src/viewer/app.js` | `renderGraph`: added container `<g>`; moved edge/node/label groups into it; added `d3.zoom` (pan + wheel/dbl-click zoom, 0.1–8×) applied to the container; grab/grabbing cursor. |

## Scope note

The **Structure Tree** view shares the same fixed-`viewBox` structure and could
clip large trees, but only the Dependency Graph was reported and fixed here.
Adding matching pan/zoom to the tree is a possible follow-up.

## Verification

- `src/viewer/app.js` delimiter balance checked (`node` unavailable locally for
  `node --check`; run `node --check src/viewer/app.js` where available).
- Manual reasoning confirmed node-drag coordinate correctness under the zoom
  transform (drag container inside the transformed `<g>`).

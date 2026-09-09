# U7 — Wiki Tag Display & Tag Search · Change Note

**Stage**: CONSTRUCTION → Code Generation (per-unit, follow-up change)
**Unit**: `u7-wiki-export-viewer`
**Date**: 2026-09-09
**Branch**: `shortFix1`
**Scope**: Client-side viewer only (`src/viewer/`). No change to the Python
exporter, the export JSON contract, or the store.

---

## Motivation

Each wiki page already carries tags (aggregated per page in `buildPages` from
each chunk's `tags`), but in the UI tags were only visible as inert badges on an
open article — they were absent from the table of contents, and the search box
matched **page paths only**. There was no way to browse or search by tag.

Requested improvements:

1. Surface **tag information** in the wiki UI (not just on the open page).
2. Let users **search by tag** from the same search box.

## What changed

### 1. Tags shown in the table of contents

- `renderWikiHome` now renders a row of clickable `#tag` chips (`tagChips`)
  after each page's meta line, so tags are visible while browsing the TOC.
- On an article page (`openWikiPage`), the tags moved out of the inline
  `meta` badge string into a dedicated `.page-tags` row built from the same
  clickable `tagChips` helper (previously non-interactive `.badge` spans).

### 2. Search matches paths **and** tags

- `pageMatches(p, q)` returns true when the query is a substring of the page
  path **or** of any of the page's tags.
- `normalizeQuery` trims the query and strips a leading `#`, so a tag search can
  be typed as either `api` or `#api`.
- `filteredPages` centralises this filtering; both `renderWikiNav` (sidebar) and
  `renderWikiHome` (contents) now use it, so a search narrows both panes.
- The search-input handler re-renders the landing TOC in addition to the
  sidebar while the TOC is showing (skipped when an article is open, detected
  via the `#page=` hash).
- `index.html` search placeholder updated to `Search pages or #tags…`.

### 3. Click a tag to filter

- `filterByTag(tag)` writes `#<tag>` into the search box, ensures the Wiki view
  is active, and re-renders the nav + home so only pages carrying that tag
  remain. Wired to every tag chip in the TOC and on article pages.

## Data / contract impact

- **None.** `wiki.json` entries already carry `tags`; page-level tags were
  already aggregated by `buildPages`. No exporter, JSON-contract, or store
  change.
- The exporter still copies `src/viewer/*` verbatim into `<store>/wiki/` on every
  ingest / `regenerate_wiki`, so the updated UI propagates on the next
  regeneration — no build step, no copy to sync.

## Files touched

| File | Change |
|---|---|
| `src/viewer/app.js` | Added `normalizeQuery`, `pageMatches`, `filteredPages`, `filterByTag`, `tagChips`; `renderWikiNav` and `renderWikiHome` filter via `filteredPages` (home now respects the query and shows a no-match notice + filtered page count); `openWikiPage` renders tags as clickable chips in a `.page-tags` row; search-input handler also re-renders the home TOC. |
| `src/viewer/styles.css` | Added `.tag-chips` / `.tag-chip` (clickable pill, hover) and `.page-tags` spacing. |
| `src/viewer/index.html` | Search placeholder → `Search pages or #tags…`. |

## Verification

- No Python touched; `tests/wiki/test_exporter.py` only asserts the viewer
  assets are copied (still true). Test suite **not run locally** — `pytest` is
  not installed in this environment.
- `node --check` unavailable locally (no `node` runtime); changes reviewed
  manually for delimiter balance and `el()`-helper shadowing (the local
  `const el = getElementById(...)` in `filterByTag`/`currentFilter` does not call
  the global `el()` DOM helper). Recommend opening the viewer in a browser to
  confirm.

## How to preview

```bash
# after re-ingest or MCP regenerate_wiki (copies src/viewer/* into the store)
python -m http.server -d <project>/.knowledge-store/wiki
# open the Wiki tab: TOC shows #tag chips; type "#<tag>" or click a chip to filter
```

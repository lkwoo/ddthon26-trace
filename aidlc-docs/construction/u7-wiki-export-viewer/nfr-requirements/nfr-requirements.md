# U7 — Wiki Export & Web Viewer · NFR Requirements

**Stage**: CONSTRUCTION → NFR Requirements (per-unit)
**Unit**: `u7-wiki-export-viewer`

---

## Applicable NFRs

### NFR-2 — Data Consistency / Viewer usability (applies)
- **NFR-2.1** Reviewers must always see the **latest chunk versions**. The wiki
  export is regenerated after each ingestion/update (via `WikiExportService`),
  and `wiki.json` records `latest_version` per chunk. Large refactors are
  reconciled by re-export/re-index. *(FR-7.4, US-7.4)*
- Usability: the viewer must be **openable with zero build/serve step** — a
  reviewer double-clicks `index.html`. Static HTML + client-side D3 satisfies
  this (see tech-stack-decisions.md).

### NFR-4 — Installability (partial, shared with U8)
- Viewer assets ship as package data (`viewer/**/*`) and are copied by the
  exporter, so no separate front-end install/build is required. Dependency-light
  by design: the only external is D3 from a CDN.

### NFR-7 — Licensing preservation (applies)
- The tree/graph rendering follows the Graphify (Apache-2.0) `tree_html.py`
  style and obsidian-wiki (MIT) presentation; the root `NOTICE` and `LICENSE`
  must be preserved. Verified present at repo root.

---

## Not applicable / off

- **Security Baseline** — **OFF** (project config) → N/A. Note: the viewer is a
  local `file://` artifact over trusted local data; `escapeHtml` is applied
  defensively but no security-baseline rules are enforced.
- **Resiliency Baseline** — **OFF** → N/A.
- **Property-Based Testing** — enabled **Partial**, but this unit is IO/static
  assets; PBT targets (PBT-02/03/07/08/09) live in U3/U5. **Largely N/A here**
  (see functional-design/domain-entities.md).
- **NFR-1 (latency), NFR-3 (LLM-free)** — indirectly satisfied (no server, no
  LLM in export), but not primary drivers for this unit.

---

## Compliance summary

| NFR / Extension | Status | Rationale |
|---|---|---|
| NFR-2 (consistency/usability) | Compliant | latest-version wiki, no-build viewer |
| NFR-4 (installability) | Compliant (partial) | assets as package data, copied on export |
| NFR-7 (licensing) | Compliant | NOTICE/LICENSE present at root |
| Security Baseline | N/A | extension OFF |
| Resiliency Baseline | N/A | extension OFF |
| PBT-02/03/07/08/09 | N/A | IO/static unit; targets in U3/U5 |

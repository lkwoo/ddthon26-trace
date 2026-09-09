# U8 — Installer & Packaging · NFR Requirements

**Stage**: CONSTRUCTION → NFR Requirements (per-unit)
**Unit**: `u8-installer-packaging`

---

## Applicable NFRs

### NFR-4 — Installability (primary driver)
- **NFR-4.1** Installation must be **script-level** — one command
  (`knowledge-store install <target>`) initializes the store and auto-configures
  detected MCP clients, with no complex manual setup (US-8.1, US-9.4).
- **NFR-4.2** **Minimal, documented prerequisites.** Core package has
  `dependencies = []`; only Python >=3.10 is required to import and run the
  installer and deterministic core; heavy integrations are opt-in extras.
- Fallback path (no client detected) still yields a **copy-paste manual
  snippet**, so install never dead-ends (US-8.3/8.4).

### NFR-7 — Licensing preservation (applies)
- Ported logic from Graphify (Apache-2.0) and obsidian-wiki (MIT) requires the
  root `NOTICE` and `LICENSE` to be preserved. Verified present at repo root.
  `pyproject.toml` declares the project's own `license = { text = "MIT" }`.

---

## Not applicable / off

- **Security Baseline** — **OFF** → N/A. (Installer writes only to the target
  project's own config files with local paths; no secrets, no network.)
- **Resiliency Baseline** — **OFF** → N/A. (Config merge tolerates malformed
  JSON via `_load` returning `{}`, but no baseline resiliency rules are enforced.)
- **Property-Based Testing** — enabled **Partial**, but U8 is packaging/IO;
  PBT-02/03/07/08/09 targets live in U3/U5. **Largely N/A here**; U8 uses
  example-based tests (see functional-design/domain-entities.md).
- **NFR-1 (latency), NFR-2 (consistency), NFR-3 (LLM-free)** — not primary for
  this unit (install runs outside the MCP server process, no LLM).

---

## Compliance summary

| NFR / Extension | Status | Rationale |
|---|---|---|
| NFR-4 (installability) | Compliant | one-command install, empty core deps, manual fallback |
| NFR-7 (licensing) | Compliant | NOTICE/LICENSE present; pyproject MIT |
| Security Baseline | N/A | extension OFF |
| Resiliency Baseline | N/A | extension OFF |
| PBT-02/03/07/08/09 | N/A | packaging/IO unit; targets in U3/U5 |

# Unit of Work Plan — Dual-Interface Knowledge Store

**Stage**: INCEPTION → Units Generation (Part 1 — Planning)
**Sources**: `application-design.md`, `components.md` (C1–C15), `services.md` (5 services), `component-dependency.md` (build order), `stories.md` (9 Epics / 28 stories), `personas.md` (P1 Agent, P2 Reviewer, P3 Installer)
**Mode**: Auto-adopt — per user directive, every `[Answer]:` below is pre-filled with the **recommended** option (marked ⭐). Ambiguity analysis (Step 7) is recorded at the end.

> Purpose: decompose the system into cohesive, dependency-respecting **units of work** for the per-unit CONSTRUCTION loop. This is a greenfield **single deployable Python package** (local, LLM-free, embedded store); units are logical **modules** within that package, not independently deployed services.

---

## Part 1 — Planning Checklist

- [x] P1.1 Analyze components, services, dependencies, and stories for natural unit boundaries
- [x] P1.2 Author decomposition questions across all mandatory categories (embedded below)
- [x] P1.3 Pre-fill recommended answers (auto-adopt mode)
- [x] P1.4 Run Step 7 ambiguity analysis on answers
- [x] P1.5 Resolve ambiguities via follow-ups (none required — see analysis)
- [x] P1.6 Record approval (auto-adopt) and transition to Part 2

## Part 2 — Generation Checklist (executed after planning approval)

- [x] G2.1 Generate `aidlc-docs/inception/application-design/unit-of-work.md` (unit definitions, responsibilities, components, code organization strategy)
- [x] G2.2 Generate `aidlc-docs/inception/application-design/unit-of-work-dependency.md` (dependency matrix + build order)
- [x] G2.3 Generate `aidlc-docs/inception/application-design/unit-of-work-story-map.md` (all 28 stories → units)
- [x] G2.4 Validate unit boundaries, dependencies, and full story coverage — DAG confirmed (no cycles), all 28 stories assigned

---

## Decomposition Questions (with recommended answers)

### Q1 — Story Grouping strategy
How should stories/components be grouped into units?
- **A ⭐** Group by **pipeline capability + build layer**, following the confirmed downward dependency order (storage → embedding → extraction → code/relationships → retrieval/summary → services/MCP → export/viewer → installer). Cohesive, dependency-respecting, maps cleanly to epics.
- B Group strictly by the 9 Epics (one unit per epic).
- C Group by persona (Agent / Reviewer / Installer).

[Answer]: A ⭐ — group by pipeline capability + build layer.

### Q2 — Unit granularity / count
How many units?
- **A ⭐** **8 units** — one per cohesive capability layer (Storage, Embedding/Search, Ingestion/Chunking, Code Structure/Relationships, Retrieval/Summarization, Service+MCP, Wiki Export/Viewer, Installer). Balances cohesion vs. loop overhead.
- B Fewer (3–4 coarse units) — faster loop, weaker cohesion.
- C More (12+ fine units) — high overhead for a single-package system.

[Answer]: A ⭐ — 8 units.

### Q3 — Dependencies / inter-unit communication
How do units interact?
- **A ⭐** **In-process Python calls** through defined component/service interfaces (typed result objects, Q7 of App Design); dependencies flow downward only. No network boundaries between units.
- B Event/message passing between units.
- C Shared global mutable state.

[Answer]: A ⭐ — in-process interface calls, downward-only.

### Q4 — Shared resources
How is the SQLite + sqlite-vec store shared?
- **A ⭐** Owned exclusively by the **Storage Foundation** unit (KnowledgeStore + Repositories); all other units access persistence only via repository interfaces (no direct SQL). Schema is centralized/versioned there.
- B Each unit manages its own tables/connection.

[Answer]: A ⭐ — Storage Foundation owns store + schema; access via repositories only.

### Q5 — Team Alignment / ownership
Ownership model for units?
- **A ⭐** **Single-owner sequential** — one build stream completes each unit fully (design→code) before the next, per the AI-DLC per-unit loop. Solo/small-team greenfield.
- B Parallel multi-team ownership per unit.

[Answer]: A ⭐ — single-owner sequential per-unit loop.

### Q6 — Technical considerations (deployment/scalability differing across units)
- **A ⭐** All units ship in **one installable Python package**; the Web Viewer is the only non-Python artifact (static HTML+D3, no build step) and is decoupled via the static-export contract. No per-unit scaling/deployment differences (local, embedded).
- B Split into multiple deployables.

[Answer]: A ⭐ — one package; viewer decoupled via static-export contract.

### Q7 — Business domain / bounded contexts
- **A ⭐** Bounded contexts align with capability layers: **Knowledge Persistence**, **Semantic Retrieval**, **Content Ingestion**, **Code Graph & Relationships**, **Summarization**, **Agent Interface (MCP)**, **Human Wiki (export+viewer)**, **Installation**. One unit per context.
- B Single monolithic context.

[Answer]: A ⭐ — capability-aligned bounded contexts (one unit each).

### Q8 — Code organization / directory structure (Greenfield multi-unit)
- **A ⭐** Single package `knowledge_store/` with one **sub-package per unit** (`store/`, `embedding/`, `ingestion/`, `codegraph/`, `retrieval/`, `services/` + `mcp/`, `wiki/`, `install/`), shared `types/` for typed results, `tests/` mirroring packages, static viewer under `viewer/`, entry points via `pyproject.toml`. Idiomatic, tree-sitter/sqlite-vec friendly.
- B Flat module layout.
- C src-layout with per-unit top-level packages.

[Answer]: A ⭐ — single package, sub-package per unit (layout detailed in unit-of-work.md).

### Q9 — Cross-unit ordering for the WikiExportService → WikiExporter dependency
IngestionService (Unit 6) triggers WikiExporter (Unit 7) post-ingestion.
- **A ⭐** Define **WikiExporter behind an interface** in Unit 7; Unit 6's WikiExportService orchestrates it. Build Unit 7's exporter core before/with Unit 6 orchestration wiring; the viewer front-end (also Unit 7) is independent and can follow. Accept the single documented cross-unit call.
- B Merge export + services into one unit.

[Answer]: A ⭐ — interface-mediated; documented single cross-unit orchestration call.

---

## Step 7 — Ambiguity Analysis (MANDATORY)

All answers are the recommended option (⭐), consistent with the confirmed Application Design decisions (thin MCP adapter, orchestrator services, pipeline components, repositories, typed results, static export) and the build-order implication in `component-dependency.md`.

- **Vague/ambiguous responses**: none — each answer selects a single concrete option.
- **Undefined terms**: none — "unit", "module", "bounded context" defined per rule terminology and App Design docs.
- **Contradictions**: none — Q1/Q2/Q7/Q8 mutually reinforce a capability-layered single-package decomposition; Q3/Q4 enforce the downward-only, repository-mediated access already in the dependency matrix; Q9 preserves the one sanctioned cross-unit call (Ingestion→WikiExport).
- **Missing generation details**: none — the 8 units, their components, and directory layout are fully specified for Part 2.
- **Combined options**: none.

**Result**: No follow-up questions required. Proceeding to Part 2 (Generation) under auto-adopt.

## Step 9/10 — Approval (auto-adopt)

Approval recorded via the standing user directive ("모든 작업이 끝날때 까지 질문에 권장사항을 채택해서 자동으로 진행"). Logged in `audit.md`. Proceeding to generation.

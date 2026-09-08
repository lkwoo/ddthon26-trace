# Story Generation Plan — Dual-Interface Knowledge Store

**Role**: Product Owner
**Stage**: INCEPTION → User Stories (Part 1: Planning)
**Requirements source**: `aidlc-docs/inception/requirements/requirements.md`

This plan defines *how* we will convert the confirmed requirements (FR-1…FR-8, NFR-1…NFR-8) into user-centered stories with acceptance criteria and personas. Please answer the embedded questions (fill each `[Answer]:` tag with a letter; use `X) Other` to write your own). All questions must be answered before story generation begins.

---

## A. Proposed Personas (draft — to be confirmed via Question 2)

1. **Agent (Autonomous LLM Consumer)** — Claude Code / opencode. Consumes MCP Resources & Tools over stdio. Needs token-efficient context, discoverable tool descriptions, low latency, and interactive ingestion/summarization tools.
2. **Developer / Knowledge Reviewer (Human)** — Uses the static HTML + D3 Web Viewer to explore structure, dependency graphs, and wiki content; reviews and verifies engine/agent-generated updates.
3. **Installer / Maintainer** — Sets up the system in a target project (copy-style installer + auto MCP config for Claude Code/opencode), manages `.knowledge-store/`, and re-indexes after large refactors.

---

## B. Story Development Methodology (execution checklist)

- [x] B1. Confirm final persona set and record in `personas.md` (archetype, goals, pains, technical context, success signals).
- [x] B2. Select story breakdown approach (per Question 1) and organize the backlog accordingly.
- [x] B3. Derive stories from each functional requirement group (FR-1 Ingestion/Chunking, FR-2 Code Structure, FR-3 Relationships, FR-4 Versioning, FR-5 Summarization, FR-6 MCP Interface, FR-7 Web Viewer, FR-8 Installation).
- [x] B4. Write each story in the confirmed format (per Question 4) at the confirmed granularity (per Question 3).
- [x] B5. Attach acceptance criteria to every story in the confirmed AC format (per Question 5).
- [x] B6. Map each persona to its relevant stories (traceability table).
- [x] B7. Add a requirement-traceability column (story → FR/NFR id) so downstream design can trace coverage.
- [x] B8. Validate every story against INVEST (Independent, Negotiable, Valuable, Estimable, Small, Testable).
- [x] B9. Ensure coverage of user-facing NFR behaviors that are testable as stories (per Question 6) — e.g., discoverability (NFR-5), token efficiency / latency (NFR-1).
- [x] B10. Confirm story language (per Question 7) and produce artifacts consistently.

## C. Mandatory Artifacts (produced in Part 2)

- [x] C1. `aidlc-docs/inception/user-stories/stories.md` — INVEST-compliant stories with acceptance criteria, organized per the chosen approach, with traceability to FR/NFR ids.
- [x] C2. `aidlc-docs/inception/user-stories/personas.md` — user archetypes and characteristics, mapped to their stories.

---

## D. Story Breakdown Options (choose in Question 1)

- **User Journey-Based**: Stories follow end-to-end workflows (e.g., "Agent ingests a new PDF → chunks → links → summarizes → stores"; "Human opens viewer → explores dependency graph → reviews updated wiki"). *Benefit*: natural narrative, great for UX flows. *Trade-off*: cross-cuts components.
- **Feature-Based**: Stories organized around system features/capabilities aligned to FR groups. *Benefit*: clean mapping to requirements & design units. *Trade-off*: less emphasis on end-to-end experience.
- **Persona-Based**: Stories grouped by persona (Agent / Human / Installer). *Benefit*: clarifies each user type's needs. *Trade-off*: shared features may be duplicated across personas.
- **Domain-Based**: Stories grouped by domain (Ingestion, Graph, Relationships, Versioning, Viewer, Deployment). *Benefit*: aligns with likely units of work. *Trade-off*: similar to feature-based.
- **Epic-Based (hybrid)**: Epics (one per FR group) each containing persona-tagged sub-stories with a user-journey narrative. *Benefit*: combines requirement mapping + journey clarity + persona coverage. *Trade-off*: more structure to maintain.

---

## E. Clarifying Questions (answer all)

## Question 1
Which story breakdown approach should we use to organize the backlog?

A) Epic-Based hybrid — one Epic per FR group, containing persona-tagged sub-stories with journey context (Recommended: maps cleanly to requirements *and* preserves agent/human journeys)

B) Feature-Based — stories organized strictly around FR feature groups

C) Persona-Based — stories grouped by Agent / Human / Installer

D) User Journey-Based — stories follow end-to-end workflows

E) Other (please describe after [Answer]: tag below)

[Answer]: Epic-Based hybrid — one Epic per FR group, containing persona-tagged sub-stories with journey context (Recommended: maps cleanly to requirements *and* preserves agent/human journeys)

## Question 2
Is the proposed persona set (Section A) correct?

A) Yes — use all three: Agent, Developer/Reviewer (Human), Installer/Maintainer (Recommended)

B) Only Agent + Human (fold Installer/Maintainer into the Human persona)

C) Agent + Human + Installer, and add a separate "Maintainer/Re-indexer" persona as a fourth

D) Other (please describe after [Answer]: tag below)

[Answer]: Yes — use all three: Agent, Developer/Reviewer (Human), Installer/Maintainer (Recommended)

## Question 3
What story granularity / size should we target?

A) Epics grouping small, individually testable stories (a story ≈ one tool, one viewer capability, or one ingestion step) (Recommended)

B) Coarse-grained stories (one story per FR group, fewer/larger stories)

C) Fine-grained stories only (no epics; many small flat stories)

D) Other (please describe after [Answer]: tag below)

[Answer]: Epics grouping small, individually testable stories (a story ≈ one tool, one viewer capability, or one ingestion step) (Recommended)

## Question 4
What story statement format should each story use?

A) Connextra: "As a &lt;persona&gt;, I want &lt;capability&gt;, so that &lt;benefit&gt;" (Recommended)

B) Job Story: "When &lt;situation&gt;, I want to &lt;motivation&gt;, so I can &lt;outcome&gt;"

C) Other (please describe after [Answer]: tag below)

[Answer]: Connextra: "As a &lt;persona&gt;, I want &lt;capability&gt;, so that &lt;benefit&gt;" (Recommended)

## Question 5
What acceptance-criteria format should each story use?

A) Gherkin Given/When/Then scenarios (Recommended — most testable; aligns well with downstream PBT and integration tests)

B) Bulleted checklist of verifiable conditions

C) Hybrid — Gherkin for behavior-heavy stories (tools, versioning, ingestion) + checklists for simple UI stories

D) Other (please describe after [Answer]: tag below)

[Answer]: Gherkin Given/When/Then scenarios (Recommended — most testable; aligns well with downstream PBT and integration tests)

## Question 6
Should user-facing NFR behaviors be captured as stories (with acceptance criteria), or referenced only?

A) Capture the user-observable ones as stories — Agent Discoverability (NFR-5/FR-6.3), Token Efficiency & Low Latency (NFR-1), Easy Installation (NFR-4) — and reference the rest (Recommended)

B) Capture all NFRs as stories

C) Keep all NFRs out of stories; reference them only in acceptance criteria of functional stories

D) Other (please describe after [Answer]: tag below)

[Answer]: Capture the user-observable ones as stories — Agent Discoverability (NFR-5/FR-6.3), Token Efficiency & Low Latency (NFR-1), Easy Installation (NFR-4) — and reference the rest (Recommended)

## Question 7
What language should the story artifacts (`stories.md`, `personas.md`) be written in?

A) Korean (matches the requirements document) (Recommended)

B) English

C) Bilingual (Korean narrative + English technical terms/ids)

D) Other (please describe after [Answer]: tag below)

[Answer]: Korean (matches the requirements document) (Recommended)

## Question 8
What scope of stories should we generate now?

A) MVP scope only (per requirements §6), excluding the Out-of-Scope items in §5 (Recommended)

B) MVP scope plus placeholder stories for near-future (post-MVP) items

C) Other (please describe after [Answer]: tag below)

[Answer]: MVP scope only (per requirements §6), excluding the Out-of-Scope items in §5 (Recommended)

---

## F. Approval Gate

After all `[Answer]:` tags are filled, I will:
1. Analyze answers for ambiguity/contradiction (create a clarification file if needed).
2. Present this plan for your explicit approval.
3. Only then proceed to Part 2 (generate `stories.md` and `personas.md`).

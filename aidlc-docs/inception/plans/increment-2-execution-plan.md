# Increment 2 Execution Plan — semantic_query RAG Improvement

## Stages to Execute
| Stage | Decision | Notes |
|---|---|---|
| Workspace Detection | DONE | Brownfield resume; existing code + full aidlc-docs |
| Reverse Engineering | SKIP | Per-unit design docs already exist; RAG subsystem freshly mapped |
| Requirements Analysis | DONE | `requirements.md`; extensions Security No / PBT Partial / Resiliency No |
| User Stories | SKIP | Internal tooling improvement; requirements + this plan are sufficient |
| Workflow Planning | DONE (this doc) | |
| Application Design | LIGHT | New `eval/` package + additive component changes; captured per-unit |
| Units Generation | DONE (this doc) | 3 units: U-Eval → U-Chunking → U-Hybrid |
| Per-unit Functional Design | LIGHT | Captured as concise design notes per unit |
| Per-unit NFR Req/Design | LIGHT | Inherits base tech-stack; deltas noted per unit |
| Infrastructure Design | SKIP | Local/offline, no cloud infra |
| Code Generation | EXECUTE | Per unit |
| Build and Test | EXECUTE | After units complete |

## Unit Sequence & Dependencies
```
U-Eval  ──(baseline numbers)──►  U-Chunking  ──►  U-Hybrid
   ▲                                  │               │
   └──────────── re-run to prove improvement ─────────┘
```
- **U-Eval** has no code dependency on the others; it is built and run first to establish the baseline.
- **U-Chunking** depends on `CodeStructureAnalyzer` gaining line spans.
- **U-Hybrid** depends on the store schema gaining a keyword index; benefits from U-Chunking metadata.
- After each of U-Chunking and U-Hybrid, the U-Eval harness is re-run to quantify the gain.

## Auto-Adopt Directive
User directive (2026-09-09): "자동으로 동작할 수 있도록 추천대로" — proceed autonomously, adopting the
recommended option at each gate; continue recording artifacts, state, and audit entries. Approval gates
are satisfied by the standing auto-adopt directive.

## U-Eval — Detailed Code Generation Plan
- [x] `eval/metrics.py` — pure functions `recall_at_k`, `reciprocal_rank`, `mrr`, `evaluate_ranking` (PBT-testable)
- [x] `eval/dataset.py` — `EvalQuestion`, `EvalDataset` (JSON load/save round-trip)
- [x] `eval/datasets/repo_questions.json` — ~15-20 dogfood questions w/ gold files
- [x] `eval/datasets/fixture/…` + `fixture_questions.json` — tiny deterministic corpus
- [x] `eval/retrievers.py` — `SemanticRetriever` (wraps QueryService) + `GrepRetriever` (keyword baseline); both return ranked unique file lists
- [x] `eval/harness.py` — ingest corpus, run retrievers over dataset, aggregate metrics, provider policy (fail-loud unless allow_hash)
- [x] `eval/report.py` — human-readable table + JSON envelope
- [x] `eval/__main__.py` — CLI (`python -m eval --corpus repo|fixture --allow-hash --json out.json`)
- [x] `tests/eval/test_metrics_pbt.py` — PBT for metric properties + dataset round-trip
- [x] `tests/eval/test_harness.py` — deterministic fixture regression (minimum baseline)

(Checkboxes reflect the plan for U-Eval; marked as generated.)

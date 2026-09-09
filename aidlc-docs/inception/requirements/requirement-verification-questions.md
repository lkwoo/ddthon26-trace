# Requirements Verification Questions — Increment 2: semantic_query RAG Improvement

**STATUS: ANSWERED (auto-adopt — user chose "추천대로", recommended options).**

**Context**: START with the evaluation baseline (item 5, minimal version) to quantify current
`semantic_query` performance, then item 1 (code-aware chunking) → item 2 (hybrid BM25+vector).

---

## Question 1 — Evaluation question-set source
A) I draft an initial set (~15–20 questions) mined from the codebase with gold file labels, then you review/refine
B) You provide questions and gold labels
C) Auto-generate from git history / symbols, then curate

[Answer]: A

## Question 2 — Gold-label granularity
A) File-level
B) Symbol/line-level
C) File-level now, upgrade to symbol/line-level after item 1 lands

[Answer]: C

## Question 3 — Metrics and k values
A) recall@k (k=1,5,10) + MRR@10
B) + nDCG@10 and precision@k
C) recall@5 + MRR only

[Answer]: A

## Question 4 — grep A/B baseline
A) Yes — implement a keyword/regex baseline and report semantic vs grep side-by-side
B) Not yet

[Answer]: A

## Question 5 — Embedding provider policy during evaluation
A) Require the real learned model and FAIL LOUDLY if only hash fallback is available
B) Report both providers separately
C) Use whatever get_default_provider returns

[Answer]: A

## Question 6 — Harness form / interface
A) Standalone script under eval/
B) pytest regression test
C) Both — standalone script + thin pytest wrapper asserting a minimum baseline

[Answer]: C

## Question 7 — Evaluation corpus
A) This repository itself (dogfood)
B) Small curated fixture corpus
C) Both — repo dogfood + tiny fixed fixture for deterministic regression

[Answer]: C

## Question 8 — Increment decomposition (units of work)
A) Three separate units w/ approval gates: U-Eval → U-Chunking → U-Hybrid (items 3 & 4 deferred)
B) Two units
C) Only U-Eval now, decide rest later

[Answer]: A

---

## Extension Opt-In Questions

## Question 9 — Property-Based Testing Extension
A) Yes (all blocking)
B) Partial (pure functions + serialization round-trips) — matches base project
C) No

[Answer]: B

## Question 10 — Security Extensions
A) Yes
B) No — matches base project (local, offline, LLM-free tooling)

[Answer]: B

## Question 11 — Resiliency Extensions
A) Yes
B) No — matches base project

[Answer]: B

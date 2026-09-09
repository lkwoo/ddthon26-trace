# Requirements — Increment 2: semantic_query RAG Improvement

## Intent Analysis
- **User request**: Improve `semantic_query` so RAG becomes a *superset* of grep (exact match + concept
  linking), not a weaker substitute. The chain is ingest → retrieve → rerank → assemble → generate;
  today it leaks at the first two stages.
- **Request type**: Enhancement (brownfield, on a completed base project).
- **Scope**: Multiple components (`ingestion/`, `embedding/`, `codegraph/`, `store/`, `services/`,
  `mcp/`) plus a new `eval/` package.
- **Complexity**: Moderate→Complex (retrieval quality, chunking algorithm, hybrid fusion).
- **Chosen delivery order**: (5) Evaluation baseline → (1) code-aware chunking → (2) hybrid BM25+vector.
  Items (3) reranker/confidence and (4) file:line output are deferred to a later increment.

## Confirmed Current-State Findings (Explore agent, verified against source)
- Chunking is **blank-line-block** based for prose and code (`ingestion/chunker.py:41,66`) — not
  symbol/AST; functions get split.
- Embedding is general-purpose `BAAI/bge-small-en-v1.5` (`embedding/provider.py:81`) with a **silent
  hash-embedding fallback** when `fastembed` is absent (`provider.py:38-71,103-108`).
- Retrieval is **pure single-vector NN** (`store/repositories.py:212-231`); **no BM25/FTS/rerank**.
- Chunks carry only `source_path`, `ordinal`, coarse `kind`, `language` — **no line_range/symbol**
  (`types/results.py:53-98`). Code graph has symbols but **no line spans** (`codegraph/analyzer.py`).
- `semantic_query` applies **no score threshold** (`embedding/search.py:37-48`) — always returns `limit`.
- **No retrieval-quality evaluation harness** exists.

## Functional Requirements

### FR-E1 — Evaluation harness (Unit U-Eval, built FIRST)
- **FR-E1.1**: Provide a labeled evaluation dataset of representative questions, each with gold
  *file-level* labels. An initial ~15–20 question set is drafted from this codebase (auth, favorites
  count, chunking, versioning, etc.) for review (Q1=A). Dataset is JSON, loadable/serializable.
- **FR-E1.2**: Gold labels are **file-level now**, with a schema that can later carry symbol/line
  ranges once item 1 lands (Q2=C).
- **FR-E1.3**: Compute and report **recall@k (k=1,5,10)** and **MRR@10** (Q3=A), at file granularity
  (a chunk hit counts for its `source_path`; ranked chunk list is reduced to a ranked unique-file list).
- **FR-E1.4**: Run a **keyword/grep-style baseline** over the same corpus and questions and report
  semantic vs grep side-by-side (Q4=A).
- **FR-E1.5**: **Embedding-provider policy** — the standalone runner REQUIRES the learned model and
  **fails loudly** if only the hash fallback is available (Q5=A); an explicit `--allow-hash` override
  exists for environments without `fastembed`.
- **FR-E1.6**: Ship as **both** a standalone runnable script (`python -m eval …`) emitting a human
  report + machine-readable JSON, AND a thin pytest regression wrapper asserting a minimum baseline
  on a deterministic fixture (Q6=C).
- **FR-E1.7**: Evaluation corpus is **both** this repository (dogfood) and a tiny checked-in fixture
  corpus for deterministic regression (Q7=C).

### FR-C1 — Code-aware chunking (Unit U-Chunking, item 1)
- **FR-C1.1**: Chunk code at **symbol boundaries** (function/method/class) rather than blank-line blocks,
  so a unit like "favorites count" stays in one chunk.
- **FR-C1.2**: Attach metadata to every chunk: `file`, `line_range` (start,end), `symbol`, `kind`
  (code/doc/test), `lang`.
- **FR-C1.3**: Extend `CodeStructureAnalyzer` to record **line spans** for symbols (prerequisite for
  symbol chunking and for upgrading gold labels to line/symbol granularity).
- **FR-C1.4**: Broaden coverage to include tests and (where available) commit/PR text.

### FR-H1 — Hybrid retrieval (Unit U-Hybrid, item 2)
- **FR-H1.1**: Add a **keyword/BM25 (or FTS5)** index alongside vectors.
- **FR-H1.2**: **Fuse** keyword and vector rankings (e.g. weighted or reciprocal-rank fusion) so exact
  identifier matches and concept matches both surface.
- **FR-H1.3**: Prove the improvement via the U-Eval harness (recall@k / MRR up vs the baseline).

## Non-Functional Requirements
- **NFR-E1 (Offline/LLM-free)**: Preserve the base project's offline, LLM-free posture; all new deps
  optional with graceful fallback.
- **NFR-E2 (Determinism)**: Metric functions and fixture-based regression must be deterministic
  (supports PBT-08 reproducibility).
- **NFR-E3 (No SQL outside repositories)**: New search paths route through repositories (App Design Q4).
- **NFR-E4 (Backward compatibility)**: Existing `semantic_query` MCP contract keeps working; changes are
  additive until a later increment revises the output format (item 4).

## Extension Configuration (this increment)
| Extension | Enabled | Decided At |
|---|---|---|
| Security Baseline | No (Q10=B) | Requirements Analysis |
| Property-Based Testing | Partial (Q9=B) | Requirements Analysis |
| Resiliency Baseline | No (Q11=B) | Requirements Analysis |

PBT Partial mode: enforce PBT rules for pure functions and serialization round-trips — here that means
the metric functions (recall@k, MRR) and dataset serialization round-trip.

## Units of Work (Q8=A — three units, each with an approval gate)
1. **U-Eval** — evaluation harness + dataset + grep baseline + metrics + tests. (FIRST)
2. **U-Chunking** — symbol-aware chunking + line/symbol metadata + analyzer spans. (item 1)
3. **U-Hybrid** — BM25/FTS keyword index + fusion with vector search. (item 2)

Items 3 (reranker/confidence threshold) and 4 (file:line + code-block output, citations, relationship
linking) are explicitly **deferred** to a later increment.

## Success Criteria
- U-Eval produces a reproducible baseline number for current `semantic_query` (and grep) on the labeled
  set, and a pytest regression guard.
- U-Chunking + U-Hybrid each demonstrably raise recall@k / MRR over that baseline on the same set.

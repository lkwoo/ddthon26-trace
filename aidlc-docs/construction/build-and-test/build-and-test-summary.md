# Build & Test Summary

## Status: GREEN — code complete, full suite passing (base + Increment 2)

- **Build**: single package `knowledge-store`, Python 3.10+, zero mandatory deps.
  Optional extras (`mcp`, `embeddings`, `vec`, `code`, `docs`, `all`, `test`) all
  degrade gracefully when absent (see build-instructions.md fallback matrix).
- **Tests**: `55 passed` via `pytest` on a core install (base 38 + Increment 2: 12
  eval + 5 keyword/hybrid). Runs on the hash embedding fallback when `fastembed` is
  absent; the standalone `python -m eval` runner fails loud unless `--allow-hash`.

## Increment 2 — semantic_query RAG improvement (U-Eval → U-Chunking → U-Hybrid)
- **New modules**: `eval/` (retrieval-quality harness: recall@k / MRR / grep A/B),
  `knowledge_store/ingestion/symbols.py` (symbol/method line spans),
  `knowledge_store/embedding/keyword.py` (code-aware BM25).
- **New tests**: `tests/eval/test_metrics_pbt.py`, `tests/eval/test_harness.py`,
  `tests/embedding/test_keyword.py`.
- **Result (hash fallback, repo dogfood, controlled A/B on identical chunks)**:
  `semantic_query` recall@10 **0.833 → 1.000**; hybrid beats pure vector on every
  metric (recall@1 0.222→0.333, MRR 0.440→0.575). Fixture corpus stays a perfect 1.0.
- **Reproduce eval**: `.venv/bin/python -m eval --corpus repo --allow-hash`
  (and `--corpus fixture`). On a learned code-embedding model, drop `--allow-hash`.
- **PBT (Partial, enforced)**: PBT-02, PBT-03, PBT-07, PBT-08, PBT-09 all satisfied
  and passing under Hypothesis (200–300 examples per property).

## Verification performed
1. End-to-end pipeline smoke: ingest → chunk → version → code graph → embed →
   relate → summarize → wiki export (all OK; wiki wrote structure/relationships/
   wiki JSON + copied viewer assets).
2. `pytest` suite: 38 passed (see unit-test-instructions.md for the mapping of
   tests → units and → enforced PBT rules). Includes `tests/wiki/test_exporter.py`
   which verifies the U7 static-export contract (JSON data + copied viewer assets).
3. Entry points: `knowledge-store` (installer/ingest/manifest) and
   `knowledge-store-mcp --manifest` produce the self-describing tool manifest.

## Enforced PBT rule coverage (Partial mode)
| Rule | Meaning | Where satisfied | State |
|---|---|---|---|
| PBT-02 | serialize/deserialize round-trip | Chunker; EvalDataset JSON (tests/eval/test_metrics_pbt.py) | PASS |
| PBT-03 | invariant/determinism | MinHash; TokenEstimator; Snippet budget; recall@k/MRR bounds & monotonicity; `tokenize` determinism | PASS |
| PBT-07 | structured generators | tests/generators.py (reused) | PASS |
| PBT-08 | shrinking/reproducibility | Hypothesis shrink + print_blob; seed guidance | PASS |
| PBT-09 | framework = Hypothesis | pinned in `[test]` extra + `[tool.hypothesis]` | PASS |
| Other PBT rules | advisory | non-blocking under Partial mode | N/A |

## Extension compliance summary
| Extension | Enabled | Result |
|---|---|---|
| Security Baseline | No (opted out) | N/A — not enforced |
| Property-Based Testing | Yes (Partial) | Compliant — PBT-02/03/07/08/09 pass |
| Resiliency Baseline | No (opted out) | N/A — not enforced |

## How to reproduce
```bash
python3 -m venv .venv && .venv/bin/python /tmp/get-pip.py   # if pip missing
.venv/bin/python -m pip install ".[test]"
.venv/bin/python -m pytest -q                                # -> 55 passed
.venv/bin/python -m eval --corpus repo --allow-hash          # retrieval-quality A/B
```

## Test types produced
- Unit + example-based tests (PBT-10) for every unit surface.
- Property-based tests (Hypothesis) for the enforced deterministic invariants.
- Integration tests through the orchestrator services and MCP tool registry.
- Performance micro-benchmark harness (advisory, NFR-1).
- Contract/e2e: static-export contract validated by the export smoke; MCP
  manifest validated as self-describing.

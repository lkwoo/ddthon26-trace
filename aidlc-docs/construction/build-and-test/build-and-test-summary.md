# Build & Test Summary

## Status: GREEN — code complete, full suite passing

- **Build**: single package `knowledge-store`, Python 3.10+, zero mandatory deps.
  Optional extras (`mcp`, `embeddings`, `vec`, `code`, `docs`, `all`, `test`) all
  degrade gracefully when absent (see build-instructions.md fallback matrix).
- **Tests**: `38 passed` via `pytest` on a core install (no optional runtime deps).
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
| PBT-02 | serialize/deserialize round-trip | Chunker (tests/ingestion/test_chunker_pbt.py) | PASS |
| PBT-03 | invariant/determinism | MinHash determinism; TokenEstimator monotonicity; Snippet budget bound | PASS |
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
.venv/bin/python -m pytest -q                                # -> 38 passed
```

## Test types produced
- Unit + example-based tests (PBT-10) for every unit surface.
- Property-based tests (Hypothesis) for the enforced deterministic invariants.
- Integration tests through the orchestrator services and MCP tool registry.
- Performance micro-benchmark harness (advisory, NFR-1).
- Contract/e2e: static-export contract validated by the export smoke; MCP
  manifest validated as self-describing.

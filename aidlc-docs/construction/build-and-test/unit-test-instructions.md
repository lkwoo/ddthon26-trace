# Unit Test Instructions — incl. Property-Based Testing (PBT Partial)

The suite lives under `tests/`, mirroring the package layout. It combines
example-based tests (PBT-10) with **Hypothesis** property-based tests for the
enforced PBT-Partial rules (PBT-02, PBT-03, PBT-07, PBT-08, PBT-09).

## Run everything
```bash
.venv/bin/python -m pip install ".[test]"
.venv/bin/python -m pytest
```
Expected: **55 passed** (verified; base 38 + Increment 2: 12 eval + 5 keyword).
No optional runtime deps are required; the tests exercise the deterministic
fallbacks (including the hash embedding provider).

## Test layout
| Path | Unit(s) | Kind |
|---|---|---|
| tests/generators.py | shared | PBT-07 domain generators (chunks, document text, tags) |
| tests/ingestion/test_chunker_pbt.py | U3 | PBT-02 serialize/deserialize round-trip |
| tests/ingestion/test_versioner_pbt.py | U3 | PBT-03 MinHash determinism + matching |
| tests/ingestion/test_extractors.py | U3 | example (typed UNSUPPORTED, tags, csv) |
| tests/codegraph/test_analyzer.py | U4 | example (symbols, call/inherit resolution) |
| tests/retrieval/test_tokens_pbt.py | U5 | PBT-03 monotonicity + determinism |
| tests/retrieval/test_snippet_pbt.py | U5 | PBT-03 token-budget invariant |
| tests/services/test_pipeline.py | U1,U6 | example end-to-end pipeline |
| tests/mcp/test_tools.py | U6 | example (manifest, typed errors) |
| tests/wiki/test_exporter.py | U7 | example (static-export contract: JSON + assets) |
| tests/install/test_install.py | U8 | example (isolation, detect/merge) |
| tests/eval/test_metrics_pbt.py | U-Eval | PBT-02 (EvalDataset round-trip) + PBT-03 (recall@k/MRR bounds, monotonicity) |
| tests/eval/test_harness.py | U-Eval, U-Chunking, U-Hybrid | example (fixture perfect baseline, repo dogfood floors, provider-policy fail-loud gate) |
| tests/embedding/test_keyword.py | U-Hybrid | PBT-03 (`tokenize` determinism) + example (camel/snake split, BM25 ranking) |

## Enforced PBT rules → where satisfied
- **PBT-02 (round-trip)**: `deserialize(serialize(chunks)) == chunks` for
  generated chunk lists and for chunks emitted by the chunker (NFR-8.2).
- **PBT-03 (invariant/determinism)**: MinHash signature determinism &
  self-similarity; TokenEstimator monotonicity; SnippetBuilder
  `estimated_tokens <= budget` for `budget >= 1`.
- **PBT-07 (generators)**: centralized structured generators in
  `tests/generators.py`, reused across property tests.
- **PBT-08 (shrinking/reproducibility)**: Hypothesis shrinks failing cases and
  prints a reproduction blob (`print_blob=true` in `[tool.hypothesis]`); see the
  reproducibility section below.
- **PBT-09 (framework)**: Hypothesis is the PBT framework (pinned via the
  `test` extra).

## Reproducibility & seeds (PBT-08)
`pyproject.toml` sets `[tool.hypothesis] derandomize=false, print_blob=true`.
- On failure, Hypothesis prints a `@reproduce_failure(...)` blob — paste it above
  the test to replay the exact case.
- For a fully deterministic CI run, pin a database/seed:
  ```bash
  HYPOTHESIS_SEED=0 .venv/bin/python -m pytest -p no:randomly
  ```
- Show example counts / statistics:
  ```bash
  .venv/bin/python -m pytest --hypothesis-show-statistics
  ```
  Property tests run 200–300 examples each (verified).

## Coverage note (advisory, PBT non-blocking rules)
U1 (store/repositories) and U2 (embedding/search) have no direct PBT targets
(schema/IO and model-backed vectors); they are covered indirectly through the
end-to-end pipeline test. U7 (wiki export) is IO/static-asset and is covered by
`tests/wiki/test_exporter.py` (example-based, PBT-10) rather than a property.
This matches PBT **Partial** scope.

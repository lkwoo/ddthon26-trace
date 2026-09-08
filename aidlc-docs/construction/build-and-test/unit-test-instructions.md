# Unit Test Execution

## Run Unit Tests

### 1. Execute All Unit Tests
```bash
.venv/bin/python -m pytest -q tests/unit
```

### 2. Execute by Unit
```bash
.venv/bin/python -m pytest -q tests/unit/domain        # U1 domain (PBT-02/03/10)
.venv/bin/python -m pytest -q tests/unit/application   # U1 services
.venv/bin/python -m pytest -q tests/unit/mcp           # U2 MCP providers
.venv/bin/python -m pytest -q tests/unit/web           # U3 web viewer
.venv/bin/python -m pytest -q tests/unit/cli           # U4 CLI & assembly
```

### 3. Property-Based Testing profiles (PBT-08 reproducibility)
```bash
HYPOTHESIS_PROFILE=dev .venv/bin/python -m pytest -q tests/unit/domain   # random, shrinking
HYPOTHESIS_PROFILE=ci  .venv/bin/python -m pytest -q tests/unit/domain   # derandomized, no deadline
```
- On failure, Hypothesis prints a reproducible `@reproduce_failure` blob (`print_blob=true`).

### 4. Review Test Results
- **Expected**: unit tests pass, **0 failures**.
  - U1 domain: 21 tests (round-trip PBT-02, invariants PBT-03, parser/extractor/query examples)
  - U1 application: 7 tests (sync/resync/read-merge/query/snippet/update/note-preservation)
  - U2 mcp: 9 tests (resources/tools/prompts, error mapping)
  - U3 web: 9 tests (routing/markdown/wiki provenance/dispatch)
  - U4 cli: 6 tests (assemble wiring, exit codes, report output)
- **Test Coverage**: PBT covers U1 serialization round-trip + pure-function invariants; example tests (PBT-10) cover parsers, services, adapters, and CLI paths.
- **Test Report Location**: pytest stdout (add `--junitxml=report.xml` for CI artifacts).

### 5. Fix Failing Tests
If tests fail: review pytest output → identify the failing case (Hypothesis blob if PBT) → fix code → rerun until green.

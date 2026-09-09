# U-Eval — Code Summary

New package `eval/` (application code at repo root, per Code Location Rules).

| File | Responsibility |
|---|---|
| `eval/__init__.py` | Public API re-exports (metrics, dataset). |
| `eval/metrics.py` | Pure metrics: `recall_at_k`, `reciprocal_rank`, `mrr`, `evaluate_ranking`, `dedup`, `EvalScore`. |
| `eval/dataset.py` | `EvalQuestion`, `EvalDataset` with JSON load/save round-trip; forward-compatible symbol/line label fields. |
| `eval/retrievers.py` | `SemanticRetriever` (wraps `QueryService.semantic_query`, chunk→file reduction) + `GrepRetriever` (keyword baseline). |
| `eval/corpus.py` | `resolve_corpus` — expand dataset corpus entries (dir/file/glob) to root-relative files. |
| `eval/harness.py` | `run_evaluation`, `MethodResult`, `EvalResult`, `ProviderPolicyError`, provider policy enforcement, ingestion + scoring. |
| `eval/report.py` | `render_table` (human) + `to_json` (machine). |
| `eval/__main__.py` | CLI: `python -m eval [--corpus repo|fixture] [--allow-hash] [--limit N] [--json PATH]`. |
| `eval/datasets/repo_questions.json` | 18 dogfood questions with gold repo files. |
| `eval/datasets/fixture_questions.json` + `eval/datasets/fixture/*.py` | Tiny deterministic corpus (5 answer files + 6 distractors) + 5 questions. |

Tests:
| File | Coverage |
|---|---|
| `tests/eval/test_metrics_pbt.py` | Hypothesis PBT for metric properties + dataset JSON round-trip. |
| `tests/eval/test_harness.py` | Fixture perfect-baseline regression, repo baseline floors, provider-policy fail-loud gate. |

**Verification**: full suite `50 passed` (38 base + 12 new) via `.venv/bin/python -m pytest`.

**Run it**:
```
python -m eval                    # dogfood over this repo (requires learned model)
python -m eval --corpus fixture --allow-hash
python -m eval --json out/eval.json
```

**Deps**: none new required. `fastembed` remains optional; the standalone runner fails loudly on the
hash fallback unless `--allow-hash` is passed.

"""CLI entry point: ``python -m eval [options]``.

Examples:
    python -m eval                         # dogfood: evaluate over this repo
    python -m eval --corpus fixture        # deterministic tiny fixture corpus
    python -m eval --allow-hash            # allow the hash fallback (no fastembed)
    python -m eval --json out/eval.json    # also write a machine-readable report
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from eval.corpus import resolve_corpus
from eval.dataset import EvalDataset
from eval.harness import ProviderPolicyError, run_evaluation
from eval.report import render_table, to_json

_HERE = Path(__file__).resolve().parent
_REPO_ROOT = _HERE.parent
_DATASETS = _HERE / "datasets"


def _load(corpus: str) -> tuple[EvalDataset, Path, list[str]]:
    """Return (dataset, corpus_root, corpus_files) for the named corpus."""
    if corpus == "repo":
        dataset = EvalDataset.load(_DATASETS / "repo_questions.json")
        root = _REPO_ROOT
        entries = dataset.corpus or ["knowledge_store"]
        return dataset, root, resolve_corpus(root, entries)
    if corpus == "fixture":
        dataset = EvalDataset.load(_DATASETS / "fixture_questions.json")
        root = _DATASETS / "fixture"
        entries = dataset.corpus or ["."]
        return dataset, root, resolve_corpus(root, entries)
    raise SystemExit(f"unknown corpus: {corpus!r} (expected 'repo' or 'fixture')")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="eval", description=__doc__)
    parser.add_argument("--corpus", choices=["repo", "fixture"], default="repo")
    parser.add_argument("--allow-hash", action="store_true",
                        help="run even if only the hash embedding fallback is available")
    parser.add_argument("--limit", type=int, default=10,
                        help="rank cutoff for retrieval (default 10)")
    parser.add_argument("--json", metavar="PATH", default=None,
                        help="also write the machine-readable report to PATH")
    args = parser.parse_args(argv)

    dataset, root, files = _load(args.corpus)
    if not files:
        print("No corpus files resolved; nothing to evaluate.", file=sys.stderr)
        return 2

    try:
        result = run_evaluation(dataset, root, files,
                                allow_hash=args.allow_hash, limit=args.limit)
    except ProviderPolicyError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 3

    print(render_table(result))

    if args.json:
        out = Path(args.json)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(to_json(result) + "\n", encoding="utf-8")
        print(f"\nWrote JSON report to {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

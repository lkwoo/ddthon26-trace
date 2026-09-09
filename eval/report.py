"""Rendering for evaluation results — human-readable table + JSON envelope."""

from __future__ import annotations

import json

from eval.harness import EvalResult


def to_json(result: EvalResult, indent: int = 2) -> str:
    return json.dumps(result.to_dict(), ensure_ascii=False, indent=indent)


def render_table(result: EvalResult) -> str:
    """A compact, aligned summary table comparing methods."""
    lines: list[str] = []
    lines.append(f"Dataset : {result.dataset_name}")
    lines.append(f"Provider: {result.provider}"
                 + ("   [WARNING: hash fallback — not the learned model]"
                    if result.provider == "hash" else ""))
    lines.append(f"Corpus  : {result.corpus_size} files   Questions: {result.num_questions}")
    lines.append("")
    header = f"{'method':<10} {'recall@1':>9} {'recall@5':>9} {'recall@10':>10} {'MRR@10':>8}"
    lines.append(header)
    lines.append("-" * len(header))
    for name, m in result.methods.items():
        lines.append(
            f"{name:<10} {m.mean_recall_at_1:>9.3f} {m.mean_recall_at_5:>9.3f} "
            f"{m.mean_recall_at_10:>10.3f} {m.mrr:>8.3f}"
        )

    # Head-to-head note (semantic vs grep) when both are present.
    if "semantic" in result.methods and "grep" in result.methods:
        s = result.methods["semantic"].mrr
        g = result.methods["grep"].mrr
        verdict = "semantic > grep" if s > g else ("grep > semantic" if g > s else "tie")
        lines.append("")
        lines.append(f"A/B (MRR@10): {verdict}  (semantic={s:.3f}, grep={g:.3f})")
    return "\n".join(lines)

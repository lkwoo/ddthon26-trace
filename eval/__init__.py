"""Retrieval-quality evaluation harness for ``semantic_query`` (Increment 2, U-Eval).

Measures recall@k / MRR of the semantic retriever against a labeled question set
with file-level gold labels, and A/Bs it against a keyword/grep baseline. The
goal is to make "we improved the RAG" a *measurable* claim, and to guard against
regressions as code-aware chunking (U-Chunking) and hybrid search (U-Hybrid) land.

Public API:
* :mod:`eval.metrics`     — pure metric functions (recall@k, reciprocal rank, MRR).
* :mod:`eval.dataset`     — labeled question set with JSON round-trip.
* :mod:`eval.retrievers`  — semantic + grep retrievers reduced to ranked file lists.
* :mod:`eval.harness`     — ingest a corpus, run retrievers, aggregate metrics.
* :mod:`eval.report`      — human-readable + JSON reporting.
"""

from eval.dataset import EvalDataset, EvalQuestion
from eval.metrics import EvalScore, evaluate_ranking, mrr, recall_at_k, reciprocal_rank

__all__ = [
    "EvalDataset",
    "EvalQuestion",
    "EvalScore",
    "evaluate_ranking",
    "mrr",
    "recall_at_k",
    "reciprocal_rank",
]

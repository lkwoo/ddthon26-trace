"""Evaluation harness — ingest a corpus, run retrievers, aggregate metrics.

Flow:
1. Build an in-memory :class:`KnowledgeSystem` and enforce the embedding-provider
   policy (Q5=A): require the learned model, fail loudly if only the hash fallback
   is available, unless ``allow_hash=True`` is explicitly passed.
2. Ingest the corpus files through the real ingestion pipeline.
3. Run the semantic retriever and the grep baseline over every question.
4. Reduce chunk hits to files, score each query with file-level metrics, and
   aggregate mean recall@1/5/10 and MRR per method.

The result object is JSON-serializable for regression tracking.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from eval.dataset import EvalDataset
from eval.metrics import EvalScore, evaluate_ranking, mrr
from eval.retrievers import GrepRetriever, Retriever, SemanticRetriever
from knowledge_store.services.services import IngestionService, QueryService
from knowledge_store.services.system import KnowledgeSystem


class ProviderPolicyError(RuntimeError):
    """Raised when the hash fallback is active but the learned model was required."""


@dataclass
class MethodResult:
    method: str
    per_query: dict[str, EvalScore] = field(default_factory=dict)

    def _mean(self, attr: str) -> float:
        if not self.per_query:
            return 0.0
        return sum(getattr(s, attr) for s in self.per_query.values()) / len(self.per_query)

    @property
    def mean_recall_at_1(self) -> float:
        return self._mean("recall_at_1")

    @property
    def mean_recall_at_5(self) -> float:
        return self._mean("recall_at_5")

    @property
    def mean_recall_at_10(self) -> float:
        return self._mean("recall_at_10")

    @property
    def mrr(self) -> float:
        return mrr(s.reciprocal_rank for s in self.per_query.values())

    def to_dict(self) -> dict[str, Any]:
        return {
            "method": self.method,
            "mean_recall@1": round(self.mean_recall_at_1, 4),
            "mean_recall@5": round(self.mean_recall_at_5, 4),
            "mean_recall@10": round(self.mean_recall_at_10, 4),
            "mrr@10": round(self.mrr, 4),
            "per_query": {qid: s.to_dict() for qid, s in self.per_query.items()},
        }


@dataclass
class EvalResult:
    dataset_name: str
    provider: str
    corpus_size: int
    num_questions: int
    methods: dict[str, MethodResult] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "dataset": self.dataset_name,
            "provider": self.provider,
            "corpus_size": self.corpus_size,
            "num_questions": self.num_questions,
            "methods": {name: m.to_dict() for name, m in self.methods.items()},
        }


def _normalizer(root: Path):
    root_abs = root.resolve()

    def normalize(source_path: str) -> str:
        p = Path(source_path)
        p_abs = p if p.is_absolute() else (root_abs / p)
        try:
            rel = os.path.relpath(p_abs.resolve(), root_abs)
        except ValueError:
            rel = str(p_abs)
        return rel.replace(os.sep, "/")

    return normalize


def load_corpus_text(root: Path, files: list[str]) -> dict[str, str]:
    """Read corpus files, keyed by corpus-relative path (for the grep baseline)."""
    corpus: dict[str, str] = {}
    for rel in files:
        abs_path = (root / rel).resolve()
        if abs_path.is_file():
            corpus[rel.replace(os.sep, "/")] = abs_path.read_text(
                encoding="utf-8", errors="replace"
            )
    return corpus


def provider_is_learned(system: KnowledgeSystem) -> bool:
    return bool(getattr(system.provider, "is_learned", False))


def run_evaluation(
    dataset: EvalDataset,
    root: str | Path,
    files: list[str],
    *,
    allow_hash: bool = False,
    limit: int = 10,
    system: Optional[KnowledgeSystem] = None,
) -> EvalResult:
    """Ingest ``files`` (relative to ``root``) and evaluate every question."""
    root_path = Path(root).resolve()
    owns_system = system is None
    if system is None:
        system = KnowledgeSystem(root_path, in_memory=True)

    try:
        learned = provider_is_learned(system)
        if not learned and not allow_hash:
            raise ProviderPolicyError(
                "Embedding provider is the hash fallback, not the learned model. "
                "Evaluation numbers would not reflect real semantic search. "
                "Install the learned model (`pip install fastembed`) or pass "
                "allow_hash=True / --allow-hash to run on the fallback anyway."
            )

        abs_files = [str((root_path / rel).resolve()) for rel in files]
        IngestionService(system).ingest(abs_files, export=False)

        normalize = _normalizer(root_path)
        corpus_text = load_corpus_text(root_path, files)

        retrievers: list[Retriever] = [
            SemanticRetriever(QueryService(system), system.repos.chunks, normalize),
            GrepRetriever(corpus_text),
        ]

        result = EvalResult(
            dataset_name=dataset.name,
            provider="learned" if learned else "hash",
            corpus_size=len(corpus_text),
            num_questions=len(dataset.questions),
        )
        for retr in retrievers:
            mres = MethodResult(method=retr.name)
            for q in dataset.questions:
                ranked = retr.retrieve(q.intent, limit=limit)
                mres.per_query[q.id] = evaluate_ranking(ranked, q.gold_files)
            result.methods[retr.name] = mres
        return result
    finally:
        if owns_system:
            system.close()

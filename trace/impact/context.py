"""지식 컨텍스트 조립 & 관련도 랭킹 (UOW-04, C6, NFR Design P1, BR-CTX).

build_context는 저장 지식을 그라운딩 컨텍스트로 모은다(Q1/Q2/Q3=A).
rank_by_relevance는 순수 함수 — 토큰 겹침 휴리스틱으로 결정적 랭킹(외부 검색 라이브러리 미도입).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from trace.common.errors import StorageError
from trace.common.logging import get_logger
from trace.knowledge.store import KnowledgeStore
from trace.models.domain import Conflict, FeatureKnowledge
from trace.models.result import FeatureSummary, Warning

_log = get_logger("trace.impact.context")

_TOKEN = re.compile(r"[a-z0-9]+")


@dataclass
class KnowledgeContext:
    """영향 분석 입력 컨텍스트 (비영속)."""

    task: str
    features: list[FeatureSummary] = field(default_factory=list)   # 전체 요약(광범위)
    focus: list[FeatureKnowledge] = field(default_factory=list)    # 상세 포함 대상
    conflicts: list[Conflict] = field(default_factory=list)        # focus의 기존 충돌(Q3=A)
    known_sources: set[str] = field(default_factory=set)           # 매핑 화이트리스트(Q1=A)


def _tokens(*texts: str) -> set[str]:
    out: set[str] = set()
    for t in texts:
        out.update(_TOKEN.findall(t.lower()))
    return out


def rank_by_relevance(task: str, summaries: list[FeatureSummary]) -> list[str]:
    """작업 텍스트와 관련도 높은 Feature id를 내림차순 반환 (순수·결정적, BR-CTX-002).

    점수 = 작업 토큰 ∩ (title + related_sources) 토큰 크기. 동률은 id 사전순.
    """
    task_tokens = _tokens(task)

    def score(s: FeatureSummary) -> int:
        return len(task_tokens & _tokens(s.title, *s.related_sources))

    return [s.id for s in sorted(summaries, key=lambda s: (-score(s), s.id))]


def build_context(
    task: str,
    feature_id: str | None,
    store: KnowledgeStore,
    *,
    top_n: int = 3,
) -> tuple[KnowledgeContext, list[Warning]]:
    """저장 지식에서 그라운딩 컨텍스트를 조립한다 (BR-CTX).

    feature_id 지정 시 그 Feature만 focus, 미지정 시 관련도 상위 top_n. 손상 파일은 skip+warning.
    """
    summaries = store.list_feature_summaries()
    warnings: list[Warning] = []

    if feature_id is not None:
        focus_ids = [feature_id]
    else:
        focus_ids = rank_by_relevance(task, summaries)[:top_n]

    focus: list[FeatureKnowledge] = []
    for fid in focus_ids:
        try:
            focus.append(store.load_feature(fid))
        except StorageError:
            _log.warning(f"event=context_load_skip id={fid}")
            warnings.append(Warning(code="knowledge_load_skip",
                                    message="지식 로드 skip", source=fid))

    conflicts: list[Conflict] = []
    known_sources: set[str] = set()
    for fk in focus:
        conflicts.extend(fk.conflicts)
        known_sources.update(fk.feature.related_sources)
        known_sources.update(e.source for e in fk.evidence)

    ctx = KnowledgeContext(
        task=task, features=summaries, focus=focus,
        conflicts=conflicts, known_sources=known_sources,
    )
    return ctx, warnings


__all__ = ["KnowledgeContext", "build_context", "rank_by_relevance"]

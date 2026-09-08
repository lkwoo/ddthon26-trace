"""C5 충돌 검출 — TRACE의 구조적 차별점 (UOW-03).

RAG는 '비슷한 것'을 검색하지만, TRACE는 정규화된 Claim(subject.predicate)에 붙은 서로 다른
value를 **결정적 코드**로 비교해 value_mismatch 충돌을 1급 산출물로 검출한다(FR-CONFLICT-001).
LLM은 Claim/Evidence 추출까지만 담당하고, 충돌 판정·신뢰도 산정은 재현 가능한 순수 함수다
(NFR-AI-004 결정성, FR-CONFIDENCE-001 근거 일치도 기반).

이 모듈은 import 시 `analyze_project` 파이프라인에 보강 훅을 등록한다(UOW-02 register_enrich_hook).
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from trace.common import Result, get_logger
from trace.engine.pipeline import register_enrich_hook
from trace.knowledge import KnowledgeStore, default_store
from trace.llm import LLMService
from trace.models import (
    Claim,
    Confidence,
    Conflict,
    ConflictType,
    ConflictValue,
    EvidenceRelation,
    Feature,
    FeatureKnowledge,
)
from trace.workflow import extract_claims, group_evidence

if TYPE_CHECKING:
    from trace.engine.assets import Asset

_log = get_logger("trace.conflict")


# --------------------------------------------------------------- 값 정규화
def normalize_value(value: str) -> str:
    """비교용 값 정규화 (결정적). 공백·대소문자·후행 구두점 제거."""
    return value.strip().strip(".;,").casefold()


# ------------------------------------------------------------- 신뢰도 산정
def assign_confidence(claim: Claim) -> Confidence:
    """근거 일치도 기반 신뢰도 (FR-CONFIDENCE-001).

    LLM 자기확신이 아니라 Evidence의 관계·수로 산정한다:
    - 반박(contradicting) 근거가 있으면 LOW
    - direct/supporting 근거 2개 이상이면 HIGH
    - 1개면 MEDIUM, 근거 없으면 LOW
    """
    ev = claim.evidence
    if not ev:
        return Confidence.LOW
    if any(e.relation == EvidenceRelation.CONTRADICTING for e in ev):
        return Confidence.LOW
    supporting = sum(1 for e in ev if e.relation in (EvidenceRelation.DIRECT, EvidenceRelation.SUPPORTING))
    if supporting >= 2:
        return Confidence.HIGH
    if supporting == 1:
        return Confidence.MEDIUM
    return Confidence.LOW


# --------------------------------------------------------------- 충돌 검출
def detect_conflicts(claims: list[Claim]) -> list[Conflict]:
    """정규화 Claim 목록에서 value_mismatch 충돌을 검출한다 (FR-CONFLICT-001, P0).

    같은 key(subject.predicate)에 정규화 값이 2종 이상이면 충돌. 순수 함수(결정적).
    """
    groups: dict[str, list[Claim]] = {}
    for c in claims:
        groups.setdefault(c.key, []).append(c)

    conflicts: list[Conflict] = []
    for key in sorted(groups):
        group = groups[key]
        distinct = {normalize_value(c.value) for c in group if c.value}
        if len(distinct) < 2:
            continue  # 합의됨 — 충돌 아님

        # 각 (값, 소스) 근거를 인용 (FR-CONFLICT-OUT-002). 순서 안정화.
        values: list[ConflictValue] = []
        seen: set[tuple[str, str]] = set()
        for c in group:
            sources = c.evidence or [None]
            for e in sources:
                src = e.source if e else "(unknown)"
                loc = e.location if e else ""
                sig = (c.value, src)
                if sig in seen:
                    continue
                seen.add(sig)
                values.append(ConflictValue(value=c.value, source=src, location=loc))
        values.sort(key=lambda v: (v.value, v.source))

        vals_desc = ", ".join(sorted({f"{c.value}" for c in group if c.value}))
        conflicts.append(
            Conflict(
                type=ConflictType.VALUE_MISMATCH,
                claim=key,
                values=values,
                interpretation=(
                    f"'{key}'에 서로 다른 값이 주장됩니다: {vals_desc}. "
                    "어느 소스가 옳은지 단정하지 않으니 착수 전 확인하세요."
                ),
            )
        )
    return conflicts


def _aggregate_confidence(claims: list[Claim], conflicts: list[Conflict]) -> Confidence:
    """Feature 수준 신뢰도. 충돌이 있으면 불확실 → MEDIUM 이하."""
    if conflicts:
        return Confidence.LOW
    if claims and all(c.confidence == Confidence.HIGH for c in claims):
        return Confidence.HIGH
    return Confidence.MEDIUM


# ----------------------------------------------------- analyze_project 보강 훅
def enrich_feature(
    feature: Feature, assets: list[Asset], llm: LLMService, fk: FeatureKnowledge
) -> int:
    """Claim/Evidence 추출 → 신뢰도 → 충돌 검출을 수행해 FeatureKnowledge를 보강한다.

    Returns: 검출된 충돌 수 (파이프라인 집계용).
    """
    claims = group_evidence(extract_claims(feature, assets, llm))
    for c in claims:
        c.confidence = assign_confidence(c)
    conflicts = detect_conflicts(claims)
    fk.claims = claims
    fk.conflicts = conflicts
    fk.confidence = _aggregate_confidence(claims, conflicts)
    _log.info("보강 %s: claim %d, conflict %d", feature.id, len(claims), len(conflicts))
    return len(conflicts)


# --------------------------------------------------------- 조회 코어 함수
def summarize_conflicts(
    feature_id: str | None = None, store: KnowledgeStore | None = None
) -> list[dict]:
    """저장된 지식에서 충돌을 수집한다 (feature_id=None이면 전체)."""
    store = store or default_store()
    out: list[dict] = []
    if feature_id:
        try:
            features = [store.load_feature(feature_id)]
        except Exception:  # noqa: BLE001
            features = []
    else:
        features = []
        for summ in store.list_feature_summaries():
            try:
                features.append(store.load_feature(summ["id"]))
            except Exception:  # noqa: BLE001
                continue
    for fk in features:
        for c in fk.conflicts:
            d = c.to_dict()
            d["feature_id"] = fk.feature.id
            out.append(d)
    return out


def get_conflicts(
    feature_id: str | None = None, store: KnowledgeStore | None = None
) -> Result:
    """충돌 목록/상세 (코어 함수, FR-CONFLICT-OUT-001)."""
    conflicts = summarize_conflicts(feature_id, store)
    scope = f"Feature '{feature_id}'" if feature_id else "전체 프로젝트"
    if not conflicts:
        return Result.ok(
            f"{scope}에서 검출된 충돌이 없습니다.",
            conflicts=[],
            meta={"conflicts_count": 0},
        )
    return Result.ok(
        f"{scope}에서 충돌 {len(conflicts)}건 검출 (착수 전 확인 권장).",
        conflicts=conflicts,
        meta={"conflicts_count": len(conflicts)},
    )


# 파이프라인에 보강 훅 등록 (import 시 활성화)
register_enrich_hook(enrich_feature)


__all__ = [
    "normalize_value",
    "assign_confidence",
    "detect_conflicts",
    "enrich_feature",
    "summarize_conflicts",
    "get_conflicts",
]

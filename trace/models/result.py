"""공통 Result envelope + 출력 DTO (UOW-0F).

모든 코어 함수(scan/analyze/list/get/impact)는 Result를 반환한다.
build_result는 business-logic-model.md §1 조립 규칙을 구현한다:
충돌 상위 노출(핵심 우선, NFR-MCP-UX-002) + warnings 사람이 읽는 합본.
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from trace.models.domain import ImpactCategory


class Warning(BaseModel):
    """부분 실패/저신뢰 경고 (BR-WARN-001, Q5=B 구조화)."""

    code: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)
    source: str | None = None


class ConflictOut(BaseModel):
    """get_conflicts 등 출력용 충돌 표현."""

    type: str
    claim: str
    values: list[dict]  # [{value, source, location}]
    interpretation: str


class EvidenceRef(BaseModel):
    source: str
    location: str
    relation: str


class ImpactItem(BaseModel):
    path: str
    reason: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class ImpactOut(BaseModel):
    must_change: list[ImpactItem] = Field(default_factory=list)
    likely_change: list[ImpactItem] = Field(default_factory=list)
    review: list[ImpactItem] = Field(default_factory=list)
    related_conflicts: list[ConflictOut] = Field(default_factory=list)  # P1
    change_plan: list[str] = Field(default_factory=list)


class FeatureSummary(BaseModel):
    id: str
    title: str
    confidence: str | None = None
    conflicts_count: int = 0
    related_sources: list[str] = Field(default_factory=list)


class Result(BaseModel):
    """사람이 읽는 요약 + 구조화 데이터 봉투."""

    summary: str
    data: dict = Field(default_factory=dict)
    conflicts: list[ConflictOut] = Field(default_factory=list)
    impact: ImpactOut | None = None
    evidence: list[EvidenceRef] = Field(default_factory=list)
    warnings: list[Warning] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)


def build_result(
    summary: str,
    data: dict | None = None,
    *,
    conflicts: list[ConflictOut] | None = None,
    impact: ImpactOut | None = None,
    evidence: list[EvidenceRef] | None = None,
    warnings: list[Warning] | None = None,
    meta: dict | None = None,
) -> Result:
    """Result 조립 (business-logic-model §1).

    - 충돌이 있으면 summary 앞에 한 줄 요약을 얹는다(핵심 우선).
    - warnings가 있으면 summary 말미에 '⚠ N건' + 사람이 읽는 합본을 덧붙이되,
      구조화 warnings 필드는 원형 유지(BR-WARN-002).
    - meta에 기본 카운트를 채운다.
    """
    conflicts = conflicts or []
    warnings = warnings or []
    evidence = evidence or []
    data = data or {}
    meta = dict(meta or {})

    parts: list[str] = []
    if conflicts:
        parts.append(f"⚠ 충돌 {len(conflicts)}건이 감지되었습니다 (아래 우선 확인).")
    parts.append(summary)
    if warnings:
        joined = "; ".join(w.message for w in warnings)
        parts.append(f"⚠ 경고 {len(warnings)}건: {joined}")
    full_summary = "\n".join(parts)

    meta.setdefault("conflicts_count", len(conflicts))
    meta.setdefault("warnings_count", len(warnings))

    return Result(
        summary=full_summary,
        data=data,
        conflicts=conflicts,
        impact=impact,
        evidence=evidence,
        warnings=warnings,
        meta=meta,
    )


__all__ = [
    "Warning",
    "ConflictOut",
    "EvidenceRef",
    "ImpactItem",
    "ImpactOut",
    "FeatureSummary",
    "Result",
    "build_result",
    "ImpactCategory",
]

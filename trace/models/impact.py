"""Task Impact LLM 중간 스키마 (UOW-04, C6, domain-entities §1).

analyze_task step 1회 구조화 호출로 영향 후보(ImpactCandidate)와 순서형 Change Plan을 함께 산출.
이 결과를 to_impact_out가 기존 ImpactOut(UOW-0F)로 매핑한다(허구 path·근거부족 review 강등).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from trace.models.domain import ImpactCategory
from trace.models.result import EvidenceRef


class ImpactCandidate(BaseModel):
    """영향 후보 — 파일/컴포넌트 하나에 대한 분류·이유·근거 (BR-IMP-001/002)."""

    path: str = Field(..., min_length=1)
    category: ImpactCategory = ImpactCategory.REVIEW
    reason: str = Field(..., min_length=1)
    evidence: list[EvidenceRef] = Field(default_factory=list)


class TaskImpactResult(BaseModel):
    """complete_structured 루트 스키마."""

    candidates: list[ImpactCandidate] = Field(default_factory=list)
    change_plan: list[str] = Field(default_factory=list)


__all__ = ["ImpactCandidate", "TaskImpactResult"]

"""LLM 추출 중간 스키마 (UOW-03, C2, domain-entities §2).

Feature당 1회 구조화 호출(Q3=A)로 원자 Claim과 각 Claim의 Evidence를 함께 산출한다.
이 중간 결과를 평탄화해 FeatureKnowledge.claims/evidence 를 채우고, claim 그룹 단위로
Confidence·Conflict 를 결정적으로 계산한다(비-LLM, workflow/claims·conflict/detect).
"""

from __future__ import annotations

from pydantic import BaseModel, Field

from trace.models.domain import Evidence


class ExtractedClaim(BaseModel):
    """원자 Claim(subject+predicate) + 그 근거 Evidence 목록 (BR-CLAIM-001/002)."""

    subject: str = Field(..., min_length=1)      # 예: "owner.telephone"
    predicate: str = Field(..., min_length=1)    # 예: "max_length"
    evidence: list[Evidence] = Field(default_factory=list)


class ClaimExtractionResult(BaseModel):
    """complete_structured 루트 스키마."""

    claims: list[ExtractedClaim] = Field(default_factory=list)


__all__ = ["ExtractedClaim", "ClaimExtractionResult"]

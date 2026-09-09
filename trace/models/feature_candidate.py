"""Feature 후보 & LLM 구조화 출력 봉투 (UOW-02).

identify_features / generate_feature_knowledge 의 구조화 출력 스키마.
FeatureCandidate.id 는 LLM 출력이라 안전하지 않을 수 있어 검증하지 않고,
Feature 승격 시 knowledge.ids.safe_feature_id 로 정규화한다.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class FeatureCandidate(BaseModel):
    id: str = Field(default="", description="후보 id(비어있으면 title에서 생성)")
    title: str = Field(..., min_length=1)
    description: str = Field(default="")
    related_sources: list[str] = Field(default_factory=list)
    rationale: str = Field(default="")


class FeatureCandidateList(BaseModel):
    """identify_features 구조화 출력(단일 루트 모델)."""

    features: list[FeatureCandidate] = Field(default_factory=list)


class KnowledgeBody(BaseModel):
    """generate_feature_knowledge 본문 구조화 출력."""

    markdown: str = Field(default="")


__all__ = ["FeatureCandidate", "FeatureCandidateList", "KnowledgeBody"]

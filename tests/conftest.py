"""테스트 공통 픽스처 (UOW-0F).

FakeLLMClient: 네트워크 없이 LLMService를 검증하기 위한 주입용 스텁 (NFR-0F-TST-1).
"""

from __future__ import annotations

import pytest

from trace.config.settings import LLMSettings
from trace.llm.client import LLMClient
from trace.models.domain import (
    Claim,
    Confidence,
    ConfidenceAssessment,
    ClaimConfidence,
    Conflict,
    ConflictValue,
    Evidence,
    EvidenceRelation,
    EvidenceType,
    Feature,
    FeatureKnowledge,
)


class FakeLLMClient:
    """미리 정해둔 응답을 순서대로 반환하는 LLMClient 구현."""

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self.calls: list[str] = []

    def complete(self, prompt: str, *, settings: LLMSettings) -> str:
        self.calls.append(prompt)
        if not self._responses:
            raise AssertionError("FakeLLMClient: 준비된 응답이 소진되었습니다.")
        return self._responses.pop(0)


# LLMClient Protocol 준수 확인 (정적 안전망)
_: LLMClient = FakeLLMClient([])


@pytest.fixture
def sample_feature_knowledge() -> FeatureKnowledge:
    feature = Feature(
        id="owner-registration",
        title="Owner Registration",
        description="반려동물 주인 등록 기능",
        related_sources=["src/Owner.java", "docs/req.pdf"],
    )
    claims = [
        Claim(subject="owner.telephone", predicate="max_length", value="10",
              feature_id="owner-registration"),
    ]
    evidence = [
        Evidence(source="src/Owner.java", type=EvidenceType.SOURCE,
                 location="L42", extracted_value="10",
                 relation=EvidenceRelation.SUPPORTS),
        Evidence(source="docs/req.pdf", type=EvidenceType.PDF,
                 location="p.3", extracted_value="20",
                 relation=EvidenceRelation.CONTRADICTS),
    ]
    confidence = [
        ClaimConfidence(
            claim_key="owner.telephone.max_length",
            assessment=ConfidenceAssessment(level=Confidence.LOW,
                                            reason="요구사항과 코드가 상충"),
        )
    ]
    conflicts = [
        Conflict(
            claim="owner.telephone.max_length",
            values=[
                ConflictValue(value="20", source="docs/req.pdf", location="p.3"),
                ConflictValue(value="10", source="src/Owner.java", location="L42"),
            ],
            interpretation="요구사항은 20자이나 구현은 10자로 제한되어 있습니다.",
        )
    ]
    return FeatureKnowledge(
        feature=feature, claims=claims, evidence=evidence,
        confidence=confidence, conflicts=conflicts,
        meta={"model": "test", "sources": 2},
    )

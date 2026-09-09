"""UOW-03 Confidence 규칙 단위 테스트 (BR-CONF, 비-LLM)."""

from __future__ import annotations

from trace.models.domain import (
    Confidence,
    Evidence,
    EvidenceRelation,
    EvidenceType,
)
from trace.models.extraction import ExtractedClaim
from trace.workflow.claims import assign_confidence


def _ev(value: str | None, relation: EvidenceRelation) -> Evidence:
    return Evidence(source="s.md", type=EvidenceType.MARKDOWN, location="L1",
                    extracted_value=value, relation=relation)


def _claim(*evs: Evidence) -> ExtractedClaim:
    return ExtractedClaim(subject="owner.telephone", predicate="max_length", evidence=list(evs))


def test_low_when_values_disagree() -> None:
    cc = assign_confidence(_claim(
        _ev("10", EvidenceRelation.SUPPORTS),
        _ev("20", EvidenceRelation.SUPPORTS),
    ))
    assert cc.assessment.level == Confidence.LOW
    assert cc.claim_key == "owner.telephone.max_length"


def test_low_when_contradiction_relation() -> None:
    cc = assign_confidence(_claim(
        _ev("10", EvidenceRelation.SUPPORTS),
        _ev("10", EvidenceRelation.CONTRADICTS),  # 같은 값이나 contradicts 관계
    ))
    assert cc.assessment.level == Confidence.LOW


def test_high_when_multiple_supports_agree() -> None:
    cc = assign_confidence(_claim(
        _ev("10", EvidenceRelation.SUPPORTS),
        _ev("10", EvidenceRelation.SUPPORTS),
    ))
    assert cc.assessment.level == Confidence.HIGH


def test_medium_when_single_support() -> None:
    cc = assign_confidence(_claim(_ev("10", EvidenceRelation.SUPPORTS)))
    assert cc.assessment.level == Confidence.MEDIUM


def test_medium_when_mentions_only() -> None:
    cc = assign_confidence(_claim(
        _ev(None, EvidenceRelation.MENTIONS),
        _ev(None, EvidenceRelation.MENTIONS),
    ))
    assert cc.assessment.level == Confidence.MEDIUM


def test_reason_is_present() -> None:
    cc = assign_confidence(_claim(_ev("10", EvidenceRelation.SUPPORTS)))
    assert cc.assessment.reason  # 사유 문자열 필수 (BR-CONF-002)

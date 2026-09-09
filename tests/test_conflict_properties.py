"""UOW-03 속성 기반 테스트 (PBT-03-A~D).

검출 코어(detect_conflicts/classify_conflict_type/assign_confidence)는 순수 함수 →
FakeLLM 없이 결정적으로 검증한다.
"""

from __future__ import annotations

import random

from hypothesis import given, settings
from hypothesis import strategies as st

from trace.conflict.detect import classify_conflict_type, detect_conflicts
from trace.models.domain import (
    Confidence,
    ConflictType,
    Evidence,
    EvidenceRelation,
    EvidenceType,
    normalize_value,
)
from trace.models.extraction import ExtractedClaim

PBT = settings(derandomize=True, max_examples=80, deadline=None)

_values = st.sampled_from(["10", "20", "10.0", " 10 ", "abc", "ABC", "absent", "none", "rejected", ""])
_value_or_none = st.one_of(st.none(), _values)


@st.composite
def _evidence(draw) -> Evidence:  # type: ignore[no-untyped-def]
    return Evidence(
        source=draw(st.text(min_size=1, max_size=8)),
        type=draw(st.sampled_from(list(EvidenceType))),
        location=draw(st.text(min_size=1, max_size=5)),
        extracted_value=draw(_value_or_none),
        relation=draw(st.sampled_from(list(EvidenceRelation))),
    )


@st.composite
def _claim(draw) -> ExtractedClaim:  # type: ignore[no-untyped-def]
    return ExtractedClaim(
        subject=draw(st.text(min_size=1, max_size=6)),
        predicate=draw(st.text(min_size=1, max_size=6)),
        evidence=draw(st.lists(_evidence(), max_size=6)),
    )


def _distinct_norm(ec: ExtractedClaim) -> set[str]:
    return {
        normalize_value(e.extracted_value)
        for e in ec.evidence
        if e.extracted_value is not None and e.extracted_value.strip()
    }


# PBT-03-A: 검출 건전성
@PBT
@given(ec=_claim())
def test_detection_soundness(ec: ExtractedClaim) -> None:
    conflicts = detect_conflicts([ec], "f")
    distinct = _distinct_norm(ec)
    if len(distinct) <= 1:
        assert conflicts == []                 # 값 ≤ 1 → 충돌 없음
    else:
        assert len(conflicts) == 1             # 값 ≥ 2 → 정확히 1건
        assert conflicts[0].claim.startswith(ec.subject.strip())


# PBT-03-B: 결정성/멱등 (evidence·claim 순서 무관)
@PBT
@given(claims=st.lists(_claim(), min_size=1, max_size=4))
def test_detection_determinism(claims: list[ExtractedClaim]) -> None:
    first = [c.model_dump() for c in detect_conflicts(claims, "f")]

    rng = random.Random(0)
    shuffled: list[ExtractedClaim] = []
    for ec in claims:
        ev = list(ec.evidence)
        rng.shuffle(ev)
        shuffled.append(ec.model_copy(update={"evidence": ev}))
    rng.shuffle(shuffled)

    second = [c.model_dump() for c in detect_conflicts(shuffled, "f")]
    assert first == second


# PBT-03-C: 유형 분류 전결정성 (예외 없이 유효 ConflictType)
@PBT
@given(ec=_claim(), vals=st.lists(st.tuples(_values, st.text(min_size=1, max_size=4),
                                            st.text(min_size=1, max_size=4)), min_size=1, max_size=5))
def test_classify_is_total(ec: ExtractedClaim, vals: list) -> None:  # type: ignore[no-untyped-def]
    ctype = classify_conflict_type(ec, vals)
    assert isinstance(ctype, ConflictType)


# PBT-03-D: Confidence 규칙 정합
@PBT
@given(ec=_claim())
def test_confidence_matches_rule(ec: ExtractedClaim) -> None:
    from trace.workflow.claims import assign_confidence

    cc = assign_confidence(ec)
    values = _distinct_norm(ec)
    supports = sum(1 for e in ec.evidence if e.relation == EvidenceRelation.SUPPORTS)
    contradicts = sum(1 for e in ec.evidence if e.relation == EvidenceRelation.CONTRADICTS)
    has_contra = contradicts > 0 or len(values) >= 2

    if has_contra:
        expected = Confidence.LOW
    elif supports >= 2 and len(values) <= 1:
        expected = Confidence.HIGH
    else:
        expected = Confidence.MEDIUM
    assert cc.assessment.level == expected

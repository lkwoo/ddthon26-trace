"""UOW-03 충돌 검출 단위 테스트 — demo 3충돌 유형 정확 (BR-CONFLICT-001/003)."""

from __future__ import annotations

from trace.conflict.detect import classify_conflict_type, detect_conflicts
from trace.models.domain import (
    ConflictType,
    Evidence,
    EvidenceRelation,
    EvidenceType,
)
from trace.models.extraction import ExtractedClaim


def _ev(source: str, etype: EvidenceType, value: str | None,
        relation: EvidenceRelation, location: str = "L1") -> Evidence:
    return Evidence(source=source, type=etype, location=location,
                    extracted_value=value, relation=relation)


# --- demo Ground Truth 3충돌 --------------------------------------------------
def test_c1_value_mismatch() -> None:
    ec = ExtractedClaim(subject="owner.telephone", predicate="max_length", evidence=[
        _ev("docs/spec.pdf", EvidenceType.PDF, "20", EvidenceRelation.SUPPORTS, "p.3"),
        _ev("openapi/petclinic.yaml", EvidenceType.OPENAPI, "10", EvidenceRelation.SUPPORTS),
        _ev("src/Owner.java", EvidenceType.SOURCE, "10", EvidenceRelation.SUPPORTS, "L42"),
        _ev("db/schema.sql", EvidenceType.SQL, "10", EvidenceRelation.SUPPORTS),
    ])
    conflicts = detect_conflicts([ec], "owner-management")
    assert len(conflicts) == 1
    assert conflicts[0].type == ConflictType.VALUE_MISMATCH
    assert conflicts[0].claim == "owner.telephone.max_length"
    assert len(conflicts[0].values) == 2  # 20 vs 10 (정규화 대표)


def test_c2_stale_knowledge() -> None:
    # 설계 노트(문서)는 "rejected", 코드는 검증 없이 "accepted" → 문서/구현 드리프트
    ec = ExtractedClaim(subject="pet.birthdate", predicate="future_date_validation", evidence=[
        _ev("docs/maintenance-notes.md", EvidenceType.MARKDOWN, "rejected", EvidenceRelation.SUPPORTS),
        _ev("src/Pet.java", EvidenceType.SOURCE, "accepted", EvidenceRelation.CONTRADICTS, "L20"),
    ])
    conflicts = detect_conflicts([ec], "pet-care")
    assert len(conflicts) == 1
    assert conflicts[0].type == ConflictType.STALE_KNOWLEDGE


def test_c3_policy_conflict() -> None:
    # 사양(문서)은 email 필수, 구현/스키마엔 부재 → 정책 충돌
    ec = ExtractedClaim(subject="owner.email", predicate="required", evidence=[
        _ev("docs/spec.pdf", EvidenceType.PDF, "required", EvidenceRelation.SUPPORTS, "p.2"),
        _ev("openapi/petclinic.yaml", EvidenceType.OPENAPI, "absent", EvidenceRelation.CONTRADICTS),
        _ev("src/Owner.java", EvidenceType.SOURCE, "absent", EvidenceRelation.CONTRADICTS),
    ])
    conflicts = detect_conflicts([ec], "owner-management")
    assert len(conflicts) == 1
    assert conflicts[0].type == ConflictType.POLICY_CONFLICT


# --- 건전성 & 결정성 ----------------------------------------------------------
def test_no_conflict_when_values_agree() -> None:
    ec = ExtractedClaim(subject="owner.telephone", predicate="max_length", evidence=[
        _ev("src/Owner.java", EvidenceType.SOURCE, "10", EvidenceRelation.SUPPORTS),
        _ev("db/schema.sql", EvidenceType.SQL, "10", EvidenceRelation.SUPPORTS),
    ])
    assert detect_conflicts([ec], "f") == []


def test_no_conflict_with_single_value() -> None:
    ec = ExtractedClaim(subject="a", predicate="b", evidence=[
        _ev("s.md", EvidenceType.MARKDOWN, "x", EvidenceRelation.MENTIONS),
    ])
    assert detect_conflicts([ec], "f") == []


def test_classify_falls_back_to_value_mismatch() -> None:
    # 부재도 행위서술도 아닌 순수 스칼라 → value_mismatch (폴백)
    ec = ExtractedClaim(subject="p.size", predicate="limit", evidence=[])
    assert classify_conflict_type(ec, [("100", "a.md", "L1"), ("200", "b.sql", "L2")]) \
        == ConflictType.VALUE_MISMATCH


def test_detect_is_sorted_by_claim() -> None:
    ec_b = ExtractedClaim(subject="z", predicate="p", evidence=[
        _ev("a.md", EvidenceType.MARKDOWN, "1", EvidenceRelation.SUPPORTS),
        _ev("b.java", EvidenceType.SOURCE, "2", EvidenceRelation.SUPPORTS),
    ])
    ec_a = ExtractedClaim(subject="a", predicate="p", evidence=[
        _ev("a.md", EvidenceType.MARKDOWN, "1", EvidenceRelation.SUPPORTS),
        _ev("b.java", EvidenceType.SOURCE, "2", EvidenceRelation.SUPPORTS),
    ])
    conflicts = detect_conflicts([ec_b, ec_a], "f")
    assert [c.claim for c in conflicts] == sorted(c.claim for c in conflicts)

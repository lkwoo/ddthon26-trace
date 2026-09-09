"""UOW-04 매핑/강등 단위 테스트 — to_impact_out (BR-IMP-003/004/005)."""

from __future__ import annotations

from trace.impact.analyze import to_impact_out
from trace.impact.context import KnowledgeContext
from trace.models.domain import (
    Conflict,
    ConflictValue,
    ImpactCategory,
)
from trace.models.impact import ImpactCandidate, TaskImpactResult
from trace.models.result import EvidenceRef


def _ctx(known: set[str], conflicts=None) -> KnowledgeContext:
    return KnowledgeContext(task="t", known_sources=known, conflicts=conflicts or [])


def _ev(source: str) -> EvidenceRef:
    return EvidenceRef(source=source, location="L1", relation="supports")


def test_known_path_with_evidence_stays_must() -> None:
    result = TaskImpactResult(candidates=[
        ImpactCandidate(path="src/Owner.java", category=ImpactCategory.MUST_CHANGE,
                        reason="검증 대상", evidence=[_ev("src/Owner.java")]),
    ])
    out = to_impact_out(result, _ctx({"src/Owner.java"}))
    assert [it.path for it in out.must_change] == ["src/Owner.java"]
    assert out.review == []


def test_foreign_path_demoted_to_review() -> None:
    result = TaskImpactResult(candidates=[
        ImpactCandidate(path="src/Ghost.java", category=ImpactCategory.MUST_CHANGE,
                        reason="추정", evidence=[_ev("src/Ghost.java")]),
    ])
    out = to_impact_out(result, _ctx({"src/Owner.java"}))
    assert out.must_change == []
    assert len(out.review) == 1
    assert "근거 밖 추정" in out.review[0].reason


def test_no_evidence_demoted_with_insufficient() -> None:
    result = TaskImpactResult(candidates=[
        ImpactCandidate(path="src/Owner.java", category=ImpactCategory.LIKELY_CHANGE,
                        reason="아마도", evidence=[]),
    ])
    out = to_impact_out(result, _ctx({"src/Owner.java"}))
    assert out.likely_change == []
    assert out.review and "Insufficient evidence" in out.review[0].reason


def test_categories_sorted_by_path() -> None:
    result = TaskImpactResult(candidates=[
        ImpactCandidate(path="src/Z.java", category=ImpactCategory.MUST_CHANGE, reason="r", evidence=[_ev("src/Z.java")]),
        ImpactCandidate(path="src/A.java", category=ImpactCategory.MUST_CHANGE, reason="r", evidence=[_ev("src/A.java")]),
    ])
    out = to_impact_out(result, _ctx({"src/Z.java", "src/A.java"}))
    assert [it.path for it in out.must_change] == ["src/A.java", "src/Z.java"]


def test_related_conflicts_surfaced_from_context() -> None:
    conflict = Conflict(claim="owner.telephone.max_length",
                        values=[ConflictValue(value="20", source="docs/spec.md", location="p.3"),
                                ConflictValue(value="10", source="src/Owner.java", location="L42")],
                        interpretation="충돌")
    out = to_impact_out(TaskImpactResult(), _ctx({"src/Owner.java"}, conflicts=[conflict]))
    assert len(out.related_conflicts) == 1
    assert out.related_conflicts[0].claim == "owner.telephone.max_length"


def test_change_plan_passed_through() -> None:
    result = TaskImpactResult(change_plan=["1. 충돌 해소", "2. API"])
    out = to_impact_out(result, _ctx(set()))
    assert out.change_plan == ["1. 충돌 해소", "2. API"]

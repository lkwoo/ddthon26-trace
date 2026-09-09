"""UOW-04 속성 기반 테스트 (PBT-04-A~D).

to_impact_out은 순수 함수 → FakeLLM 없이 결정적으로 검증한다.
"""

from __future__ import annotations

import random

from hypothesis import given, settings
from hypothesis import strategies as st

from trace.impact.analyze import to_impact_out
from trace.impact.context import KnowledgeContext
from trace.models.domain import Conflict, ConflictValue, ImpactCategory
from trace.models.impact import ImpactCandidate, TaskImpactResult
from trace.models.result import EvidenceRef

PBT = settings(derandomize=True, max_examples=80, deadline=None)

_paths = st.sampled_from(["a", "b", "c", "d"])


@st.composite
def _evidence_ref(draw) -> EvidenceRef:  # type: ignore[no-untyped-def]
    return EvidenceRef(
        source=draw(st.text(min_size=1, max_size=4)),
        location=draw(st.text(min_size=1, max_size=3)),
        relation=draw(st.sampled_from(["supports", "contradicts", "mentions"])),
    )


@st.composite
def _candidate(draw) -> ImpactCandidate:  # type: ignore[no-untyped-def]
    return ImpactCandidate(
        path=draw(_paths),
        category=draw(st.sampled_from(list(ImpactCategory))),
        reason=draw(st.text(min_size=1, max_size=8)),
        evidence=draw(st.lists(_evidence_ref(), max_size=3)),
    )


def _conflicts(n: int) -> list[Conflict]:
    return [
        Conflict(claim=f"s{i}.p", values=[
            ConflictValue(value="20", source="docs/x.md", location="p.1"),
            ConflictValue(value="10", source="src/y.java", location="L1"),
        ], interpretation="c")
        for i in range(n)
    ]


@st.composite
def _fixture(draw):  # type: ignore[no-untyped-def]
    candidates = draw(st.lists(_candidate(), max_size=6))
    known = set(draw(st.lists(_paths, max_size=4)))
    conflicts = _conflicts(draw(st.integers(min_value=0, max_value=3)))
    return candidates, known, conflicts


# PBT-04-A & B: must/likely 항목은 항상 known_sources 안 + 근거 존재
@PBT
@given(fx=_fixture())
def test_promoted_items_are_grounded(fx) -> None:  # type: ignore[no-untyped-def]
    candidates, known, conflicts = fx
    ctx = KnowledgeContext(task="t", known_sources=known, conflicts=conflicts)
    out = to_impact_out(TaskImpactResult(candidates=candidates), ctx)
    for it in (*out.must_change, *out.likely_change):
        assert it.path in known          # PBT-04-A: 허구 path는 승격 불가
        assert it.evidence               # PBT-04-B: 근거 없는 항목은 승격 불가


# PBT-04-C: 정렬 결정성/멱등 (후보 순서 무관)
@PBT
@given(fx=_fixture())
def test_mapping_is_order_independent(fx) -> None:  # type: ignore[no-untyped-def]
    candidates, known, conflicts = fx
    ctx = KnowledgeContext(task="t", known_sources=known, conflicts=conflicts)
    first = to_impact_out(TaskImpactResult(candidates=candidates), ctx).model_dump()

    shuffled = list(candidates)
    random.Random(0).shuffle(shuffled)
    second = to_impact_out(TaskImpactResult(candidates=shuffled), ctx).model_dump()
    assert first == second


# PBT-04-D: related_conflicts 정합
@PBT
@given(fx=_fixture())
def test_related_conflicts_count_matches(fx) -> None:  # type: ignore[no-untyped-def]
    candidates, known, conflicts = fx
    ctx = KnowledgeContext(task="t", known_sources=known, conflicts=conflicts)
    out = to_impact_out(TaskImpactResult(candidates=candidates), ctx)
    assert len(out.related_conflicts) == len(conflicts)

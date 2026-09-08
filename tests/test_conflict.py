"""UOW-03 Claims/Evidence/Conflict 테스트 — TRACE 구조적 차별점 검증.

충돌 검출·신뢰도 산정은 결정적 순수 함수이므로 속성 기반 테스트(Hypothesis)로 불변식을 검증한다.
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from trace.config import Config, LLMSettings
from trace.conflict import (
    assign_confidence,
    detect_conflicts,
    get_conflicts,
    normalize_value,
)
from trace.engine.pipeline import analyze_project
from trace.knowledge import KnowledgeStore
from trace.models import (
    Claim,
    Confidence,
    ConflictType,
    Evidence,
    EvidenceRelation,
)

DEMO = Path(__file__).resolve().parents[1] / "demo"
REPLAY = DEMO / "replay"


def _claim(value: str, sources: list[str], relation=EvidenceRelation.DIRECT) -> Claim:
    return Claim(
        "Owner.telephone", "max_length", value,
        evidence=[Evidence(s, "source", "", value, relation) for s in sources],
    )


# ------------------------------------------------------ 결정성/불변식 (속성)
@given(st.lists(st.text(min_size=1, max_size=6), min_size=1, max_size=5))
def test_detect_conflicts_never_flags_agreement(values_same):
    # 같은 정규화 값만 있으면 (다른 표기여도) 충돌 아님
    claims = [_claim(v, [f"s{i}.txt"]) for i, v in enumerate([values_same[0]] * 3)]
    assert detect_conflicts(claims) == []


@given(st.integers(min_value=1, max_value=99), st.integers(min_value=1, max_value=99))
def test_detect_conflicts_symmetric_on_disagreement(a, b):
    claims = [_claim(str(a), ["spec.pdf"]), _claim(str(b), ["code.java"])]
    conflicts = detect_conflicts(claims)
    if a == b:
        assert conflicts == []
    else:
        assert len(conflicts) == 1
        assert conflicts[0].type == ConflictType.VALUE_MISMATCH
        assert conflicts[0].claim == "Owner.telephone.max_length"
        # 두 값 모두 근거와 함께 보존
        vals = {v.value for v in conflicts[0].values}
        assert vals == {str(a), str(b)}


def test_detect_conflicts_is_deterministic():
    claims = [_claim("20", ["spec.pdf"]), _claim("10", ["a.sql", "b.yaml"])]
    first = [c.to_dict() for c in detect_conflicts(claims)]
    second = [c.to_dict() for c in detect_conflicts(list(reversed(claims)))]
    assert first == second  # 입력 순서와 무관 (안정 정렬)


@given(st.text())
def test_normalize_value_idempotent(v):
    assert normalize_value(normalize_value(v)) == normalize_value(v)


# --------------------------------------------------------- 신뢰도 (FR-CONFIDENCE-001)
def test_confidence_from_evidence_agreement():
    two_support = _claim("10", ["a", "b"])
    assert assign_confidence(two_support) == Confidence.HIGH
    one = _claim("10", ["a"])
    assert assign_confidence(one) == Confidence.MEDIUM
    none = Claim("X", "y", "1", evidence=[])
    assert assign_confidence(none) == Confidence.LOW


def test_confidence_low_when_contradicted():
    c = Claim("X", "y", "1", evidence=[
        Evidence("a", "source", "", "1", EvidenceRelation.SUPPORTING),
        Evidence("b", "source", "", "2", EvidenceRelation.CONTRADICTING),
    ])
    assert assign_confidence(c) == Confidence.LOW


# --------------------------------------------------------- E2E (replay) Hero 충돌
def test_hero_value_mismatch_detected_e2e(tmp_path):
    store = KnowledgeStore(tmp_path)
    cfg = Config(llm=LLMSettings(backend="replay", replay_dir=str(REPLAY)))
    r = analyze_project(str(DEMO), config=cfg, store=store, refresh=True)
    assert r.data["conflicts_count"] == 1

    gc = get_conflicts(store=store)
    assert gc.meta["conflicts_count"] == 1
    conflict = gc.conflicts[0]
    assert conflict["claim"] == "Owner.telephone.max_length"
    values = {v["value"] for v in conflict["values"]}
    assert values == {"10", "20"}
    # 요구(20)는 PDF, 명세/구현(10)은 code/spec 소스에서 인용됐는지
    src_by_val = {v["value"]: v["source"] for v in conflict["values"]}
    assert "pdf" in src_by_val["20"]

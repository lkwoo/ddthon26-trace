"""UOW-0F 도메인 모델 테스트 — 단위 + 속성(PBT).

직렬화 왕복(to_dict→from_dict)은 순수 로직이라 속성 테스트에 적합하다(PBT-01, Q10=A).
어떤 무작위 Claim/Evidence/Conflict/FeatureKnowledge도 왕복 후 동일해야 한다.
"""

from __future__ import annotations

from hypothesis import given, strategies as st

from trace.models import (
    Claim,
    Confidence,
    Conflict,
    ConflictType,
    ConflictValue,
    Evidence,
    EvidenceRelation,
    Feature,
    FeatureKnowledge,
)

text = st.text(max_size=40)

evidence_st = st.builds(
    Evidence,
    source=st.text(min_size=1, max_size=30),
    type=st.sampled_from(["openapi", "source", "sql", "requirement", "config", "test"]),
    location=text,
    extracted_value=text,
    relation=st.sampled_from(list(EvidenceRelation)),
)

claim_st = st.builds(
    Claim,
    subject=st.text(min_size=1, max_size=20),
    predicate=st.text(min_size=1, max_size=20),
    value=st.text(min_size=1, max_size=20),
    evidence=st.lists(evidence_st, max_size=4),
    confidence=st.sampled_from(list(Confidence)),
)

conflict_st = st.builds(
    Conflict,
    type=st.sampled_from(list(ConflictType)),
    claim=st.text(min_size=1, max_size=20),
    values=st.lists(
        st.builds(ConflictValue, value=text, source=st.text(min_size=1, max_size=20), location=text),
        max_size=4,
    ),
    interpretation=text,
)


@given(evidence_st)
def test_evidence_roundtrip(ev: Evidence):
    assert Evidence.from_dict(ev.to_dict()) == ev


@given(claim_st)
def test_claim_roundtrip(c: Claim):
    assert Claim.from_dict(c.to_dict()) == c


@given(conflict_st)
def test_conflict_roundtrip(cf: Conflict):
    assert Conflict.from_dict(cf.to_dict()) == cf


@given(
    st.builds(
        FeatureKnowledge,
        feature=st.builds(
            Feature,
            id=st.text(min_size=1, max_size=15),
            title=st.text(min_size=1, max_size=30),
            description=text,
            related_sources=st.lists(st.text(min_size=1, max_size=20), max_size=4),
        ),
        overview=text,
        business_rules=st.lists(text, max_size=4),
        claims=st.lists(claim_st, max_size=3),
        conflicts=st.lists(conflict_st, max_size=3),
        dependencies=st.lists(text, max_size=3),
        confidence=st.sampled_from(list(Confidence)),
    )
)
def test_feature_knowledge_roundtrip(fk: FeatureKnowledge):
    assert FeatureKnowledge.from_dict(fk.to_dict()) == fk


@given(claim_st)
def test_claim_key_is_stable(c: Claim):
    """정규화 키는 subject.predicate 이며 공백에 안정적이어야 한다(충돌 그룹핑의 기반)."""
    assert c.key == f"{c.subject.strip()}.{c.predicate.strip()}"


def test_feature_knowledge_all_evidence_collects_from_claims():
    fk = FeatureKnowledge(
        feature=Feature(id="f1", title="F"),
        claims=[
            Claim("Owner.telephone", "max_length", "10", evidence=[Evidence("a.sql", "sql")]),
            Claim("Owner.telephone", "max_length", "20", evidence=[Evidence("req.pdf", "requirement")]),
        ],
    )
    assert len(fk.all_evidence) == 2

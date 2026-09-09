"""직렬화 결정성·round-trip 속성 테스트 (PBT, NFR-0F-DET-1/TST-2)."""

from __future__ import annotations

from hypothesis import given, settings
from hypothesis import strategies as st

from trace.models.domain import (
    Claim,
    Feature,
    FeatureKnowledge,
    make_feature_id,
)
from trace.models.serialize import deserialize, serialize


def test_round_trip_preserves_knowledge(sample_feature_knowledge):
    text = serialize(sample_feature_knowledge)
    restored = deserialize(text)
    assert restored.feature.id == sample_feature_knowledge.feature.id
    assert len(restored.claims) == len(sample_feature_knowledge.claims)
    assert len(restored.conflicts) == len(sample_feature_knowledge.conflicts)


def test_serialize_is_deterministic(sample_feature_knowledge):
    assert serialize(sample_feature_knowledge) == serialize(sample_feature_knowledge)


def test_round_trip_is_idempotent(sample_feature_knowledge):
    once = serialize(sample_feature_knowledge)
    twice = serialize(deserialize(once))
    assert once == twice


# ---- Property-based ---- #
_text = st.text(
    alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=8
)


@st.composite
def feature_knowledge(draw) -> FeatureKnowledge:
    title = draw(_text)
    fid = make_feature_id(title)
    n = draw(st.integers(min_value=0, max_value=3))
    claims = [
        Claim(
            subject=draw(_text),
            predicate=draw(_text),
            value=draw(_text),
            feature_id=fid,
        )
        for _ in range(n)
    ]
    return FeatureKnowledge(
        feature=Feature(id=fid, title=title, description=draw(_text)),
        claims=claims,
    )


@settings(max_examples=50)
@given(fk=feature_knowledge())
def test_pbt_round_trip_idempotent(fk: FeatureKnowledge):
    once = serialize(fk)
    twice = serialize(deserialize(once))
    assert once == twice


@settings(max_examples=50)
@given(fk=feature_knowledge())
def test_pbt_deserialize_recovers_feature_id(fk: FeatureKnowledge):
    restored = deserialize(serialize(fk))
    assert restored.feature.id == fk.feature.id

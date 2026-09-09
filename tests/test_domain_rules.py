"""도메인 규칙 테스트: slug·정규화·검증·충돌 (BR-ID/NORM/VAL/CONFLICT)."""

from __future__ import annotations

import pytest
from hypothesis import given
from hypothesis import strategies as st
from pydantic import ValidationError

from trace.models.domain import (
    Conflict,
    ConflictValue,
    Feature,
    make_feature_id,
    make_unique_feature_id,
    normalize_value,
)


def test_make_feature_id_kebab():
    assert make_feature_id("Owner Registration") == "owner-registration"
    assert make_feature_id("  Pet__Type!!  ") == "pet-type"
    assert make_feature_id("!!!") == "feature"


@given(st.text())
def test_make_feature_id_idempotent(s: str):
    once = make_feature_id(s)
    assert make_feature_id(once) == once


@given(st.text())
def test_make_feature_id_charset(s: str):
    import re

    assert re.fullmatch(r"[a-z0-9-]+", make_feature_id(s))


def test_make_unique_feature_id():
    existing = {"owner-registration"}
    assert make_unique_feature_id("Owner Registration", existing) == "owner-registration-2"


def test_normalize_numeric_equivalence():
    assert normalize_value("20") == normalize_value("20.0")
    assert normalize_value(' "20" ') == normalize_value("20")


def test_normalize_idempotent():
    once = normalize_value("  Hello  ")
    assert normalize_value(once) == once


def test_feature_id_must_be_path_safe():
    with pytest.raises(ValidationError):
        Feature(id="../evil", title="t", description="d")


def test_conflict_requires_two_distinct_values():
    with pytest.raises(ValidationError):
        Conflict(
            claim="x.y",
            values=[ConflictValue(value="10", source="a", location="L1")],
            interpretation="only one",
        )
    with pytest.raises(ValidationError):
        Conflict(
            claim="x.y",
            values=[
                ConflictValue(value="10", source="a", location="L1"),
                ConflictValue(value="10.0", source="b", location="L2"),
            ],
            interpretation="not distinct after normalization",
        )


def test_conflict_valid_with_distinct_values():
    c = Conflict(
        claim="owner.telephone.max_length",
        values=[
            ConflictValue(value="20", source="req.pdf", location="p3"),
            ConflictValue(value="10", source="Owner.java", location="L42"),
        ],
        interpretation="요구 20 vs 구현 10",
    )
    assert len(c.values) == 2

"""C4 도메인 모델 (UOW-0F).

Functional Design의 domain-entities.md 계약을 Pydantic v2 모델로 동결한다.
이후 UOW-01~06이 이 모델을 임포트한다. business-rules.md의 BR-ID/NORM/VAL/CONFLICT 반영.
"""

from __future__ import annotations

import re
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# --------------------------------------------------------------------------- #
# Enums (도메인 값 집합 고정)
# --------------------------------------------------------------------------- #
class Confidence(str, Enum):
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvidenceRelation(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    MENTIONS = "mentions"


class EvidenceType(str, Enum):
    SOURCE = "source"
    OPENAPI = "openapi"
    SQL = "sql"
    CONFIG = "config"
    TEST = "test"
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class ConflictType(str, Enum):
    VALUE_MISMATCH = "value_mismatch"      # P0: 구체 값 스칼라 불일치 (예: 20 vs 10)
    STALE_KNOWLEDGE = "stale_knowledge"    # P1: 문서/지식이 구현과 어긋남(드리프트)
    POLICY_CONFLICT = "policy_conflict"    # P1: 요구(필수/규정) vs 구현 부재


class ImpactCategory(str, Enum):
    MUST_CHANGE = "must_change"
    LIKELY_CHANGE = "likely_change"
    REVIEW = "review"


# --------------------------------------------------------------------------- #
# 헬퍼: ID 생성 / 값 정규화 (business-rules §ID, §정규화)
# --------------------------------------------------------------------------- #
_SLUG_STRIP = re.compile(r"[^a-z0-9]+")
_SLUG_EDGES = re.compile(r"^-+|-+$")


def make_feature_id(title: str) -> str:
    """제목을 kebab-case slug로 변환 (BR-ID-001~004).

    소문자화 → 영숫자 외를 '-'로 → 연속 '-' 축약 → 양끝 '-' 제거.
    빈 결과는 'feature'로 대체. 결과는 항상 ^[a-z0-9-]+$ 이며 멱등.
    (유일화 -2/-3 접미사는 호출측이 make_unique_feature_id로 처리)
    """
    slug = _SLUG_STRIP.sub("-", title.lower())
    slug = _SLUG_EDGES.sub("", slug)
    return slug or "feature"


def make_unique_feature_id(title: str, existing: set[str]) -> str:
    """같은 분석 내 slug 충돌 시 -2, -3 … 접미사로 유일화 (BR-ID-003)."""
    base = make_feature_id(title)
    if base not in existing:
        return base
    n = 2
    while f"{base}-{n}" in existing:
        n += 1
    return f"{base}-{n}"


def normalize_value(value: str) -> str:
    """값 비교용 정규화 (BR-NORM-001). 표시값은 보존하고 비교시에만 사용.

    앞뒤 공백·따옴표 제거, 소문자화. 순수 숫자는 숫자 동등성으로 비교되도록
    후행 0/소수점을 정리한다 ("20" == "20.0").
    """
    v = value.strip().strip("'\"").strip()
    lowered = v.lower()
    try:
        num = float(v)
        # 정수면 정수 문자열로, 아니면 float 정규형
        return str(int(num)) if num.is_integer() else repr(num)
    except ValueError:
        return lowered


def claim_key(subject: str, predicate: str) -> str:
    """신뢰도·충돌 그룹핑 키 (BR-NORM-002)."""
    return f"{subject.strip()}.{predicate.strip()}"


# --------------------------------------------------------------------------- #
# 코어 엔티티
# --------------------------------------------------------------------------- #
class Feature(BaseModel):
    id: str = Field(..., min_length=1)
    title: str = Field(..., min_length=1)
    description: str = Field(..., min_length=1)
    related_sources: list[str] = Field(default_factory=list)

    @field_validator("id")
    @classmethod
    def _id_safe(cls, v: str) -> str:
        # BR-ID-004: 파일명/URI 안전 — 경로 구분자·상위참조 금지
        if "/" in v or "\\" in v or ".." in v:
            raise ValueError(f"unsafe feature id: {v!r}")
        return v


class Claim(BaseModel):
    subject: str = Field(..., min_length=1)
    predicate: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    feature_id: str = Field(..., min_length=1)

    @property
    def key(self) -> str:
        return claim_key(self.subject, self.predicate)


class Evidence(BaseModel):
    source: str = Field(..., min_length=1)
    type: EvidenceType
    location: str = Field(..., min_length=1)
    extracted_value: str | None = None
    relation: EvidenceRelation


class ConfidenceAssessment(BaseModel):
    level: Confidence
    reason: str = Field(..., min_length=1)  # BR-CONF-002: 사유 필수


class ClaimConfidence(BaseModel):
    claim_key: str = Field(..., min_length=1)
    assessment: ConfidenceAssessment


class ConflictValue(BaseModel):
    value: str = Field(..., min_length=1)
    source: str = Field(..., min_length=1)
    location: str = Field(..., min_length=1)


class Conflict(BaseModel):
    type: ConflictType = ConflictType.VALUE_MISMATCH
    claim: str = Field(..., min_length=1)
    values: list[ConflictValue]
    interpretation: str = Field(..., min_length=1)  # BR-CONFLICT-002

    @field_validator("values")
    @classmethod
    def _at_least_two_distinct(cls, v: list[ConflictValue]) -> list[ConflictValue]:
        # BR-VAL-004 / BR-CONFLICT-001: 서로 다른 값 2개 이상이어야 충돌 성립
        if len(v) < 2:
            raise ValueError("conflict requires at least 2 values")
        if len({normalize_value(cv.value) for cv in v}) < 2:
            raise ValueError("conflict values must be distinct after normalization")
        return v


class FeatureKnowledge(BaseModel):
    """한 Feature의 지식 전체 (집계 루트). .trace/knowledge/features/<id>.md 로 영속."""

    feature: Feature
    claims: list[Claim] = Field(default_factory=list)
    evidence: list[Evidence] = Field(default_factory=list)
    confidence: list[ClaimConfidence] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    body_markdown: str = ""
    meta: dict = Field(default_factory=dict)

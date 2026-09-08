"""C4 도메인 모델 — TRACE 지식 표현의 단일 진실원 (UOW-0F, 계약 동결).

핵심 구조적 차별점(요구사항 §1.3): RAG는 '비슷한 것'을 찾지만, TRACE는 정규화된
Claim(subject·predicate·value) ↔ Evidence 링크를 만들고 같은 Claim에 붙은 서로 다른 값을
value_mismatch 충돌로 검출한다. 이 모듈은 그 표현을 정의한다.

모든 모델은 순수 데이터(dataclass)이며 외부 의존성이 없다 → 오프라인 단위/속성 테스트 가능.
직렬화는 `to_dict`/`from_dict`(JSON/딕셔너리)로 왕복 가능하도록 설계한다(속성 테스트 대상).
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class Confidence(str, Enum):
    """근거 일치도 기반 신뢰도 (FR-CONFIDENCE-001). LLM 자기확신이 아니라 Evidence 일치도로 산정."""

    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class EvidenceRelation(str, Enum):
    """Claim과 Evidence의 관계 (FR-EVIDENCE-001)."""

    DIRECT = "direct"            # 값을 직접 명시
    SUPPORTING = "supporting"    # 값을 뒷받침
    RELATED = "related"          # 관련은 있으나 값 미명시
    CONTRADICTING = "contradicting"  # 값과 충돌


class ConflictType(str, Enum):
    """충돌 유형. value_mismatch만 P0, 나머지는 P1."""

    VALUE_MISMATCH = "value_mismatch"                # 같은 Claim, 다른 값 (P0)
    MISSING_IMPLEMENTATION = "missing_implementation"  # 문서엔 있으나 구현 없음 (P1)
    UNDOCUMENTED_BEHAVIOR = "undocumented_behavior"    # 구현엔 있으나 문서 없음 (P1)


@dataclass
class Evidence:
    """Claim을 뒷받침/반박하는 실제 자산 근거 (근거 그라운딩, NFR-AI-002)."""

    source: str                       # 자산 경로 (프로젝트 상대경로)
    type: str                         # 자산 유형 (openapi, source, sql, requirement, config, test ...)
    location: str = ""                # 위치 힌트 (예: "line 42", "paths./owners.post", "§3.2")
    extracted_value: str = ""         # 이 근거에서 추출한 원자 값
    relation: EvidenceRelation = EvidenceRelation.SUPPORTING

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["relation"] = self.relation.value
        return d

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Evidence":
        return cls(
            source=d["source"],
            type=d.get("type", ""),
            location=d.get("location", ""),
            extracted_value=d.get("extracted_value", ""),
            relation=EvidenceRelation(d.get("relation", "supporting")),
        )


@dataclass
class Claim:
    """정규화 원자 Claim (FR-CLAIM-001): subject + predicate + value.

    예) subject="Owner.telephone", predicate="max_length", value="10".
    같은 (subject, predicate)에 서로 다른 value를 주장하는 Claim/Evidence가 있으면 충돌이다.
    """

    subject: str
    predicate: str
    value: str
    evidence: list[Evidence] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM

    @property
    def key(self) -> str:
        """정규화 키 — subject.predicate. 충돌 비교의 그룹핑 단위."""
        return f"{self.subject.strip()}.{self.predicate.strip()}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "subject": self.subject,
            "predicate": self.predicate,
            "value": self.value,
            "confidence": self.confidence.value,
            "evidence": [e.to_dict() for e in self.evidence],
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Claim":
        return cls(
            subject=d["subject"],
            predicate=d["predicate"],
            value=str(d["value"]),
            confidence=Confidence(d.get("confidence", "MEDIUM")),
            evidence=[Evidence.from_dict(e) for e in d.get("evidence", [])],
        )


@dataclass
class ConflictValue:
    """충돌에 참여하는 하나의 값과 그 근거 소스 (FR-CONFLICT-OUT-002)."""

    value: str
    source: str
    location: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "ConflictValue":
        return cls(value=str(d["value"]), source=d["source"], location=d.get("location", ""))


@dataclass
class Conflict:
    """검출된 충돌 (FR-CONFLICT-001). value_mismatch가 1급 산출물."""

    type: ConflictType
    claim: str                        # 충돌이 걸린 정규화 Claim 키 (subject.predicate)
    values: list[ConflictValue] = field(default_factory=list)
    interpretation: str = ""          # 사람이 읽는 짧은 해석 (소스가 항상 옳다고 가정하지 않음)

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "claim": self.claim,
            "values": [v.to_dict() for v in self.values],
            "interpretation": self.interpretation,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Conflict":
        return cls(
            type=ConflictType(d.get("type", "value_mismatch")),
            claim=d["claim"],
            values=[ConflictValue.from_dict(v) for v in d.get("values", [])],
            interpretation=d.get("interpretation", ""),
        )


@dataclass
class Feature:
    """검출된 기능 (FR-KNOWLEDGE-001, 자동 검출)."""

    id: str
    title: str
    description: str = ""
    related_sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "Feature":
        return cls(
            id=d["id"],
            title=d["title"],
            description=d.get("description", ""),
            related_sources=list(d.get("related_sources", [])),
        )


@dataclass
class FeatureKnowledge:
    """Feature 중심 지식 뷰 (FR-KNOWLEDGE-002). MD+YAML 단일 진실원으로 영속화된다.

    구조화 값(claims/evidence/conflicts)은 YAML front matter에 1회만 저장하고,
    사람이 읽는 서술(overview/business_rules)은 Markdown 본문에 둔다(NFR-MAINT-002 정신).
    """

    feature: Feature
    overview: str = ""
    business_rules: list[str] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    conflicts: list[Conflict] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    confidence: Confidence = Confidence.MEDIUM

    @property
    def all_evidence(self) -> list[Evidence]:
        """지식에 연결된 모든 근거 (교차소스 연결 확인용, FR-KNOWLEDGE-003)."""
        out: list[Evidence] = []
        for c in self.claims:
            out.extend(c.evidence)
        return out

    def to_dict(self) -> dict[str, Any]:
        return {
            "feature": self.feature.to_dict(),
            "overview": self.overview,
            "business_rules": list(self.business_rules),
            "claims": [c.to_dict() for c in self.claims],
            "conflicts": [c.to_dict() for c in self.conflicts],
            "dependencies": list(self.dependencies),
            "confidence": self.confidence.value,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FeatureKnowledge":
        return cls(
            feature=Feature.from_dict(d["feature"]),
            overview=d.get("overview", ""),
            business_rules=list(d.get("business_rules", [])),
            claims=[Claim.from_dict(c) for c in d.get("claims", [])],
            conflicts=[Conflict.from_dict(c) for c in d.get("conflicts", [])],
            dependencies=list(d.get("dependencies", [])),
            confidence=Confidence(d.get("confidence", "MEDIUM")),
        )


__all__ = [
    "Confidence",
    "EvidenceRelation",
    "ConflictType",
    "Evidence",
    "Claim",
    "ConflictValue",
    "Conflict",
    "Feature",
    "FeatureKnowledge",
]

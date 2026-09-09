"""Claim 추출 · Confidence · 완본화 (UOW-03, C3, NFR Design P1/P2/P3/P5, BR-CLAIM/EVID/CONF/PIPE).

- extract_claims: Feature당 1회 구조화 호출 → ExtractedClaim 목록 (허구근거 드롭, 실패 시 warning 강등).
- assign_confidence: 근거 일치도 기반 비-LLM 신뢰도 (BR-CONF, 순수 함수).
- enrich_feature_knowledge: 지식 셸(UOW-02)을 원자 Claim·Evidence·Confidence·Conflict로 완본화.
"""

from __future__ import annotations

from collections import Counter

from trace.common.errors import TraceError, sanitize_error
from trace.common.logging import get_logger
from trace.conflict.detect import detect_conflicts
from trace.llm.service import LLMService
from trace.models.asset import Asset
from trace.models.domain import (
    Claim,
    ClaimConfidence,
    Confidence,
    ConfidenceAssessment,
    EvidenceRelation,
    Feature,
    FeatureKnowledge,
    claim_key,
    normalize_value,
)
from trace.models.extraction import ClaimExtractionResult, ExtractedClaim
from trace.models.result import Warning
from trace.prompts.loader import get_prompt
from trace.workflow.catalog import build_catalog, render_catalog

_log = get_logger("trace.workflow.claims")


def extract_claims(
    feature: Feature, assets: list[Asset], llm: LLMService
) -> tuple[list[ExtractedClaim], list[Warning]]:
    """Feature의 관련 자산에서 원자 Claim과 Evidence를 1회 구조화 호출로 추출한다.

    허구 소스(스캔되지 않은 rel_path)의 Evidence는 드롭 + warning (BR-EVID-004).
    LLM 실패는 이 Feature에서 포착해 빈 목록 + warning 강등(BR-PIPE-002).
    """
    related_paths = set(feature.related_sources)
    related = [a for a in assets if a.rel_path in related_paths]
    warnings: list[Warning] = []

    prompt = get_prompt(
        "extract_claims",
        feature_title=feature.title,
        feature_description=feature.description,
        sources=render_catalog(build_catalog(related)) if related else "(연결된 자산 없음)",
    )
    try:
        result = llm.complete_structured(prompt, ClaimExtractionResult)
    except TraceError as exc:
        _log.warning(f"event=extract_failed id={feature.id}")
        return [], [Warning(code="extract_failed",
                            message=f"Claim 추출 실패: {sanitize_error(exc)}",
                            source=feature.id)]

    # 스캔된 자산 rel_path 전체(허구 소스 판별 기준) — 관련 목록에 한정하지 않고 실재 여부로 판정
    scanned_paths = {a.rel_path for a in assets}
    cleaned: list[ExtractedClaim] = []
    for ec in result.claims:
        kept = [e for e in ec.evidence if e.source in scanned_paths]
        if len(kept) != len(ec.evidence):
            warnings.append(Warning(
                code="fictitious_evidence_dropped",
                message="스캔되지 않은 소스의 근거를 드롭했습니다",
                source=f"{feature.id}:{claim_key(ec.subject, ec.predicate)}",
            ))
        cleaned.append(ec.model_copy(update={"evidence": kept}))
    return cleaned, warnings


def assign_confidence(ec: ExtractedClaim) -> ClaimConfidence:
    """근거 일치도 기반 신뢰도 (BR-CONF, 비-LLM 순수 함수).

    distinct(정규화 상이값 수)·contradicts·supports 로 LOW/HIGH/MEDIUM 결정.
    """
    values = {
        normalize_value(e.extracted_value)
        for e in ec.evidence
        if e.extracted_value is not None and e.extracted_value.strip()
    }
    supports = sum(1 for e in ec.evidence if e.relation == EvidenceRelation.SUPPORTS)
    contradicts = sum(1 for e in ec.evidence if e.relation == EvidenceRelation.CONTRADICTS)
    has_contradiction = contradicts > 0 or len(values) >= 2

    if has_contradiction:
        level = Confidence.LOW
    elif supports >= 2 and len(values) <= 1:
        level = Confidence.HIGH
    else:
        level = Confidence.MEDIUM

    reason = (
        f"근거 {len(ec.evidence)}건, 상이값 {len(values)}개, "
        f"supports {supports}건, contradicts {contradicts}건"
    )
    return ClaimConfidence(
        claim_key=claim_key(ec.subject, ec.predicate),
        assessment=ConfidenceAssessment(level=level, reason=reason),
    )


def _representative_value(ec: ExtractedClaim) -> str | None:
    """대표 Claim.value — 최다 supports 값; 동률/부재 시 정규화 사전순 첫 값 (domain-entities §3)."""
    vals = [e.extracted_value for e in ec.evidence
            if e.extracted_value is not None and e.extracted_value.strip()]
    if not vals:
        return None
    support_counts: Counter[str] = Counter(
        e.extracted_value for e in ec.evidence
        if e.relation == EvidenceRelation.SUPPORTS and e.extracted_value and e.extracted_value.strip()
    )
    if support_counts:
        # 최다 supports → 동률 시 정규화 사전순
        return min(support_counts, key=lambda v: (-support_counts[v], normalize_value(v)))
    return min(vals, key=normalize_value)


def enrich_feature_knowledge(
    fk_shell: FeatureKnowledge, assets: list[Asset], llm: LLMService
) -> tuple[FeatureKnowledge, list[Warning]]:
    """지식 셸을 Claim·Evidence·Confidence·Conflict 로 완본화한다 (BR-PIPE-001, Q5=A)."""
    feature = fk_shell.feature
    claims_ex, warnings = extract_claims(feature, assets, llm)

    confidence = [assign_confidence(ec) for ec in claims_ex]
    conflicts = detect_conflicts(claims_ex, feature.id)

    claims: list[Claim] = []
    evidence = []
    for ec in claims_ex:
        rep = _representative_value(ec)
        if rep is not None:
            claims.append(Claim(
                subject=ec.subject, predicate=ec.predicate,
                value=rep, feature_id=feature.id,
            ))
        evidence.extend(ec.evidence)

    fk = fk_shell.model_copy(update={
        "claims": claims,
        "evidence": evidence,
        "confidence": confidence,
        "conflicts": conflicts,
        "meta": {**fk_shell.meta, "stage": "complete", "conflicts": len(conflicts)},
    })
    return fk, warnings


__all__ = ["extract_claims", "assign_confidence", "enrich_feature_knowledge"]

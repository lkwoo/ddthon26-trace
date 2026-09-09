"""충돌 검출 & 유형 분류 (UOW-03, C5, NFR Design P3/P4, BR-CONFLICT/DET).

detect_conflicts / classify_conflict_type 는 **순수 함수**(네트워크·모델 없음) —
동일 입력 → 동일 출력. PBT-03-A~C 의 대상이자 TRACE 결정적 검출의 핵심.
"""

from __future__ import annotations

from trace.models.domain import (
    Conflict,
    ConflictType,
    ConflictValue,
    EvidenceType,
    claim_key,
    normalize_value,
)
from trace.models.extraction import ExtractedClaim

# 부재/없음을 뜻하는 정규화 토큰 (BR-CONFLICT-003, 국소화 — 확장 용이)
ABSENCE_TOKENS: frozenset[str] = frozenset(
    {"absent", "none", "missing", "n/a", "null", "없음", "부재"}
)

# 검증·규칙·행위 서술 계열 (stale_knowledge 판정용, 부분 일치)
_BEHAVIORAL_TOKENS: frozenset[str] = frozenset(
    {
        "validated", "validate", "rejected", "reject", "enforced", "enforce",
        "required", "allowed", "disallowed", "supported", "검증", "거부", "허용", "차단",
    }
)

# 문서 계열 vs 구현 계열 (stale_knowledge: 문서와 코드/스키마가 상충)
_DOC_TYPES: frozenset[EvidenceType] = frozenset(
    {EvidenceType.PDF, EvidenceType.MARKDOWN, EvidenceType.TEXT}
)
_CODE_TYPES: frozenset[EvidenceType] = frozenset(
    {EvidenceType.SOURCE, EvidenceType.OPENAPI, EvidenceType.SQL, EvidenceType.CONFIG, EvidenceType.TEST}
)


def _distinct_values(ec: ExtractedClaim) -> list[tuple[str, str, str]]:
    """정규화 기준 서로 다른 값을 (value, source, location)로 수집 (첫 관측 대표).

    결정성: (normalize_value, source) 정렬 후 정규화값별 첫 항목만 유지.
    """
    rows = [
        (e.extracted_value, e.source, e.location)
        for e in ec.evidence
        if e.extracted_value is not None and e.extracted_value.strip()
    ]
    rows.sort(key=lambda r: (normalize_value(r[0]), r[1], r[2]))
    seen: set[str] = set()
    out: list[tuple[str, str, str]] = []
    for value, source, location in rows:
        norm = normalize_value(value)
        if norm in seen:
            continue
        seen.add(norm)
        out.append((value, source, location))
    return out


def _looks_behavioral(predicate: str, norm_values: set[str]) -> bool:
    """predicate/값이 검증·규칙·행위 서술 계열인지 (부분 일치)."""
    hay = predicate.lower()
    if any(tok in hay for tok in _BEHAVIORAL_TOKENS):
        return True
    return any(tok in nv for nv in norm_values for tok in _BEHAVIORAL_TOKENS)


def _has_doc_vs_code(ec: ExtractedClaim) -> bool:
    """evidence에 문서 계열과 코드/스키마 계열이 모두 있는지."""
    types = {e.type for e in ec.evidence}
    return bool(types & _DOC_TYPES) and bool(types & _CODE_TYPES)


def classify_conflict_type(
    ec: ExtractedClaim, vals: list[tuple[str, str, str]]
) -> ConflictType:
    """충돌 유형을 결정적 순서로 분류한다 (BR-CONFLICT-003, P4).

    전결정성(PBT-03-C): 임의 입력에도 예외 없이 유효 ConflictType 하나를 반환.
    모호/미매칭은 value_mismatch(P0 기본)로 폴백해 누락을 방지한다(BR-CONFLICT-005).
    """
    norm = {normalize_value(v) for v, _, _ in vals}
    # ① 부재 토큰이 있고 다른(요구) 값이 존재 → 정책 충돌
    if (norm & ABSENCE_TOKENS) and (norm - ABSENCE_TOKENS):
        return ConflictType.POLICY_CONFLICT
    # ② 행위 서술이며 문서와 코드가 상충 → 오래된 지식(드리프트)
    if _looks_behavioral(ec.predicate, norm) and _has_doc_vs_code(ec):
        return ConflictType.STALE_KNOWLEDGE
    # ③ 그 외 구체 값 불일치 → value_mismatch (폴백)
    return ConflictType.VALUE_MISMATCH


def _render_interpretation(
    ec: ExtractedClaim, ctype: ConflictType, vals: list[tuple[str, str, str]]
) -> str:
    """사람이 읽는 한 줄 해석 (BR-CONFLICT-004). 원문 비노출 — 값·소스만."""
    key = claim_key(ec.subject, ec.predicate)
    pairs = ", ".join(f"{v}({src})" for v, src, _ in vals)
    label = {
        ConflictType.VALUE_MISMATCH: "값 불일치",
        ConflictType.STALE_KNOWLEDGE: "문서/지식이 구현과 어긋남",
        ConflictType.POLICY_CONFLICT: "요구와 구현 부재의 충돌",
    }[ctype]
    return f"[{label}] {key}: {pairs}"


def detect_conflicts(claims: list[ExtractedClaim], feature_id: str) -> list[Conflict]:
    """claim별 evidence 값 비교로 충돌을 결정적으로 검출한다 (BR-CONFLICT-001, P3).

    한 claim의 정규화 값이 2개 이상 다르면 Conflict 1건. claim_key 순 정렬(재현성).
    feature_id 는 로깅/추적 맥락용(현재 Conflict 모델에는 저장하지 않음).
    """
    conflicts: list[Conflict] = []
    for ec in claims:
        vals = _distinct_values(ec)
        if len(vals) < 2:
            continue  # 충돌 아님 (건전성: 값 ≤ 1)
        ctype = classify_conflict_type(ec, vals)
        conflicts.append(
            Conflict(
                type=ctype,
                claim=claim_key(ec.subject, ec.predicate),
                values=[ConflictValue(value=v, source=src, location=loc) for v, src, loc in vals],
                interpretation=_render_interpretation(ec, ctype, vals),
            )
        )
    # 완전 결정적 정렬: claim_key 동률 시 값 목록으로 tie-break (입력 순서 무관, PBT-03-B)
    conflicts.sort(key=lambda c: (c.claim, tuple((cv.value, cv.source, cv.location) for cv in c.values)))
    return conflicts


__all__ = ["ABSENCE_TOKENS", "classify_conflict_type", "detect_conflicts"]

"""C5 충돌 검출 — 결정적 구조 비교 (UOW-03).

한 claim_key(subject+predicate)의 evidence에서 정규화된 값이 2개 이상 다르면 Conflict.
LLM 판단이 아닌 구조적 비교 — TRACE의 RAG 대비 차별점의 코드적 입증(BR-CONFLICT-001).
"""

from trace.conflict.detect import (
    ABSENCE_TOKENS,
    classify_conflict_type,
    detect_conflicts,
)
from trace.conflict.summarize import summarize_conflicts

__all__ = [
    "ABSENCE_TOKENS",
    "classify_conflict_type",
    "detect_conflicts",
    "summarize_conflicts",
]

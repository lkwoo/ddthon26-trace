"""Feature id 안전화 (UOW-02, NFR Design P3, BR-IDF-004, PBT-02-A).

임의의 title/후보 id를 파일·URI 안전한 슬러그로 변환한다.
결과는 항상 비어있지 않고 `/ \ ..` 를 포함하지 않는다(Feature.id 검증 통과 보장).
"""

from __future__ import annotations

import re

_ALLOWED = re.compile(r"[^a-z0-9]+")
_FALLBACK = "feature"


def safe_feature_id(raw: str) -> str:
    """raw(title 또는 후보 id) → 안전한 케밥 슬러그.

    - 소문자화, 영숫자 외 문자는 '-' 로 축약, 양끝/연속 '-' 정리.
    - 결과가 비면 'feature' 로 폴백.
    """
    text = (raw or "").strip().lower()
    slug = _ALLOWED.sub("-", text).strip("-")
    slug = re.sub(r"-{2,}", "-", slug)
    if not slug:
        return _FALLBACK
    # 방어: 어떤 경우에도 경로/상위참조 토큰이 남지 않음 (_ALLOWED가 이미 제거)
    return slug


def dedupe_ids(ids: list[str]) -> list[str]:
    """중복 id에 -2, -3 … 접미사를 붙여 유일화(입력 순서 유지)."""
    seen: dict[str, int] = {}
    out: list[str] = []
    for i in ids:
        if i not in seen:
            seen[i] = 1
            out.append(i)
        else:
            seen[i] += 1
            out.append(f"{i}-{seen[i]}")
    return out


__all__ = ["safe_feature_id", "dedupe_ids"]

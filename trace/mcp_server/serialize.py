"""Result → dict 직렬화 (UOW-05, C1, NFR Design P3, NFR-05-UX-1).

핵심 우선 키 순서(summary→data→conflicts→impact→evidence→warnings→meta)로 재조립하고
None·빈 컬렉션은 생략한다. 도구는 이 dict를 반환해 사람이 읽는 summary를 앞머리로 노출한다.
"""

from __future__ import annotations

from trace.models.result import Result

# 핵심 우선 노출 순서 (NFR-MCP-UX-002)
_KEY_ORDER = ["summary", "data", "conflicts", "impact", "evidence", "warnings", "meta"]


def _is_empty(value: object) -> bool:
    return value is None or value == [] or value == {}


def serialize_result(result: Result) -> dict:
    """Result를 핵심 우선 순서의 JSON 직렬화 가능한 dict로 변환한다."""
    dumped = result.model_dump(exclude_none=True)
    ordered: dict = {}
    for key in _KEY_ORDER:
        if key in dumped and not _is_empty(dumped[key]):
            ordered[key] = dumped[key]
    # 혹시 모를 추가 키(스키마 확장 대비)는 뒤에 붙인다
    for key, value in dumped.items():
        if key not in ordered and not _is_empty(value):
            ordered[key] = value
    return ordered


__all__ = ["serialize_result"]

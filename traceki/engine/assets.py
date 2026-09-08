"""자산(Asset) 표현과 분류 규칙 (UOW-01, C2).

Asset은 스캔으로 발견된 하나의 분석 대상 파일이다. 분류(type)와 파싱 상태(parse_status)를
함께 담아 부분 실패를 추적한다(FR-ANALYSIS-003).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any

from traceki.config import ASSET_EXTENSIONS

# 확장자 → 자산 유형 역인덱스
_EXT_TO_TYPE: dict[str, str] = {}
for _type, _exts in ASSET_EXTENSIONS.items():
    for _e in _exts:
        _EXT_TO_TYPE[_e] = _type

# OpenAPI 판별을 위한 콘텐츠 마커
_OPENAPI_MARKERS = ("openapi:", '"openapi"', "swagger:", '"swagger"')


@dataclass
class Asset:
    """분석 대상 파일 하나."""

    path: str                  # 프로젝트 루트 기준 상대경로 (POSIX 정규화)
    abspath: str
    type: str                  # source/markdown/text/pdf/openapi/sql/config/test/unknown
    filename: str
    parse_status: str = "pending"  # pending | ok | error | skipped
    content: str = ""
    error: str = ""

    def summary_dict(self) -> dict[str, Any]:
        """scan_project 결과에 넣는 경량 요약(콘텐츠 제외)."""
        return {
            "path": self.path,
            "type": self.type,
            "filename": self.filename,
            "parse_status": self.parse_status,
        }


def is_test_path(relpath: str, filename: str) -> bool:
    """테스트 자산 판별 (경로/파일명 규칙)."""
    parts = PurePosixPath(relpath).parts
    if any(p in ("test", "tests", "__tests__") for p in parts):
        return True
    stem = filename.rsplit(".", 1)[0]
    return (
        filename.startswith("test_")
        or stem.endswith("_test")
        or stem.endswith("Test")
        or stem.endswith("Tests")
    )


def classify(relpath: str, filename: str, ext: str, content_sniff: str = "") -> str:
    """파일을 자산 유형으로 분류한다. content_sniff는 yaml/json의 OpenAPI 판별에 사용."""
    if is_test_path(relpath, filename):
        return "test"
    base_type = _EXT_TO_TYPE.get(ext.lower())
    if base_type == "openapi":
        # .yaml/.yml/.json 은 내용으로 OpenAPI vs 일반 config 구분
        low = content_sniff.lower()
        if any(m in low for m in _OPENAPI_MARKERS):
            return "openapi"
        return "config"
    return base_type or "unknown"


__all__ = ["Asset", "classify", "is_test_path"]

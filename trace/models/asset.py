"""자산 모델 (UOW-01, C2 스캐너).

Functional Design(domain-entities.md)의 계약을 Pydantic v2 모델로 구현한다.
AssetType 값은 EvidenceType(UOW-0F)과 동일 문자열로 맞춰 하위 단위(UOW-02+) 매핑을 단순화한다.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """자산 유형 (BR-CLASSIFY). EvidenceType과 값 정렬."""

    SOURCE = "source"
    OPENAPI = "openapi"
    SQL = "sql"
    CONFIG = "config"
    TEST = "test"
    MARKDOWN = "markdown"
    PDF = "pdf"
    TEXT = "text"


class ParseStatus(str, Enum):
    """파싱 결과 상태 (BR-PARSE/SIZE/FAIL)."""

    PARSED = "parsed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    FAILED = "failed"


class Asset(BaseModel):
    """스캔된 단일 자산.

    content 는 텍스트 추출 결과(eager, Q4=A). skipped/failed 이면 None.
    scan_project 의 Result.data 에는 content 를 넣지 않는다(Q5=A → to_meta 사용).
    """

    rel_path: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)
    asset_type: AssetType
    parse_status: ParseStatus
    size_bytes: int = 0
    content: str | None = None
    truncated: bool = False
    error: str | None = None

    def to_meta(self) -> dict:
        """Result.data.assets 용 메타 표현 (content 제외, Q5=A)."""
        return {
            "rel_path": self.rel_path,
            "filename": self.filename,
            "asset_type": self.asset_type.value,
            "parse_status": self.parse_status.value,
            "size_bytes": self.size_bytes,
            "truncated": self.truncated,
        }


__all__ = ["AssetType", "ParseStatus", "Asset"]

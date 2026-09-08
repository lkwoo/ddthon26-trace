"""콘텐츠 파서 (UOW-01, C2) — 자산 유형별 텍스트 추출.

부분 실패 허용(FR-ANALYSIS-003): 한 파일 파싱 실패는 예외를 밖으로 던지지 않고 (텍스트, 오류)
튜플로 반환해 호출자가 warning 처리하도록 한다. PDF는 P0(pypdf).
"""

from __future__ import annotations

from pathlib import Path

# 텍스트로 그대로 읽는 유형
_TEXT_TYPES = {"source", "markdown", "text", "sql", "config", "openapi", "test", "unknown"}
_MAX_BYTES = 2_000_000  # 개별 파일 상한(데모 규모 최적화, NFR-PERF-001)


def parse_pdf(path: Path) -> str:
    """PDF에서 텍스트 추출 (P0). pypdf 지연 임포트."""
    from pypdf import PdfReader  # 지연 임포트

    reader = PdfReader(str(path))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def parse_asset(path: Path, asset_type: str) -> tuple[str, str]:
    """(content, error)를 반환. 성공 시 error="". 예외를 삼켜 부분 실패를 지원한다."""
    try:
        if path.stat().st_size > _MAX_BYTES:
            return "", f"파일이 너무 큼(>{_MAX_BYTES} bytes), 건너뜀"
        if asset_type == "pdf":
            return parse_pdf(path), ""
        if asset_type in _TEXT_TYPES:
            return path.read_text(encoding="utf-8", errors="replace"), ""
        return "", f"지원하지 않는 자산 유형: {asset_type}"
    except Exception as exc:  # noqa: BLE001 — 부분 실패 허용(FR-ANALYSIS-003)
        return "", f"{type(exc).__name__}: {exc}"


__all__ = ["parse_asset", "parse_pdf"]

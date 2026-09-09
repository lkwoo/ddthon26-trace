"""자산 텍스트 추출 (UOW-01, BR-PARSE/SIZE, NFR Design P3/P4).

추출 '방법'은 확장자로 결정하고(파서 레지스트리), 자산의 '의미 유형'은 classifier 가 별도로 정한다.
- PDF: pypdf 페이지별 extract_text (일부 실패 시 partial)
- 그 외: UTF-8 → latin-1 폴백 텍스트 읽기
크기 상한(파일당) 초과 시 상한까지만 읽고 truncated + partial.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from trace.common.errors import sanitize_error
from trace.config.scan_settings import ScanSettings
from trace.models.asset import ParseStatus
from trace.models.result import Warning


@dataclass
class ParseResult:
    content: str | None
    status: ParseStatus
    truncated: bool = False
    error: str | None = None
    warnings: list[Warning] = field(default_factory=list)


def _normalize_newlines(text: str) -> str:
    """개행을 \\n 으로 정규화 (BR-PARSE-004, 결정성)."""
    return text.replace("\r\n", "\n").replace("\r", "\n")


def _parse_text(path: Path, size: int, settings: ScanSettings, rel_path: str) -> ParseResult:
    cap = settings.max_file_bytes
    truncated = size > cap
    try:
        with path.open("rb") as f:
            raw = f.read(cap if truncated else size)
    except OSError as exc:
        return ParseResult(
            content=None,
            status=ParseStatus.FAILED,
            error=sanitize_error(exc),
            warnings=[Warning(code="parse_failed", message="파일 읽기 실패", source=rel_path)],
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")
    content = _normalize_newlines(text)
    if truncated:
        return ParseResult(
            content=content,
            status=ParseStatus.PARTIAL,
            truncated=True,
            warnings=[Warning(code="file_truncated",
                              message=f"파일이 상한({cap}B)을 초과해 잘렸습니다.",
                              source=rel_path)],
        )
    return ParseResult(content=content, status=ParseStatus.PARSED)


def _parse_pdf(path: Path, size: int, settings: ScanSettings, rel_path: str) -> ParseResult:
    try:
        from pypdf import PdfReader
    except ImportError as exc:  # 런타임 의존성 누락 방어
        return ParseResult(
            content=None,
            status=ParseStatus.FAILED,
            error=sanitize_error(exc),
            warnings=[Warning(code="parse_failed", message="pypdf 미설치", source=rel_path)],
        )
    try:
        reader = PdfReader(str(path))
        pages = reader.pages
        chunks: list[str] = []
        failed_pages = 0
        for page in pages:
            try:
                chunks.append(page.extract_text() or "")
            except Exception:  # noqa: BLE001 — 페이지 단위 실패는 격리(부분 추출)
                failed_pages += 1
        content = _normalize_newlines("\n".join(chunks))
    except Exception as exc:  # noqa: BLE001 — 파일 단위 실패
        return ParseResult(
            content=None,
            status=ParseStatus.FAILED,
            error=sanitize_error(exc),
            warnings=[Warning(code="parse_failed", message="PDF 파싱 실패", source=rel_path)],
        )
    if failed_pages:
        return ParseResult(
            content=content,
            status=ParseStatus.PARTIAL,
            warnings=[Warning(code="parse_failed",
                              message=f"PDF 일부 페이지({failed_pages}) 추출 실패",
                              source=rel_path)],
        )
    return ParseResult(content=content, status=ParseStatus.PARSED)


# 확장자 → 파서 레지스트리 (P3). 미등록 확장자는 _parse_text 로 폴백.
_PARSERS = {".pdf": _parse_pdf}


def parse_asset(path: Path, size: int, settings: ScanSettings, rel_path: str) -> ParseResult:
    """확장자에 맞는 파서로 텍스트를 추출한다 (레지스트리 조회, 기본 텍스트)."""
    ext = path.suffix.lower()
    parser = _PARSERS.get(ext, _parse_text)
    return parser(path, size, settings, rel_path)


__all__ = ["ParseResult", "parse_asset"]

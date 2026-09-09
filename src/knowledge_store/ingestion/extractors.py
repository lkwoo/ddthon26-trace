"""Extractor registry + concrete extractors (pluggable — Application Design Q5).

Each extractor produces a typed :class:`ExtractionResult`. Unsupported formats
are reported as ``Status.UNSUPPORTED`` rather than raising (US-1.1). Heavy
parsers (PDF, xlsx) are optional; when their library is missing the extractor
returns ``Status.ERROR`` with a clear message instead of crashing ingestion.
"""

from __future__ import annotations

import csv
import io
import re
from pathlib import Path
from typing import Protocol, runtime_checkable

from knowledge_store.types import ExtractionResult, Status

_TAG_RE = re.compile(r"(?:^|\s)#([A-Za-z0-9_/-]+)")

_CODE_LANGS = {
    ".py": "python", ".js": "javascript", ".ts": "typescript", ".tsx": "tsx",
    ".jsx": "javascript", ".java": "java", ".go": "go", ".rs": "rust",
    ".c": "c", ".h": "c", ".cpp": "cpp", ".cc": "cpp", ".hpp": "cpp",
    ".rb": "ruby", ".php": "php", ".cs": "c_sharp", ".kt": "kotlin",
    ".swift": "swift", ".scala": "scala", ".sql": "sql",
}


@runtime_checkable
class Extractor(Protocol):
    def supports(self, path: Path) -> bool: ...
    def extract(self, path: Path) -> ExtractionResult: ...


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _find_tags(text: str) -> tuple[str, ...]:
    return tuple(sorted(set(_TAG_RE.findall(text))))


class MarkdownExtractor:
    """Markdown / plain text (+ inline #tags and wikilinks preserved in text)."""

    _EXTS = {".md", ".markdown", ".txt", ".rst"}

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self._EXTS

    def extract(self, path: Path) -> ExtractionResult:
        text = _read_text(path)
        return ExtractionResult(
            status=Status.OK, source_path=str(path), format="markdown",
            text=text, tags=_find_tags(text),
        )


class CodeExtractor:
    """Multi-language source. Detailed graph extraction is done by U4; here we
    return raw source + detected language (FR-2.1 uses this downstream)."""

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in _CODE_LANGS

    def extract(self, path: Path) -> ExtractionResult:
        text = _read_text(path)
        return ExtractionResult(
            status=Status.OK, source_path=str(path), format="code",
            text=text, is_code=True, language=_CODE_LANGS[path.suffix.lower()],
            tags=_find_tags(text),
        )


class XmlExtractor:
    """XML / markup — raw text (tags preserved so element names and content stay
    searchable). Structured XML parsing is out of scope; content is chunked as
    prose downstream, matching how other text formats are handled."""

    _EXTS = {".xml"}

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in self._EXTS

    def extract(self, path: Path) -> ExtractionResult:
        text = _read_text(path)
        return ExtractionResult(
            status=Status.OK, source_path=str(path), format="xml",
            text=text, tags=_find_tags(text),
        )


class SpreadsheetExtractor:
    """csv (stdlib) and xlsx (openpyxl, optional) — extracts table cell data."""

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() in {".csv", ".xlsx"}

    def extract(self, path: Path) -> ExtractionResult:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            rows = list(csv.reader(io.StringIO(_read_text(path))))
            return ExtractionResult(
                status=Status.OK, source_path=str(path), format="csv",
                tables=[rows], text=_rows_preview(rows),
            )
        # xlsx
        try:
            from openpyxl import load_workbook  # type: ignore
        except Exception:
            return ExtractionResult(
                status=Status.ERROR, source_path=str(path), format="xlsx",
                message="openpyxl not installed; install extra 'docs' to parse xlsx",
            )
        wb = load_workbook(filename=str(path), read_only=True, data_only=True)
        tables: list[list[list[str]]] = []
        for ws in wb.worksheets:
            rows = [["" if c is None else str(c) for c in row]
                    for row in ws.iter_rows(values_only=True)]
            if rows:
                tables.append(rows)
        return ExtractionResult(
            status=Status.OK, source_path=str(path), format="xlsx",
            tables=tables, text="\n\n".join(_rows_preview(t) for t in tables),
        )


class PdfExtractor:
    """PDF text + tables (pypdf, optional)."""

    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"

    def extract(self, path: Path) -> ExtractionResult:
        try:
            from pypdf import PdfReader  # type: ignore
        except Exception:
            return ExtractionResult(
                status=Status.ERROR, source_path=str(path), format="pdf",
                message="pypdf not installed; install extra 'docs' to parse PDF",
            )
        reader = PdfReader(str(path))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)
        return ExtractionResult(
            status=Status.OK, source_path=str(path), format="pdf",
            text=text, tags=_find_tags(text),
        )


def _rows_preview(rows: list[list[str]], limit: int = 20) -> str:
    return "\n".join(" | ".join(r) for r in rows[:limit])


class ExtractorRegistry:
    """Resolves a file to the first registered extractor that supports it."""

    def __init__(self, extractors: list[Extractor] | None = None) -> None:
        self._extractors: list[Extractor] = list(extractors) if extractors else []

    def register(self, extractor: Extractor) -> None:
        self._extractors.append(extractor)

    def resolve(self, path: Path) -> Extractor | None:
        for ex in self._extractors:
            if ex.supports(path):
                return ex
        return None

    def extract(self, path: str | Path) -> ExtractionResult:
        p = Path(path)
        extractor = self.resolve(p)
        if extractor is None:
            return ExtractionResult(
                status=Status.UNSUPPORTED, source_path=str(p),
                format=p.suffix.lstrip("."),
                message=f"unsupported format: {p.suffix or '(none)'}",
            )
        return extractor.extract(p)


def default_registry() -> ExtractorRegistry:
    """Registry with all built-in extractors (order = resolution priority)."""
    return ExtractorRegistry([
        MarkdownExtractor(),
        CodeExtractor(),
        XmlExtractor(),
        SpreadsheetExtractor(),
        PdfExtractor(),
    ])

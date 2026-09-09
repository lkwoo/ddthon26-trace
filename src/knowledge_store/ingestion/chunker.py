"""Chunker — deterministic semantic-unit chunking with round-trip serialization.

Splits an :class:`ExtractionResult` into chunks at semantic boundaries
(markdown headings/paragraphs, table rows-as-a-unit, code blank-line blocks).
Chunking is a pure function of its input, and ``deserialize(serialize(chunks))``
reproduces the exact chunk list (NFR-8.2 / PBT round-trip target, PBT-02).
"""

from __future__ import annotations

import json
import re
from dataclasses import replace

from knowledge_store.ingestion.symbols import SymbolSpanExtractor
from knowledge_store.ingestion.tagging import TagEnricher
from knowledge_store.types import Chunk, ExtractionResult

_HEADING_RE = re.compile(r"^#{1,6}\s")


def _code_role(source_path: str) -> str:
    """Classify a code file as ``test`` or ``code`` from its path (FR-C1.2)."""
    p = source_path.replace("\\", "/").lower()
    fname = p.rsplit("/", 1)[-1]
    if "/tests/" in p or "/test/" in p or fname.startswith("test_") or fname.endswith("_test.py"):
        return "test"
    return "code"


class Chunker:
    """Deterministic semantic-unit chunker.

    Code is chunked at **symbol boundaries** (whole function/class) with line and
    symbol metadata; prose/tables keep their blank-line/table strategies. When no
    symbols are detected (e.g. a non-Python file or a plain script) code falls back
    to the original blank-line block strategy so nothing is lost.
    """

    def __init__(self) -> None:
        self._symbols = SymbolSpanExtractor()
        self._enricher = TagEnricher()

    def chunk(self, extraction: ExtractionResult) -> list[Chunk]:
        """Produce semantic chunks with stable ids + source metadata.

        Tags are enriched from each chunk's own content (symbols, links, salient
        keywords, path/language facets) so the tag-match relationship reflects real
        relatedness, not just literal ``#hashtags``. Enrichment leaves the chunk id
        untouched (ids derive from path/ordinal/kind/text, never tags), so
        versioning and the serialize round-trip are unaffected.
        """
        if not extraction.ok:
            return []
        if extraction.tables:
            chunks = self._chunk_tables(extraction)
        elif extraction.is_code:
            chunks = self._chunk_code(extraction)
        else:
            chunks = self._chunk_text(extraction)
        return [replace(c, tags=self._enricher.enrich(c)) for c in chunks]

    # -- strategies --------------------------------------------------------
    def _chunk_text(self, ex: ExtractionResult) -> list[Chunk]:
        blocks = self._split_markdown(ex.text)
        return [
            Chunk.make(text=block, source_path=ex.source_path, ordinal=i,
                       kind="section" if _HEADING_RE.match(block) else "paragraph",
                       tags=ex.tags, metadata={"role": "doc"})
            for i, block in enumerate(blocks)
        ]

    def _chunk_code(self, ex: ExtractionResult) -> list[Chunk]:
        spans = self._symbols.spans(ex.text, ex.language)
        if not spans:
            return self._chunk_code_blocks(ex)

        lines = ex.text.split("\n")
        n = len(lines)
        role = _code_role(ex.source_path)
        chunks: list[Chunk] = []
        ordinal = 0

        def emit(text: str, symbol: str, symbol_kind: str, start: int, end: int) -> None:
            nonlocal ordinal
            if not text.strip():
                return
            chunks.append(Chunk.make(
                text=text, source_path=ex.source_path, ordinal=ordinal, kind="code",
                tags=ex.tags,
                metadata={"language": ex.language, "lang": ex.language,
                          "symbol": symbol, "symbol_kind": symbol_kind,
                          "start_line": start, "end_line": end, "role": role},
            ))
            ordinal += 1

        # Sweep the file in line order: symbol segments stay whole; any non-blank
        # region between/around symbols (imports, module docstring, top-level code)
        # becomes a "<module>" chunk so no content is dropped.
        cursor = 1  # 1-indexed next uncovered line
        for sp in sorted(spans, key=lambda s: s.start_line):
            if sp.start_line > cursor:
                gap_text = "\n".join(lines[cursor - 1:sp.start_line - 1])
                emit(gap_text, "<module>", "module", cursor, sp.start_line - 1)
            emit(sp.text, sp.name, sp.kind, sp.start_line, sp.end_line)
            cursor = sp.end_line + 1
        if cursor <= n:
            tail = "\n".join(lines[cursor - 1:n])
            emit(tail, "<module>", "module", cursor, n)
        return chunks

    def _chunk_code_blocks(self, ex: ExtractionResult) -> list[Chunk]:
        """Fallback: blank-line block chunking for code without detected symbols."""
        blocks = [b for b in re.split(r"\n\s*\n", ex.text) if b.strip()]
        if not blocks:
            blocks = [ex.text] if ex.text.strip() else []
        role = _code_role(ex.source_path)
        return [
            Chunk.make(text=block, source_path=ex.source_path, ordinal=i,
                       kind="code", tags=ex.tags,
                       metadata={"language": ex.language, "lang": ex.language, "role": role})
            for i, block in enumerate(blocks)
        ]

    def _chunk_tables(self, ex: ExtractionResult) -> list[Chunk]:
        chunks: list[Chunk] = []
        ordinal = 0
        for t_idx, table in enumerate(ex.tables):
            text = "\n".join(" | ".join(row) for row in table)
            chunks.append(Chunk.make(
                text=text, source_path=ex.source_path, ordinal=ordinal,
                kind="table", tags=ex.tags, metadata={"table_index": t_idx},
            ))
            ordinal += 1
        return chunks

    @staticmethod
    def _split_markdown(text: str) -> list[str]:
        """Split on blank lines, keeping headings attached to following block."""
        raw_blocks = re.split(r"\n\s*\n", text.strip())
        blocks = [b.strip() for b in raw_blocks if b.strip()]
        return blocks

    # -- serialization (round-trip invariant) ------------------------------
    def serialize(self, chunks: list[Chunk]) -> bytes:
        payload = [c.to_dict() for c in chunks]
        return json.dumps(payload, ensure_ascii=False, sort_keys=True).encode("utf-8")

    def deserialize(self, blob: bytes) -> list[Chunk]:
        payload = json.loads(blob.decode("utf-8"))
        return [Chunk.from_dict(d) for d in payload]

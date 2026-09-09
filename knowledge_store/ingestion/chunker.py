"""Chunker — deterministic semantic-unit chunking with round-trip serialization.

Splits an :class:`ExtractionResult` into chunks at semantic boundaries
(markdown headings/paragraphs, table rows-as-a-unit, code blank-line blocks).
Chunking is a pure function of its input, and ``deserialize(serialize(chunks))``
reproduces the exact chunk list (NFR-8.2 / PBT round-trip target, PBT-02).
"""

from __future__ import annotations

import json
import re

from knowledge_store.types import Chunk, ExtractionResult

_HEADING_RE = re.compile(r"^#{1,6}\s")


class Chunker:
    def chunk(self, extraction: ExtractionResult) -> list[Chunk]:
        """Produce semantic chunks with stable ids + source metadata."""
        if not extraction.ok:
            return []
        if extraction.tables:
            return self._chunk_tables(extraction)
        if extraction.is_code:
            return self._chunk_code(extraction)
        return self._chunk_text(extraction)

    # -- strategies --------------------------------------------------------
    def _chunk_text(self, ex: ExtractionResult) -> list[Chunk]:
        blocks = self._split_markdown(ex.text)
        return [
            Chunk.make(text=block, source_path=ex.source_path, ordinal=i,
                       kind="section" if _HEADING_RE.match(block) else "paragraph",
                       tags=ex.tags)
            for i, block in enumerate(blocks)
        ]

    def _chunk_code(self, ex: ExtractionResult) -> list[Chunk]:
        blocks = [b for b in re.split(r"\n\s*\n", ex.text) if b.strip()]
        if not blocks:
            blocks = [ex.text] if ex.text.strip() else []
        return [
            Chunk.make(text=block, source_path=ex.source_path, ordinal=i,
                       kind="code", tags=ex.tags,
                       metadata={"language": ex.language})
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

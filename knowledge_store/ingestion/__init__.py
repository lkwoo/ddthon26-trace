"""U3 — Ingestion & Chunking.

Pluggable extractor registry (Application Design Q5), deterministic semantic
chunking with serialize/deserialize round-trip invariance (NFR-8.2), and
chunk-level versioning via text-similarity/hash matching (Epic 4).
"""

from knowledge_store.ingestion.extractors import (
    CodeExtractor,
    Extractor,
    ExtractorRegistry,
    MarkdownExtractor,
    PdfExtractor,
    SpreadsheetExtractor,
    default_registry,
)
from knowledge_store.ingestion.chunker import Chunker
from knowledge_store.ingestion.versioner import ChunkVersioner

__all__ = [
    "Extractor",
    "ExtractorRegistry",
    "MarkdownExtractor",
    "PdfExtractor",
    "SpreadsheetExtractor",
    "CodeExtractor",
    "default_registry",
    "Chunker",
    "ChunkVersioner",
]

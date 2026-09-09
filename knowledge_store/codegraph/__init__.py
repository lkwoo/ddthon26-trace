"""U4 — Code Structure & Relationships.

Deterministic, LLM-free code-graph extraction (FR-2) and code<->chunk
relationship construction via three strategies (FR-3).
"""

from knowledge_store.codegraph.analyzer import CodeStructureAnalyzer, CodeUnit
from knowledge_store.codegraph.relationships import (
    EmbeddingSimilarityStrategy,
    MarkdownLinkStrategy,
    RelationStrategy,
    RelationshipBuilder,
    TagMatchStrategy,
)

__all__ = [
    "CodeStructureAnalyzer",
    "CodeUnit",
    "RelationStrategy",
    "RelationshipBuilder",
    "EmbeddingSimilarityStrategy",
    "MarkdownLinkStrategy",
    "TagMatchStrategy",
]

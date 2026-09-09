"""Shared typed result objects and enums (Application Design Q7).

Every unit depends on these contracts rather than on each other's internals.
All operations return typed result objects with an explicit ``status`` field
instead of raising for expected outcomes (e.g. unsupported formats, unresolved
symbols, broken links).
"""

from knowledge_store.types.results import (
    Chunk,
    ChunkVersion,
    Content,
    EdgeType,
    ExportResult,
    ExtractionResult,
    GraphEdge,
    GraphNode,
    GraphResult,
    IngestionReport,
    InstallReport,
    MatchResult,
    RelationType,
    Relationship,
    SearchHit,
    SnippetResult,
    Status,
    Summary,
    ToolResult,
    VersionResult,
)

__all__ = [
    "Status",
    "RelationType",
    "EdgeType",
    "Chunk",
    "ChunkVersion",
    "Content",
    "ExtractionResult",
    "GraphNode",
    "GraphEdge",
    "GraphResult",
    "Relationship",
    "MatchResult",
    "VersionResult",
    "SearchHit",
    "SnippetResult",
    "Summary",
    "ToolResult",
    "IngestionReport",
    "InstallReport",
    "ExportResult",
]

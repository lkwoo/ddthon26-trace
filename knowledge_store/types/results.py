"""Typed result objects and status enums shared across all units.

Design decisions applied: typed result objects with status fields (App Design
Q7). Dataclasses are used for clarity and cheap equality; ``to_dict`` methods
provide stable, JSON-serializable, token-efficient envelopes for the MCP layer
and the static wiki export.
"""

from __future__ import annotations

import enum
import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any, Optional


class Status(str, enum.Enum):
    """Explicit outcome for any operation (Q7 — no exceptions for expected cases)."""

    OK = "ok"
    UNSUPPORTED = "unsupported"      # e.g. unsupported file format (US-1.1)
    UNRESOLVED = "unresolved"        # e.g. unresolved symbol / broken link (US-2.2, US-3.2)
    NOT_FOUND = "not_found"
    SKIPPED = "skipped"
    ERROR = "error"


class RelationType(str, enum.Enum):
    """Code <-> chunk relationship provenance (Epic 3)."""

    EMBEDDING = "embedding"          # US-3.1 similarity
    MARKDOWN_LINK = "markdown_link"  # US-3.2 [[wikilink]] / links
    TAG = "tag"                      # US-3.3 tag match


class EdgeType(str, enum.Enum):
    """Code-graph edge kinds (FR-2.1)."""

    DEFINE = "define"
    CALL = "call"
    DEPEND = "depend"
    INHERIT = "inherit"
    CONTAIN = "contain"


def _stable_id(*parts: Any) -> str:
    """Deterministic short id from stable inputs (used for chunk identity)."""
    joined = "\x1f".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(joined.encode("utf-8")).hexdigest()[:16]


@dataclass(frozen=True)
class Chunk:
    """A semantic-unit chunk with stable identity and source metadata (FR-1.3).

    ``id`` is derived deterministically from source path, ordinal and text so
    that chunking is reproducible and serialization round-trips (NFR-8.2).
    """

    id: str
    text: str
    source_path: str
    ordinal: int
    kind: str = "paragraph"          # section | paragraph | table | code | sheet
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def make(text: str, source_path: str, ordinal: int, kind: str = "paragraph",
             tags: tuple[str, ...] = (), metadata: Optional[dict[str, Any]] = None) -> "Chunk":
        cid = _stable_id(source_path, ordinal, kind, text)
        return Chunk(
            id=cid,
            text=text,
            source_path=source_path,
            ordinal=ordinal,
            kind=kind,
            tags=tuple(tags),
            metadata=dict(metadata or {}),
        )

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["tags"] = list(self.tags)
        return d

    @staticmethod
    def from_dict(d: dict[str, Any]) -> "Chunk":
        return Chunk(
            id=d["id"],
            text=d["text"],
            source_path=d["source_path"],
            ordinal=int(d["ordinal"]),
            kind=d.get("kind", "paragraph"),
            tags=tuple(d.get("tags", ())),
            metadata=dict(d.get("metadata", {})),
        )


@dataclass
class ChunkVersion:
    """A versioned chunk row (Epic 4)."""

    chunk_id: str
    version: int
    text: str
    is_latest: bool = True


@dataclass
class ExtractionResult:
    """Output of an Extractor (Q7 typed result)."""

    status: Status
    source_path: str
    format: str = ""
    text: str = ""
    tables: list[list[list[str]]] = field(default_factory=list)  # list of tables (rows of cells)
    tags: tuple[str, ...] = ()
    is_code: bool = False
    language: str = ""
    message: str = ""

    @property
    def ok(self) -> bool:
        return self.status == Status.OK


@dataclass
class Content:
    """Content-to-summarize returned to the agent (US-5.1)."""

    ref_id: str
    text: str
    kind: str = "chunk"


@dataclass
class GraphNode:
    id: str
    name: str
    kind: str                        # file | function | class | module
    path: str = ""
    language: str = ""


@dataclass
class GraphEdge:
    src: str
    dst: str
    type: EdgeType
    resolved: bool = True


@dataclass
class GraphResult:
    status: Status
    nodes: list[GraphNode] = field(default_factory=list)
    edges: list[GraphEdge] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)  # references with no definition (US-2.2)


@dataclass
class Relationship:
    src_id: str
    dst_id: str
    type: RelationType
    score: float = 1.0
    resolved: bool = True            # False for broken markdown links (US-3.2)


@dataclass
class MatchResult:
    """Outcome of matching a new chunk against existing candidates (US-4.1)."""

    status: Status                   # OK = matched, NOT_FOUND = new chunk
    matched_chunk_id: Optional[str] = None
    similarity: float = 0.0


@dataclass
class VersionResult:
    """Outcome of applying versioning (US-4.2)."""

    chunk_id: str
    version: int
    is_new: bool


@dataclass
class SearchHit:
    ref_id: str
    kind: str                        # chunk | symbol
    score: float
    preview: str = ""


@dataclass
class SnippetResult:
    """Token-budget-aware smart snippet (US-6.3, NFR-1.2)."""

    status: Status
    text: str = ""
    estimated_tokens: int = 0
    token_budget: int = 0
    truncated: bool = False


@dataclass
class Summary:
    chunk_id: str
    text: str


@dataclass
class ToolResult:
    """Token-efficient envelope the MCP layer serializes to the agent (NFR-1.2)."""

    status: Status
    data: Any = None
    message: str = ""

    def to_json(self) -> str:
        payload = {"status": self.status.value, "data": _jsonable(self.data)}
        if self.message:
            payload["message"] = self.message
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


@dataclass
class IngestionReport:
    status: Status
    ingested_files: int = 0
    chunks_new: int = 0
    chunks_updated: int = 0
    unsupported: list[str] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)
    pending_summaries: list[str] = field(default_factory=list)
    message: str = ""


@dataclass
class InstallReport:
    status: Status
    target_dir: str
    store_dir: str = ""
    configured_clients: list[str] = field(default_factory=list)
    manual_snippet: str = ""
    message: str = ""


@dataclass
class ExportResult:
    status: Status
    export_dir: str
    files_written: list[str] = field(default_factory=list)
    message: str = ""


def _jsonable(value: Any) -> Any:
    """Best-effort conversion of typed results to JSON-serializable structures."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, enum.Enum):
        return value.value
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(v) for v in value]
    if hasattr(value, "to_dict"):
        return _jsonable(value.to_dict())
    if hasattr(value, "__dataclass_fields__"):
        return _jsonable(asdict(value))
    return str(value)

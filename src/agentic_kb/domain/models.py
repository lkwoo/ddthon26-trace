"""Immutable domain models for the Engine Core (U1).

All models are frozen dataclasses with a deterministic serialization contract
(`to_dict` / `from_dict`) that satisfies the round-trip property
``from_dict(to_dict(x)) == x`` for all valid instances (PBT-02).

Design rules honored here:
- BR-4  paths are project-root-relative, POSIX-normalized.
- BR-6  collections are stored in a stable, sorted order for deterministic output.
- BR-7  engine artifacts carry no timestamps; only AgentNote/SyncReport are time-bearing.
- BR-25 deserializing an unknown enum value raises ValueError.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from typing import Literal

SymbolKind = Literal["file", "function", "class", "method"]
EdgeKind = Literal["call", "dependency", "import"]
DocKind = Literal["docstring", "comment", "heading"]
TreeKind = Literal["dir", "file", "module"]
ResultKind = Literal["keyword", "graph"]
MatchedOn = Literal["name", "signature", "doc", "body", "edge"]

_SYMBOL_KINDS = ("file", "function", "class", "method")
_EDGE_KINDS = ("call", "dependency", "import")
_DOC_KINDS = ("docstring", "comment", "heading")
_TREE_KINDS = ("dir", "file", "module")
_RESULT_KINDS = ("keyword", "graph")
_MATCHED_ON = ("name", "signature", "doc", "body", "edge")


def _require(value: str, allowed: tuple[str, ...], field_name: str) -> str:
    """Validate an enum-like string field (BR-25)."""
    if value not in allowed:
        raise ValueError(f"invalid {field_name}: {value!r} (allowed: {allowed})")
    return value


def content_sha(content: str) -> str:
    """Deterministic SHA-256 hex of file content (BR-6, US-N7 skip cache)."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# --------------------------------------------------------------------------- #
# Span
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Span:
    start_line: int
    start_col: int
    end_line: int
    end_col: int

    def __post_init__(self) -> None:
        if self.start_line < 1 or self.end_line < self.start_line:
            raise ValueError("Span line range invalid")
        if (self.end_line, self.end_col) < (self.start_line, self.start_col):
            raise ValueError("Span end precedes start")

    def to_dict(self) -> dict:
        return {
            "start_line": self.start_line,
            "start_col": self.start_col,
            "end_line": self.end_line,
            "end_col": self.end_col,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Span":
        return cls(
            start_line=d["start_line"],
            start_col=d["start_col"],
            end_line=d["end_line"],
            end_col=d["end_col"],
        )


# --------------------------------------------------------------------------- #
# SourceFile
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class SourceFile:
    path: str
    language: str
    content: str
    sha: str = ""

    def __post_init__(self) -> None:
        if self.path.startswith("/") or ".." in self.path.split("/"):
            raise ValueError(f"path must be relative and confined: {self.path!r}")
        if not self.sha:
            object.__setattr__(self, "sha", content_sha(self.content))

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "language": self.language,
            "content": self.content,
            "sha": self.sha,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SourceFile":
        return cls(
            path=d["path"],
            language=d["language"],
            content=d["content"],
            sha=d.get("sha", ""),
        )


# --------------------------------------------------------------------------- #
# Symbol
# --------------------------------------------------------------------------- #
def make_symbol_id(path: str, kind: str, qualified_name: str) -> str:
    """Deterministic, human-readable symbol id (Q1=A, BR-6)."""
    return f"{path}::{kind}::{qualified_name}"


@dataclass(frozen=True)
class Symbol:
    id: str
    kind: SymbolKind
    name: str
    qualified_name: str
    location: Span

    def __post_init__(self) -> None:
        _require(self.kind, _SYMBOL_KINDS, "Symbol.kind")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "kind": self.kind,
            "name": self.name,
            "qualified_name": self.qualified_name,
            "location": self.location.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Symbol":
        return cls(
            id=d["id"],
            kind=_require(d["kind"], _SYMBOL_KINDS, "Symbol.kind"),
            name=d["name"],
            qualified_name=d["qualified_name"],
            location=Span.from_dict(d["location"]),
        )


# --------------------------------------------------------------------------- #
# Reference
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Reference:
    src_symbol: str
    dst_name: str
    kind: EdgeKind
    location: Span

    def __post_init__(self) -> None:
        _require(self.kind, _EDGE_KINDS, "Reference.kind")

    def to_dict(self) -> dict:
        return {
            "src_symbol": self.src_symbol,
            "dst_name": self.dst_name,
            "kind": self.kind,
            "location": self.location.to_dict(),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Reference":
        return cls(
            src_symbol=d["src_symbol"],
            dst_name=d["dst_name"],
            kind=_require(d["kind"], _EDGE_KINDS, "Reference.kind"),
            location=Span.from_dict(d["location"]),
        )


# --------------------------------------------------------------------------- #
# DocElement
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DocElement:
    kind: DocKind
    text: str
    location: Span
    level: int | None = None

    def __post_init__(self) -> None:
        _require(self.kind, _DOC_KINDS, "DocElement.kind")
        if self.kind == "heading" and self.level is None:
            raise ValueError("heading DocElement requires a level")

    def to_dict(self) -> dict:
        return {
            "kind": self.kind,
            "text": self.text,
            "location": self.location.to_dict(),
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DocElement":
        return cls(
            kind=_require(d["kind"], _DOC_KINDS, "DocElement.kind"),
            text=d["text"],
            location=Span.from_dict(d["location"]),
            level=d.get("level"),
        )


# --------------------------------------------------------------------------- #
# ParsedUnit
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ParsedUnit:
    file: SourceFile
    symbols: tuple[Symbol, ...] = ()
    references: tuple[Reference, ...] = ()
    doc_elements: tuple[DocElement, ...] = ()

    def to_dict(self) -> dict:
        return {
            "file": self.file.to_dict(),
            "symbols": [s.to_dict() for s in self.symbols],
            "references": [r.to_dict() for r in self.references],
            "doc_elements": [e.to_dict() for e in self.doc_elements],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ParsedUnit":
        return cls(
            file=SourceFile.from_dict(d["file"]),
            symbols=tuple(Symbol.from_dict(x) for x in d.get("symbols", [])),
            references=tuple(Reference.from_dict(x) for x in d.get("references", [])),
            doc_elements=tuple(DocElement.from_dict(x) for x in d.get("doc_elements", [])),
        )


# --------------------------------------------------------------------------- #
# Edge / RelationshipGraph
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Edge:
    src: str
    dst: str
    kind: EdgeKind

    def __post_init__(self) -> None:
        _require(self.kind, _EDGE_KINDS, "Edge.kind")

    def to_dict(self) -> dict:
        return {"src": self.src, "dst": self.dst, "kind": self.kind}

    @classmethod
    def from_dict(cls, d: dict) -> "Edge":
        return cls(
            src=d["src"],
            dst=d["dst"],
            kind=_require(d["kind"], _EDGE_KINDS, "Edge.kind"),
        )


@dataclass(frozen=True)
class RelationshipGraph:
    nodes: tuple[Symbol, ...] = ()
    edges: tuple[Edge, ...] = ()

    def __post_init__(self) -> None:
        node_ids = {n.id for n in self.nodes}
        for e in self.edges:
            if e.src not in node_ids or e.dst not in node_ids:
                raise ValueError(f"edge endpoint not in nodes: {e}")  # BR-26

    def to_dict(self) -> dict:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "RelationshipGraph":
        return cls(
            nodes=tuple(Symbol.from_dict(x) for x in d.get("nodes", [])),
            edges=tuple(Edge.from_dict(x) for x in d.get("edges", [])),
        )


# --------------------------------------------------------------------------- #
# TreeNode / StructureTree
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class TreeNode:
    path: str
    kind: TreeKind
    name: str
    children: tuple["TreeNode", ...] = ()

    def __post_init__(self) -> None:
        _require(self.kind, _TREE_KINDS, "TreeNode.kind")

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "kind": self.kind,
            "name": self.name,
            "children": [c.to_dict() for c in self.children],
        }

    @classmethod
    def from_dict(cls, d: dict) -> "TreeNode":
        return cls(
            path=d["path"],
            kind=_require(d["kind"], _TREE_KINDS, "TreeNode.kind"),
            name=d["name"],
            children=tuple(TreeNode.from_dict(c) for c in d.get("children", [])),
        )


@dataclass(frozen=True)
class StructureTree:
    root: TreeNode

    def to_dict(self) -> dict:
        return {"root": self.root.to_dict()}

    @classmethod
    def from_dict(cls, d: dict) -> "StructureTree":
        return cls(root=TreeNode.from_dict(d["root"]))


# --------------------------------------------------------------------------- #
# ModuleSummary
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ModuleSummary:
    target: str
    signatures: tuple[str, ...] = ()
    docstrings: tuple[str, ...] = ()
    headings: tuple[str, ...] = ()
    comments: tuple[str, ...] = ()

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "signatures": list(self.signatures),
            "docstrings": list(self.docstrings),
            "headings": list(self.headings),
            "comments": list(self.comments),
        }

    @classmethod
    def from_dict(cls, d: dict) -> "ModuleSummary":
        return cls(
            target=d["target"],
            signatures=tuple(d.get("signatures", [])),
            docstrings=tuple(d.get("docstrings", [])),
            headings=tuple(d.get("headings", [])),
            comments=tuple(d.get("comments", [])),
        )


# --------------------------------------------------------------------------- #
# AgentNote / MergedSummary
# --------------------------------------------------------------------------- #
def make_note_id(target: str, created_at: str, author: str) -> str:
    return f"{target}::note::{created_at}::{author}"


@dataclass(frozen=True)
class AgentNote:
    target: str
    body_md: str
    author: str
    created_at: str
    note_id: str = ""

    def __post_init__(self) -> None:
        if not self.note_id:
            object.__setattr__(
                self, "note_id", make_note_id(self.target, self.created_at, self.author)
            )

    def to_dict(self) -> dict:
        return {
            "note_id": self.note_id,
            "target": self.target,
            "body_md": self.body_md,
            "author": self.author,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "AgentNote":
        return cls(
            target=d["target"],
            body_md=d["body_md"],
            author=d["author"],
            created_at=d["created_at"],
            note_id=d.get("note_id", ""),
        )


@dataclass(frozen=True)
class MergedSummary:
    target: str
    engine: ModuleSummary | None = None
    agent_notes: tuple[AgentNote, ...] = ()
    engine_first: bool = True

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "engine": self.engine.to_dict() if self.engine else None,
            "agent_notes": [n.to_dict() for n in self.agent_notes],
            "engine_first": self.engine_first,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "MergedSummary":
        engine = d.get("engine")
        return cls(
            target=d["target"],
            engine=ModuleSummary.from_dict(engine) if engine else None,
            agent_notes=tuple(AgentNote.from_dict(n) for n in d.get("agent_notes", [])),
            engine_first=d.get("engine_first", True),
        )


# --------------------------------------------------------------------------- #
# Snippet / SearchResult / SyncReport
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Snippet:
    text: str
    estimated_tokens: int
    truncated: bool = False

    def to_dict(self) -> dict:
        return {
            "text": self.text,
            "estimated_tokens": self.estimated_tokens,
            "truncated": self.truncated,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "Snippet":
        return cls(
            text=d["text"],
            estimated_tokens=d["estimated_tokens"],
            truncated=d.get("truncated", False),
        )


@dataclass(frozen=True)
class SearchResult:
    target: str
    score: float
    kind: ResultKind
    matched_on: MatchedOn

    def __post_init__(self) -> None:
        _require(self.kind, _RESULT_KINDS, "SearchResult.kind")
        _require(self.matched_on, _MATCHED_ON, "SearchResult.matched_on")

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "score": self.score,
            "kind": self.kind,
            "matched_on": self.matched_on,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SearchResult":
        return cls(
            target=d["target"],
            score=d["score"],
            kind=_require(d["kind"], _RESULT_KINDS, "SearchResult.kind"),
            matched_on=_require(d["matched_on"], _MATCHED_ON, "SearchResult.matched_on"),
        )


@dataclass(frozen=True)
class SyncReport:
    files_total: int = 0
    symbols_total: int = 0
    skipped: tuple[str, ...] = ()
    failures: tuple[str, ...] = ()
    duration_ms: int = 0

    def to_dict(self) -> dict:
        return {
            "files_total": self.files_total,
            "symbols_total": self.symbols_total,
            "skipped": list(self.skipped),
            "failures": list(self.failures),
            "duration_ms": self.duration_ms,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "SyncReport":
        return cls(
            files_total=d.get("files_total", 0),
            symbols_total=d.get("symbols_total", 0),
            skipped=tuple(d.get("skipped", [])),
            failures=tuple(d.get("failures", [])),
            duration_ms=d.get("duration_ms", 0),
        )

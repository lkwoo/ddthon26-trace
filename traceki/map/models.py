"""C10 온보딩 맵 도메인 모델 (UOW-07).

관계 그래프·진입점·Feature 매핑을 순수 데이터로 표현한다. `Evidence`(traceki.models)는
관계 근거로 **그대로 재사용**한다(FR-MAP-007). 모든 모델은 `to_dict`/`from_dict`로 왕복
가능해야 한다(overview.md 영속화 round-trip, PBT P3).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from traceki.models import Evidence


@dataclass
class EntryPoint:
    """프로젝트에 들어가는 실행/요청 진입점 (US-07.2)."""

    kind: str          # rest_endpoint | main | cli | route | test_entry ...
    symbol: str        # 메서드/함수/클래스 식별자
    file: str          # 프로젝트 상대경로
    reason: str = ""   # 왜 진입점으로 판단했는지(근거 단서)

    def to_dict(self) -> dict[str, Any]:
        return {"kind": self.kind, "symbol": self.symbol, "file": self.file, "reason": self.reason}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "EntryPoint":
        return cls(
            kind=str(d.get("kind", "")),
            symbol=str(d.get("symbol", "")),
            file=str(d.get("file", "")),
            reason=str(d.get("reason", "")),
        )


@dataclass
class FileNode:
    """관계 그래프의 노드(파일 하나)."""

    path: str
    module: str = ""
    type: str = "code"   # code | api | db | config | test

    def to_dict(self) -> dict[str, Any]:
        return {"path": self.path, "module": self.module, "type": self.type}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FileNode":
        return cls(path=str(d.get("path", "")), module=str(d.get("module", "")), type=str(d.get("type", "code")))


@dataclass
class DependencyEdge:
    """파일→모듈/파일 의존(import) 엣지."""

    src: str
    dst: str
    kind: str = "import"
    evidence: Evidence | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "src": self.src,
            "dst": self.dst,
            "kind": self.kind,
            "evidence": self.evidence.to_dict() if self.evidence else None,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "DependencyEdge":
        ev = d.get("evidence")
        return cls(
            src=str(d.get("src", "")),
            dst=str(d.get("dst", "")),
            kind=str(d.get("kind", "import")),
            evidence=Evidence.from_dict(ev) if isinstance(ev, dict) else None,
        )


@dataclass
class CallEdge:
    """함수/메서드 호출 관계 엣지 (US-07.4)."""

    caller: str
    callee: str
    file: str = ""
    evidence: Evidence | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "caller": self.caller,
            "callee": self.callee,
            "file": self.file,
            "evidence": self.evidence.to_dict() if self.evidence else None,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "CallEdge":
        ev = d.get("evidence")
        return cls(
            caller=str(d.get("caller", "")),
            callee=str(d.get("callee", "")),
            file=str(d.get("file", "")),
            evidence=Evidence.from_dict(ev) if isinstance(ev, dict) else None,
        )


@dataclass
class FeatureFileMap:
    """Feature → 관련 파일 매핑 (US-07.3, C4 지식 재사용)."""

    feature_id: str
    title: str
    files: list[dict] = field(default_factory=list)  # [{path, category}]

    def to_dict(self) -> dict[str, Any]:
        return {"feature_id": self.feature_id, "title": self.title, "files": list(self.files)}

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "FeatureFileMap":
        return cls(
            feature_id=str(d.get("feature_id", "")),
            title=str(d.get("title", "")),
            files=[dict(f) for f in d.get("files", []) if isinstance(f, dict)],
        )


@dataclass
class RelationGraph:
    """정적 추출로 얻은 파일·의존·호출 관계."""

    nodes: list[FileNode] = field(default_factory=list)
    dep_edges: list[DependencyEdge] = field(default_factory=list)
    call_edges: list[CallEdge] = field(default_factory=list)
    unresolved: list[str] = field(default_factory=list)  # 정적 파싱 불가 → LLM 폴백 위임

    def to_dict(self) -> dict[str, Any]:
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "dep_edges": [e.to_dict() for e in self.dep_edges],
            "call_edges": [e.to_dict() for e in self.call_edges],
            "unresolved": list(self.unresolved),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "RelationGraph":
        return cls(
            nodes=[FileNode.from_dict(n) for n in d.get("nodes", [])],
            dep_edges=[DependencyEdge.from_dict(e) for e in d.get("dep_edges", [])],
            call_edges=[CallEdge.from_dict(e) for e in d.get("call_edges", [])],
            unresolved=[str(u) for u in d.get("unresolved", [])],
        )


@dataclass
class OnboardingMap:
    """온보딩 맵 산출물의 단일 진실원. overview.md로 영속화된다."""

    entry_points: list[EntryPoint] = field(default_factory=list)
    file_graph: RelationGraph = field(default_factory=RelationGraph)
    feature_file_maps: list[FeatureFileMap] = field(default_factory=list)
    call_relations: list[dict] = field(default_factory=list)  # key_flow 정규화 단계
    narrative: str = ""
    mermaid: dict = field(default_factory=dict)  # {dependency, sequence}
    evidence: list[Evidence] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_points": [e.to_dict() for e in self.entry_points],
            "file_graph": self.file_graph.to_dict(),
            "feature_file_maps": [m.to_dict() for m in self.feature_file_maps],
            "call_relations": list(self.call_relations),
            "narrative": self.narrative,
            "mermaid": dict(self.mermaid),
            "evidence": [e.to_dict() for e in self.evidence],
            "warnings": list(self.warnings),
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> "OnboardingMap":
        return cls(
            entry_points=[EntryPoint.from_dict(e) for e in d.get("entry_points", [])],
            file_graph=RelationGraph.from_dict(d.get("file_graph", {}) or {}),
            feature_file_maps=[FeatureFileMap.from_dict(m) for m in d.get("feature_file_maps", [])],
            call_relations=[dict(c) for c in d.get("call_relations", []) if isinstance(c, dict)],
            narrative=str(d.get("narrative", "")),
            mermaid=dict(d.get("mermaid", {}) or {}),
            evidence=[Evidence.from_dict(e) for e in d.get("evidence", []) if isinstance(e, dict)],
            warnings=[str(w) for w in d.get("warnings", [])],
        )


__all__ = [
    "EntryPoint",
    "FileNode",
    "DependencyEdge",
    "CallEdge",
    "FeatureFileMap",
    "RelationGraph",
    "OnboardingMap",
]

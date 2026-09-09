"""정적 관계 추출 — Python `ast` · Java 정규식 휴리스틱 (UOW-07, FR-MAP-004).

정적 뼈대(엣지)가 관계의 **사실**이고, LLM은 서술·근거만 얹는다(하이브리드 병합, 규칙 1).
개별 파일 파싱이 실패해도 전체를 중단하지 않고 `RelationGraph.unresolved`에 적재한 뒤 LLM
폴백에 위임한다(부분 실패 허용, 규칙 4 / PBT P2 무크래시).
"""

from __future__ import annotations

import ast
import re
from typing import TYPE_CHECKING

from traceki.common import get_logger
from traceki.models import Evidence, EvidenceRelation
from traceki.map.models import (
    CallEdge,
    DependencyEdge,
    EntryPoint,
    FeatureFileMap,
    FileNode,
    RelationGraph,
)

if TYPE_CHECKING:
    from traceki.engine.assets import Asset
    from traceki.knowledge import KnowledgeStore

_log = get_logger("trace.map.relations")

# asset.type → 그래프 노드 type
_NODE_TYPE = {
    "source": "code",
    "test": "test",
    "openapi": "api",
    "sql": "db",
    "config": "config",
    "markdown": "config",
    "text": "config",
    "pdf": "config",
}

_JAVA_IMPORT = re.compile(r"^\s*import\s+(?:static\s+)?([\w.]+)\s*;", re.M)
_JAVA_MAIN = re.compile(r"public\s+static\s+void\s+main\s*\(")
_JAVA_MAPPING = re.compile(r"@(Get|Post|Put|Delete|Patch|Request)Mapping\s*(?:\(([^)]*)\))?")
_JAVA_REST = re.compile(r"@(RestController|Controller)\b")
_JAVA_CALL = re.compile(r"\.(\w+)\s*\(")
_JAVA_METHOD = re.compile(
    r"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],\s.]+?\s+(\w+)\s*\([^;{]*\)\s*\{"
)


def _node_type(asset_type: str) -> str:
    return _NODE_TYPE.get(asset_type, "code")


def _module_name(path: str) -> str:
    """경로에서 사람이 읽는 모듈명(파일 stem)."""
    name = path.rsplit("/", 1)[-1]
    return name.rsplit(".", 1)[0] if "." in name else name


# --------------------------------------------------------------- Python (ast)
class _PyVisitor(ast.NodeVisitor):
    """import·함수 정의·호출을 수집한다(현재 함수 스코프 추적)."""

    def __init__(self) -> None:
        self.imports: list[str] = []
        self.calls: list[tuple[str, str]] = []  # (caller, callee)
        self._scope: list[str] = ["<module>"]

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            self.imports.append(alias.name)

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        if node.module:
            self.imports.append(node.module)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._scope.append(node.name)
        self.generic_visit(node)
        self._scope.pop()

    visit_AsyncFunctionDef = visit_FunctionDef  # type: ignore[assignment]

    def visit_Call(self, node: ast.Call) -> None:
        callee = _call_name(node.func)
        if callee:
            self.calls.append((self._scope[-1], callee))
        self.generic_visit(node)


def _call_name(func: ast.AST) -> str:
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return func.attr
    return ""


def _extract_python(asset: "Asset", graph: RelationGraph) -> None:
    """Python 소스를 ast로 파싱해 dep/call 엣지를 그래프에 추가한다."""
    tree = ast.parse(asset.content or "")  # 실패 시 SyntaxError → 호출자가 unresolved 처리
    v = _PyVisitor()
    v.visit(tree)
    for mod in v.imports:
        graph.dep_edges.append(
            DependencyEdge(
                src=asset.path,
                dst=mod,
                evidence=Evidence(
                    source=asset.path, type=asset.type, location=f"import {mod}",
                    extracted_value=mod, relation=EvidenceRelation.DIRECT,
                ),
            )
        )
    for caller, callee in v.calls:
        graph.call_edges.append(
            CallEdge(
                caller=f"{_module_name(asset.path)}.{caller}",
                callee=callee,
                file=asset.path,
                evidence=Evidence(source=asset.path, type=asset.type, location=f"{caller}()→{callee}()"),
            )
        )


# --------------------------------------------------------------- Java (regex)
def _extract_java(asset: "Asset", graph: RelationGraph) -> None:
    content = asset.content or ""
    for mod in _JAVA_IMPORT.findall(content):
        graph.dep_edges.append(
            DependencyEdge(
                src=asset.path,
                dst=mod,
                evidence=Evidence(
                    source=asset.path, type=asset.type, location=f"import {mod};",
                    extracted_value=mod, relation=EvidenceRelation.DIRECT,
                ),
            )
        )
    stem = _module_name(asset.path)
    methods = set(_JAVA_METHOD.findall(content))
    for callee in _JAVA_CALL.findall(content):
        graph.call_edges.append(
            CallEdge(caller=stem, callee=callee, file=asset.path,
                     evidence=Evidence(source=asset.path, type=asset.type, location=f".{callee}()"))
        )
    # 메서드 정의도 호출 대상 노드로 알 수 있게 남긴다(자기 정의)
    for m in sorted(methods):
        graph.call_edges.append(
            CallEdge(caller=stem, callee=m, file=asset.path,
                     evidence=Evidence(source=asset.path, type=asset.type, location=f"def {m}(...)"))
        )


# --------------------------------------------------------------- 진입점
def find_entry_points(assets: list["Asset"]) -> list[EntryPoint]:
    """실행/요청 진입점을 정적 단서로 찾는다 (US-07.2, FR-MAP-003)."""
    out: list[EntryPoint] = []
    for a in assets:
        content = a.content or ""
        ext = a.filename.rsplit(".", 1)[-1].lower() if "." in a.filename else ""
        if ext == "java":
            if _JAVA_REST.search(content):
                out.append(EntryPoint("rest_controller", _module_name(a.path), a.path,
                                       "@RestController/@Controller 애노테이션"))
            for m in _JAVA_MAPPING.finditer(content):
                verb = m.group(1)
                route = (m.group(2) or "").strip()
                out.append(EntryPoint("rest_endpoint", f"{verb}Mapping {route}".strip(), a.path,
                                       f"@{verb}Mapping 라우트"))
            if _JAVA_MAIN.search(content):
                out.append(EntryPoint("main", "main", a.path, "public static void main 진입점"))
        elif ext == "py":
            if re.search(r"__name__\s*==\s*['\"]__main__['\"]", content):
                out.append(EntryPoint("main", "__main__", a.path, "if __name__ == '__main__' 블록"))
            for m in re.finditer(r"@(app|router|blueprint)\.(get|post|put|delete|route)\b", content):
                out.append(EntryPoint("route", f"{m.group(1)}.{m.group(2)}", a.path, "웹 프레임워크 라우트 데코레이터"))
    # 안정 정렬(결정성)
    out.sort(key=lambda e: (e.file, e.kind, e.symbol))
    return out


# --------------------------------------------------------------- Feature 매핑
def map_features_to_files(store: "KnowledgeStore | None" = None) -> list[FeatureFileMap]:
    """저장된 Feature 지식의 related_sources를 파일 매핑으로 변환한다 (US-07.3, C4 재사용)."""
    from traceki.knowledge import default_store

    store = store or default_store()
    out: list[FeatureFileMap] = []
    for summ in store.list_feature_summaries():
        files = [{"path": p, "category": _guess_category(p)} for p in summ.get("related_sources", [])]
        out.append(FeatureFileMap(feature_id=summ["id"], title=summ["title"], files=files))
    return out


def _guess_category(path: str) -> str:
    p = path.lower()
    if p.endswith((".sql",)):
        return "db"
    if "test" in p:
        return "test"
    if p.endswith((".yaml", ".yml", ".json")):
        return "api"
    if p.endswith((".md", ".txt", ".pdf", ".rst")):
        return "doc"
    return "code"


# --------------------------------------------------------------- 오케스트레이션 진입
def extract_relations(assets: list["Asset"]) -> RelationGraph:
    """자산 목록에서 정적 관계 그래프를 만든다. 파싱 실패는 unresolved로 폴백(무크래시, P2)."""
    graph = RelationGraph()
    for a in assets:
        graph.nodes.append(FileNode(path=a.path, module=_module_name(a.path), type=_node_type(a.type)))
        ext = a.filename.rsplit(".", 1)[-1].lower() if "." in a.filename else ""
        try:
            if ext == "py":
                _extract_python(a, graph)
            elif ext == "java":
                _extract_java(a, graph)
            else:
                if a.type in ("source", "test"):
                    graph.unresolved.append(a.path)  # 미지원 언어 → LLM 폴백
        except (SyntaxError, ValueError, RecursionError) as exc:
            graph.unresolved.append(a.path)
            _log.warning("정적 관계 추출 실패(폴백): %s (%s)", a.path, exc)
    return graph


__all__ = [
    "extract_relations",
    "find_entry_points",
    "map_features_to_files",
]

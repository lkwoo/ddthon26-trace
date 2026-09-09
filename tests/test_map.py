"""UOW-07 온보딩 맵 단위 + 속성(PBT) 테스트.

정적 추출(Python ast · Java 정규식), Mermaid 렌더, overview 왕복을 검증한다.
PBT P1~P4는 순수 로직 불변식을 확인한다(replay/네트워크 불필요, NFR-AI-004).
"""

from __future__ import annotations

from hypothesis import given
from hypothesis import strategies as st

from traceki.engine.assets import Asset
from traceki.knowledge import KnowledgeStore
from traceki.map.mermaid import _node_id, _sanitize_label, render_dependency_graph, render_sequence
from traceki.map.models import (
    DependencyEdge,
    EntryPoint,
    FileNode,
    OnboardingMap,
    RelationGraph,
)
from traceki.map.overview import load_overview, overview_exists, save_overview
from traceki.map.relations import extract_relations, find_entry_points


def _asset(path: str, content: str, atype: str = "source") -> Asset:
    filename = path.rsplit("/", 1)[-1]
    return Asset(path=path, abspath="/" + path, type=atype, filename=filename,
                 content=content, parse_status="ok")


# --------------------------------------------------------- Python 정적 추출
def test_extract_python_imports_and_calls():
    src = "import os\nfrom pkg.sub import thing\n\ndef main():\n    thing()\n    os.getcwd()\n"
    graph = extract_relations([_asset("app/main.py", src)])
    dsts = {e.dst for e in graph.dep_edges}
    assert "os" in dsts and "pkg.sub" in dsts
    callees = {c.callee for c in graph.call_edges}
    assert "thing" in callees and "getcwd" in callees
    assert not graph.unresolved


def test_extract_python_syntax_error_goes_unresolved():
    graph = extract_relations([_asset("bad.py", "def (:\n  ???")])
    assert "bad.py" in graph.unresolved  # 파싱 실패 → 폴백, 예외 없음


# ----------------------------------------------------------- Java 정적 추출
def test_extract_java_imports_and_entry_points():
    src = (
        "package a.b;\n"
        "import a.b.Owner;\n"
        "@RestController\n@RequestMapping(\"/api/owners\")\n"
        "public class OwnerRestController {\n"
        "  @PostMapping\n  public void addOwner() { owner.validate(); }\n}\n"
    )
    a = _asset("a/b/OwnerRestController.java", src)
    graph = extract_relations([a])
    assert any(e.dst == "a.b.Owner" for e in graph.dep_edges)
    eps = find_entry_points([a])
    kinds = {e.kind for e in eps}
    assert "rest_controller" in kinds and "rest_endpoint" in kinds


def test_extract_unsupported_language_unresolved():
    graph = extract_relations([_asset("main.go", "package main\nfunc main(){}", atype="source")])
    assert "main.go" in graph.unresolved


# --------------------------------------------------------------- Mermaid
def test_render_dependency_graph_is_flowchart():
    g = RelationGraph(
        nodes=[FileNode("a.py", "a", "code")],
        dep_edges=[DependencyEdge("a.py", "os"), DependencyEdge("a.py", "b.py")],
    )
    out = render_dependency_graph(g)
    assert out.startswith("flowchart LR")
    assert out.count("-->") == 2


def test_render_sequence_empty_is_valid():
    out = render_sequence([])
    assert out.startswith("sequenceDiagram")


# --------------------------------------------------------- overview 왕복
def test_overview_save_load_roundtrip(tmp_path):
    store = KnowledgeStore(tmp_path)
    omap = OnboardingMap(
        entry_points=[EntryPoint("main", "main", "app.py", "진입점")],
        file_graph=RelationGraph(
            nodes=[FileNode("app.py", "app", "code")],
            dep_edges=[DependencyEdge("app.py", "os")],
        ),
        narrative="온보딩 설명",
        mermaid={"dependency": "flowchart LR", "sequence": "sequenceDiagram"},
    )
    assert not overview_exists(store)
    path = save_overview(omap, store)
    assert path.endswith("overview.md")
    assert overview_exists(store)
    loaded = load_overview(store)
    assert [e.to_dict() for e in loaded.entry_points] == [e.to_dict() for e in omap.entry_points]
    assert [e.to_dict() for e in loaded.file_graph.dep_edges] == \
           [e.to_dict() for e in omap.file_graph.dep_edges]


# ============================================================ PBT P1~P4
_safe_text = st.text(alphabet="abcdefghijklmnop_/.0123456789", min_size=1, max_size=20)


@given(st.lists(st.tuples(_safe_text, _safe_text), max_size=15))
def test_p1_dependency_graph_includes_all_edge_nodes(pairs):
    """P1: dep_edge가 참조하는 모든 노드가 렌더 출력에 선언된다."""
    g = RelationGraph(dep_edges=[DependencyEdge(s, d) for s, d in pairs])
    out = render_dependency_graph(g)
    for s, d in pairs:
        assert _node_id(s) in out
        assert _node_id(d) in out


@given(st.text(max_size=200))
def test_p2_python_extraction_never_crashes(source):
    """P2: 임의 소스에 무크래시(파싱 실패=unresolved, 예외 누출 없음)."""
    graph = extract_relations([_asset("x.py", source)])
    assert isinstance(graph, RelationGraph)


@given(
    st.lists(st.tuples(_safe_text, _safe_text), min_size=1, max_size=10),
    st.lists(st.tuples(_safe_text, _safe_text), max_size=10),
)
def test_p3_overview_roundtrip_preserves_entrypoints_and_edges(tmp_path_factory, eps, deps):
    """P3: save_overview→load_overview 왕복에서 entry_points·edges 보존."""
    store = KnowledgeStore(tmp_path_factory.mktemp("ov"))
    omap = OnboardingMap(
        entry_points=[EntryPoint("main", sym, f, "r") for sym, f in eps],
        file_graph=RelationGraph(dep_edges=[DependencyEdge(s, d) for s, d in deps]),
        narrative="n",
    )
    save_overview(omap, store)
    loaded = load_overview(store)
    assert [e.to_dict() for e in loaded.entry_points] == [e.to_dict() for e in omap.entry_points]
    assert [e.to_dict() for e in loaded.file_graph.dep_edges] == \
           [e.to_dict() for e in omap.file_graph.dep_edges]


@given(st.text(max_size=100))
def test_p4_sanitize_label_is_idempotent(text):
    """P4: 라벨 안전화는 멱등이며 개행·따옴표 파손을 만들지 않는다."""
    once = _sanitize_label(text)
    assert _sanitize_label(once) == once
    assert "\n" not in once and '"' not in once

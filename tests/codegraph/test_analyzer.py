"""PBT-10 example tests for the code structure analyzer (FR-2.1/2.2, US-2.2)."""

from knowledge_store.codegraph.analyzer import CodeStructureAnalyzer, CodeUnit
from knowledge_store.types import EdgeType, Status


def _analyze(text: str):
    return CodeStructureAnalyzer().analyze([CodeUnit(path="a.py", language="python", text=text)])


def test_defines_functions_and_classes():
    result = _analyze("class Foo:\n    pass\n\ndef bar():\n    return 1\n")
    assert result.status == Status.OK
    names = {n.name for n in result.nodes}
    assert {"Foo", "bar", "a.py"} <= names


def test_resolves_call_to_definition():
    text = "def helper():\n    return 1\n\ndef main():\n    helper()\n"
    result = _analyze(text)
    call_edges = [e for e in result.edges if e.type == EdgeType.CALL]
    assert any(e.resolved for e in call_edges)


def test_unresolved_call_is_recorded_not_fatal():
    result = _analyze("def main():\n    external_thing()\n")
    assert "external_thing" in result.unresolved
    assert result.status == Status.OK


def test_inheritance_edge_resolves_cross_symbol():
    units = [
        CodeUnit(path="base.py", language="python", text="class Base:\n    pass\n"),
        CodeUnit(path="child.py", language="python", text="class Child(Base):\n    pass\n"),
    ]
    result = CodeStructureAnalyzer().analyze(units)
    inherit = [e for e in result.edges if e.type == EdgeType.INHERIT]
    assert any(e.resolved for e in inherit)


def test_deterministic_across_runs():
    text = "def a():\n    b()\n\ndef b():\n    pass\n"
    r1 = _analyze(text)
    r2 = _analyze(text)
    assert [n.id for n in r1.nodes] == [n.id for n in r2.nodes]
    assert [(e.src, e.dst, e.type) for e in r1.edges] == [(e.src, e.dst, e.type) for e in r2.edges]

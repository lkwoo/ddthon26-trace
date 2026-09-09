"""UOW-05 serialize_result 단위 테스트 (NFR-05-UX-1, 핵심 우선 순서)."""

from __future__ import annotations

from trace.mcp_server.serialize import serialize_result
from trace.models.result import ConflictOut, Result, Warning, build_result


def test_key_order_core_first() -> None:
    r = build_result(
        "요약",
        data={"x": 1},
        conflicts=[ConflictOut(type="value_mismatch", claim="a.b",
                               values=[{"value": "1", "source": "s", "location": "L1"}],
                               interpretation="i")],
        warnings=[Warning(code="w", message="경고")],
        meta={"conflicts_count": 1},
    )
    keys = list(serialize_result(r).keys())
    # conflicts가 data 뒤·meta 앞(핵심 우선)
    assert keys.index("summary") < keys.index("data") < keys.index("conflicts") < keys.index("meta")


def test_empty_collections_omitted() -> None:
    r = Result(summary="s")
    out = serialize_result(r)
    assert out == {"summary": "s"}  # 빈 data/conflicts/warnings/meta 생략


def test_impact_included_when_present() -> None:
    from trace.models.result import ImpactItem, ImpactOut
    r = build_result("s", impact=ImpactOut(must_change=[ImpactItem(path="p", reason="r")]))
    out = serialize_result(r)
    assert "impact" in out
    assert out["impact"]["must_change"][0]["path"] == "p"

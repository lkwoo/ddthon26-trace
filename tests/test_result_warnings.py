"""Result 조립 + WarningCollector 테스트 (BR-WARN, build_result 규칙)."""

from __future__ import annotations

from trace.common.warnings import CODE_PARSE_PARTIAL, WarningCollector
from trace.models.result import ConflictOut, Warning, build_result


def test_build_result_basic():
    r = build_result("완료", {"features": 3})
    assert "완료" in r.summary
    assert r.meta["conflicts_count"] == 0
    assert r.meta["warnings_count"] == 0


def test_build_result_surfaces_conflicts_first():
    conflicts = [
        ConflictOut(type="value_mismatch", claim="x.y", values=[], interpretation="i")
    ]
    r = build_result("본문 요약", {}, conflicts=conflicts)
    # 충돌 요약이 본문보다 앞에 위치 (핵심 우선)
    assert r.summary.index("충돌") < r.summary.index("본문 요약")
    assert r.meta["conflicts_count"] == 1


def test_build_result_appends_warnings():
    warnings = [Warning(code=CODE_PARSE_PARTIAL, message="일부 파일 파싱 실패", source="a.py")]
    r = build_result("요약", {}, warnings=warnings)
    assert "경고 1건" in r.summary
    assert r.warnings[0].code == CODE_PARSE_PARTIAL  # 구조화 원형 유지


def test_warning_collector():
    c = WarningCollector()
    assert not c
    c.add(CODE_PARSE_PARTIAL, "부분 실패", source="x.md")
    assert len(c) == 1
    assert bool(c)
    lst = c.to_list()
    assert lst[0].code == CODE_PARSE_PARTIAL
    # to_list는 사본 — 원본 불변
    lst.clear()
    assert len(c) == 1

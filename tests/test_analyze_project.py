"""UOW-03 전체 파이프라인 테스트 — FakeLLM 주입 (BR-PIPE, Q5=A)."""

from __future__ import annotations

import json
from pathlib import Path

from trace.engine.analyze import analyze_project, get_conflicts
from trace.llm.service import LLMService

from tests.conftest import FakeLLMClient

_FEATURES = json.dumps({"features": [
    {"id": "owner-management", "title": "Owner Management", "description": "주인 관리",
     "related_sources": ["src/Owner.java", "docs/spec.md"], "rationale": "r"},
]})
_BODY = json.dumps({"markdown": "# Owner Management\n\n개요"})
_EXTRACTION = json.dumps({"claims": [
    {"subject": "owner.telephone", "predicate": "max_length", "evidence": [
        {"source": "docs/spec.md", "type": "markdown", "location": "L1",
         "extracted_value": "20", "relation": "supports"},
        {"source": "src/Owner.java", "type": "source", "location": "L42",
         "extracted_value": "10", "relation": "contradicts"},
    ]},
]})


def _make_project(root: Path) -> None:
    (root / "src").mkdir(parents=True)
    (root / "docs").mkdir(parents=True)
    (root / "src" / "Owner.java").write_text("class Owner { String telephone; }", encoding="utf-8")
    (root / "docs" / "spec.md").write_text("# Spec\ntelephone max 20", encoding="utf-8")


def test_analyze_project_detects_conflict(tmp_path: Path) -> None:
    _make_project(tmp_path)
    fake = FakeLLMClient([_FEATURES, _BODY, _EXTRACTION])
    result = analyze_project(str(tmp_path), llm=LLMService(fake))

    assert result.data["conflicts_count"] == 1
    assert result.data["assets_count"] >= 2
    assert result.conflicts[0].claim == "owner.telephone.max_length"
    assert result.conflicts[0].type == "value_mismatch"
    assert len(fake.calls) == 3  # identify + knowledge + extract


def test_analyze_project_second_run_uses_cache_no_llm(tmp_path: Path) -> None:
    _make_project(tmp_path)
    analyze_project(str(tmp_path), llm=LLMService(FakeLLMClient([_FEATURES, _BODY, _EXTRACTION])))

    # 2회차: 자산 불변 → 캐시 히트 + 완본 스테이지 → LLM 미호출
    fake2 = FakeLLMClient([])  # 호출되면 예외
    result = analyze_project(str(tmp_path), llm=LLMService(fake2))
    assert len(fake2.calls) == 0
    assert result.data["conflicts_count"] == 1


def test_analyze_project_isolates_extract_failure(tmp_path: Path) -> None:
    _make_project(tmp_path)
    # 추출 단계 실패(무효 JSON, 재시도 소진) → warning 강등, 파이프라인 계속
    fake = FakeLLMClient([_FEATURES, _BODY, "bad", "bad", "bad"])
    result = analyze_project(str(tmp_path), llm=LLMService(fake))
    assert result.data["conflicts_count"] == 0
    assert any(w.code == "extract_failed" for w in result.warnings)


def test_get_conflicts_reads_stored(tmp_path: Path) -> None:
    _make_project(tmp_path)
    analyze_project(str(tmp_path), llm=LLMService(FakeLLMClient([_FEATURES, _BODY, _EXTRACTION])))

    result = get_conflicts(path=str(tmp_path))
    assert result.meta["conflicts_count"] == 1
    assert result.conflicts[0].claim == "owner.telephone.max_length"

    # feature_id 지정
    scoped = get_conflicts("owner-management", path=str(tmp_path))
    assert scoped.meta["conflicts_count"] == 1


def test_get_conflicts_unknown_feature(tmp_path: Path) -> None:
    _make_project(tmp_path)
    analyze_project(str(tmp_path), llm=LLMService(FakeLLMClient([_FEATURES, _BODY, _EXTRACTION])))
    result = get_conflicts("does-not-exist", path=str(tmp_path))
    assert result.meta["conflicts_count"] == 0
    assert any(w.code == "feature_not_found" for w in result.warnings)


def test_analyze_project_invalid_path() -> None:
    result = analyze_project("/no/such/path/xyz", llm=LLMService(FakeLLMClient([])))
    # 무효 경로는 오류 Result (예외 전파 없음)
    assert result.warnings or "찾을 수 없" in result.summary or result.data == {}

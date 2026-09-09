"""UOW-06 Hero 시나리오 E2E (US-06.1, NFR-REL-001/AI-004).

demo/ 데이터셋에 스크립트 FakeLLM을 주입해 전체 코어 파이프라인을 구동한다:
analyze_project → get_conflicts → analyze_task_impact. 스캔·파싱·저장·충돌검출·영향매핑은 실제 코드.
반복 실행 시 동일 출력(고정 데이터셋, 결정적).
"""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from trace.engine.analyze import (
    analyze_project,
    analyze_task_impact,
    get_conflicts,
    get_feature_knowledge,
    list_features,
)
from trace.engine.scan import scan_project_assets
from trace.llm.service import LLMService

# demo 하니스의 스크립트 빌더 재사용(단일 진실원)
import sys
_REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO / "demo"))
from run_demo import _build_scripts, _ScriptedLLM, _impact_script  # type: ignore  # noqa: E402

_DEMO = _REPO / "demo"


@pytest.fixture
def demo_root(tmp_path: Path) -> str:
    root = tmp_path / "demo"
    shutil.copytree(_DEMO, root, ignore=shutil.ignore_patterns("run_demo.py", "__pycache__", ".trace"))
    return str(root)


def _run_analysis(demo_root: str):
    assets, _ = scan_project_assets(demo_root)
    scripts, hero_fid = _build_scripts(assets)
    result = analyze_project(demo_root, llm=LLMService(_ScriptedLLM(scripts)))
    return result, assets, hero_fid


def test_hero_analyze_detects_three_conflicts(demo_root: str) -> None:
    result, _, _ = _run_analysis(demo_root)
    assert result.data["conflicts_count"] == 3
    types = {c.type for c in result.conflicts}
    assert types == {"value_mismatch", "policy_conflict", "stale_knowledge"}


def test_hero_full_flow(demo_root: str) -> None:
    _, assets, hero_fid = _run_analysis(demo_root)

    # list_features / get_feature_knowledge (저장 지식, LLM 미호출)
    features = list_features(path=demo_root).data["features"]
    assert {f["id"] for f in features} == {"owner-registration", "pet-management"}
    fk = get_feature_knowledge("owner-registration", path=demo_root)
    assert fk.data["resource_uri"] == "trace://feature/owner-registration"

    # get_conflicts
    assert get_conflicts(path=demo_root).meta["conflicts_count"] == 3

    # analyze_task_impact — 충돌 경고 + 3범주 + Change Plan
    impact = analyze_task_impact("Add SMS verification to Owner registration", hero_fid,
                                 path=demo_root, llm=LLMService(_ScriptedLLM(_impact_script(assets))))
    assert impact.impact is not None
    assert len(impact.impact.related_conflicts) == 2  # owner-registration의 기존 충돌(telephone·email)
    assert impact.impact.must_change and impact.impact.change_plan
    assert "충돌" in impact.summary  # 구현 권고 전 경고 상단 노출


def test_hero_is_repeatable(demo_root: str) -> None:
    """고정 데이터셋 반복 실행 → 동일 충돌 집합 (NFR-AI-004)."""
    r1, _, _ = _run_analysis(demo_root)
    first = sorted((c.type, c.claim) for c in r1.conflicts)

    # 2회차: 캐시 히트 + 완본 스테이지 → LLM 미호출로도 동일 결과
    r2 = analyze_project(demo_root, llm=LLMService(_ScriptedLLM([])))
    second = sorted((c.type, c.claim) for c in r2.conflicts)
    assert first == second

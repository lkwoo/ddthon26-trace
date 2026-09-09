"""UOW-07 온보딩 맵 통합 테스트 — 데모(Java Petclinic) 대상.

replay 백엔드(demo/replay/describe_relations.json)로 API 키 없이 결정적으로 검증한다
(NFR-AI-004, NFR-REL-001). Hero 온보딩 시나리오: 진입점·의존 그래프·Feature→파일·핵심
흐름·내러티브가 overview.md에 Mermaid 포함으로 생성되고 관계에 근거가 인용된다.
"""

from __future__ import annotations

from pathlib import Path

from traceki.config import Config, LLMSettings
from traceki.engine import generate_onboarding_map
from traceki.engine.pipeline import analyze_project
from traceki.knowledge import KnowledgeStore
from traceki.map.overview import load_overview, overview_path

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
REPLAY = DEMO / "replay"


def _replay_config() -> Config:
    return Config(llm=LLMSettings(backend="replay", replay_dir=str(REPLAY)))


def test_generate_onboarding_map_on_demo(tmp_path):
    store = KnowledgeStore(tmp_path)
    # Feature 지식을 먼저 채워야 Feature→파일 매핑이 포함된다(C4 재사용).
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)

    r = generate_onboarding_map(str(DEMO), config=_replay_config(), store=store, refresh=True)
    assert r.meta["ok"] is True

    # 진입점: OwnerRestController(REST) 검출
    eps = r.data["entry_points"]
    assert any(e["kind"] == "rest_controller" for e in eps)
    assert any("OwnerRestController" in e["file"] for e in eps)

    # 의존 그래프: Java import 엣지가 잡힘
    graph = r.data["file_graph"]
    assert graph["nodes"] and graph["dep_edges"]

    # Feature → 파일 매핑에 Hero Feature 포함
    fmaps = r.data["feature_file_maps"]
    assert any(m["feature_id"] == "owner-registration" for m in fmaps)

    # 내러티브(replay) + Mermaid 2종
    assert "OwnerRestController" in r.summary
    assert r.data["mermaid"]["dependency"].startswith("flowchart LR")
    assert r.data["mermaid"]["sequence"].startswith("sequenceDiagram")

    # 관계 근거 인용(FR-MAP-007)
    assert r.evidence


def test_overview_md_written_with_mermaid(tmp_path):
    store = KnowledgeStore(tmp_path)
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)
    generate_onboarding_map(str(DEMO), config=_replay_config(), store=store, refresh=True)

    path = Path(overview_path(store))
    assert path.is_file()
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---")            # YAML front matter
    assert "```mermaid" in text              # embedded diagram
    assert "# 프로젝트 온보딩 맵" in text


def test_generate_onboarding_map_uses_cache(tmp_path):
    store = KnowledgeStore(tmp_path)
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)
    generate_onboarding_map(str(DEMO), config=_replay_config(), store=store, refresh=True)

    second = generate_onboarding_map(str(DEMO), config=_replay_config(), store=store)  # refresh=False
    assert second.data.get("cached") is True


def test_generate_onboarding_map_invalid_path():
    r = generate_onboarding_map(str(ROOT / "does-not-exist"), config=_replay_config())
    assert r.meta["ok"] is False


def test_overview_roundtrip_from_demo(tmp_path):
    store = KnowledgeStore(tmp_path)
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)
    generate_onboarding_map(str(DEMO), config=_replay_config(), store=store, refresh=True)
    loaded = load_overview(store)
    assert loaded.entry_points
    assert loaded.narrative

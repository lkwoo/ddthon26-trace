"""UOW-04 Task Impact 테스트 — Hero 작업 영향 분석 (replay E2E)."""

from __future__ import annotations

from pathlib import Path

from trace.config import Config, LLMSettings
from trace.engine.pipeline import analyze_project
from trace.impact import analyze_task_impact
from trace.knowledge import KnowledgeStore

DEMO = Path(__file__).resolve().parents[1] / "demo"
REPLAY = DEMO / "replay"
HERO = "Add SMS verification to Owner registration"


def _prepared_store(tmp_path) -> tuple[KnowledgeStore, Config]:
    store = KnowledgeStore(tmp_path)
    cfg = Config(llm=LLMSettings(backend="replay", replay_dir=str(REPLAY)))
    analyze_project(str(DEMO), config=cfg, store=store, refresh=True)
    return store, cfg


def test_empty_task_returns_error(tmp_path):
    store, cfg = _prepared_store(tmp_path)
    r = analyze_task_impact("   ", store=store, config=cfg)
    assert r.meta["ok"] is False


def test_no_knowledge_guides_to_analyze_first(tmp_path):
    cfg = Config(llm=LLMSettings(backend="replay", replay_dir=str(REPLAY)))
    r = analyze_task_impact(HERO, store=KnowledgeStore(tmp_path), config=cfg)
    assert r.meta["ok"] is False
    assert "analyze_project" in r.summary


def test_hero_task_impact_classifies_and_plans(tmp_path):
    store, cfg = _prepared_store(tmp_path)
    r = analyze_task_impact(HERO, store=store, config=cfg)
    assert r.meta["ok"] is True
    imp = r.impact
    # 컨트롤러가 반드시 변경 대상 (SMS 인증 없음)
    must_paths = [m["path"] for m in imp["must_change"]]
    assert any("OwnerRestController" in p for p in must_paths)
    # 순서형 Change Plan 존재
    assert len(imp["change_plan"]) >= 3
    # 모든 must 항목은 근거를 동반 (그라운딩)
    assert all(m["evidence"] for m in imp["must_change"])


def test_hero_task_is_conflict_aware(tmp_path):
    store, cfg = _prepared_store(tmp_path)
    r = analyze_task_impact(HERO, store=store, config=cfg)
    # 전화번호 길이 충돌을 함께 경고
    assert r.meta["conflicts_count"] >= 1
    claims = {c["claim"] for c in r.conflicts}
    assert "Owner.telephone.max_length" in claims
    assert r.warnings and any("충돌" in w for w in r.warnings)


def test_impact_does_not_mutate_sources(tmp_path):
    """소스 자동 수정 없음(FR-IMPACT-003) — 데모 파일이 그대로인지 확인."""
    controller = DEMO / "petclinic/src/main/java/org/springframework/samples/petclinic/owner/OwnerRestController.java"
    before = controller.read_bytes()
    store, cfg = _prepared_store(tmp_path)
    analyze_task_impact(HERO, store=store, config=cfg)
    assert controller.read_bytes() == before

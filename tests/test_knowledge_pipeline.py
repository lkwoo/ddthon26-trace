"""UOW-02 지식 저장소·analyze_project 파이프라인 테스트.

replay 백엔드(demo/replay 픽스처)로 API 키 없이 결정적으로 검증한다(NFR-AI-004).
"""

from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import strategies as st

from trace.config import Config, LLMSettings
from trace.engine.pipeline import analyze_project, get_feature_knowledge, list_features
from trace.knowledge import KnowledgeStore, slugify
from trace.models import (
    Claim,
    Confidence,
    Conflict,
    ConflictType,
    ConflictValue,
    Evidence,
    Feature,
    FeatureKnowledge,
)

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "demo"
REPLAY = DEMO / "replay"


def _replay_config() -> Config:
    return Config(llm=LLMSettings(backend="replay", replay_dir=str(REPLAY)))


# ------------------------------------------------------------- 저장소 왕복
def test_store_save_load_roundtrip(tmp_path):
    store = KnowledgeStore(tmp_path)
    fk = FeatureKnowledge(
        feature=Feature(id="owner-registration", title="Owner Registration",
                        related_sources=["a.java", "b.sql"]),
        overview="등록 기능",
        business_rules=["전화번호 검증"],
        claims=[Claim("Owner.telephone", "max_length", "10",
                      evidence=[Evidence("b.sql", "sql", "line 3", "10")])],
        conflicts=[Conflict(ConflictType.VALUE_MISMATCH, "Owner.telephone.max_length",
                            values=[ConflictValue("20", "spec.pdf"), ConflictValue("10", "b.sql")],
                            interpretation="요구 20 vs 구현 10")],
        dependencies=["owners table"],
        confidence=Confidence.HIGH,
    )
    path = store.save_feature(fk)
    assert Path(path).is_file()
    loaded = store.load_feature("owner-registration")
    assert loaded.to_dict() == fk.to_dict()


def test_store_read_resource_has_markdown_body(tmp_path):
    store = KnowledgeStore(tmp_path)
    fk = FeatureKnowledge(feature=Feature(id="f1", title="My Feature"), overview="hello")
    store.save_feature(fk)
    body = store.read_resource("f1")
    assert body.startswith("---")           # YAML front matter
    assert "# My Feature" in body            # human-readable body
    assert "hello" in body


def test_list_summaries_empty(tmp_path):
    assert KnowledgeStore(tmp_path).list_feature_summaries() == []


@given(st.text(min_size=1, max_size=40))
def test_slugify_is_filename_safe(text):
    s = slugify(text)
    assert s and all(c.isalnum() or c in "._-" for c in s)


# --------------------------------------------------- analyze_project (replay)
def test_analyze_project_replay_identifies_hero_feature(tmp_path):
    store = KnowledgeStore(tmp_path)
    r = analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)
    assert r.meta["ok"] is True
    ids = [f["id"] for f in r.data["features"]]
    assert "owner-registration" in ids
    assert r.data["assets_count"] >= 5


def test_analyze_project_persists_and_get_knowledge(tmp_path):
    store = KnowledgeStore(tmp_path)
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)

    lst = list_features(store=store)
    assert lst.meta["ok"] is True
    assert any(f["id"] == "owner-registration" for f in lst.data["features"])

    got = get_feature_knowledge("owner-registration", store=store)
    assert got.meta["ok"] is True
    assert got.data["feature"]["title"] == "Owner Registration"
    assert got.data["business_rules"]                     # non-empty overview/rules
    assert "telephone" in got.summary.lower() or got.data["overview"]


def test_analyze_project_uses_cache_on_second_run(tmp_path):
    store = KnowledgeStore(tmp_path)
    analyze_project(str(DEMO), config=_replay_config(), store=store, refresh=True)
    second = analyze_project(str(DEMO), config=_replay_config(), store=store)  # refresh=False
    assert second.data.get("cached") is True


def test_get_unknown_feature_returns_error(tmp_path):
    r = get_feature_knowledge("does-not-exist", store=KnowledgeStore(tmp_path))
    assert r.meta["ok"] is False

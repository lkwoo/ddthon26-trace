"""UOW-02 워크플로 테스트 — FakeLLM 주입, 부분실패 강등, 캐시 (BR-IDF/KN/FAIL/CACHE)."""

from __future__ import annotations

import json
from pathlib import Path

from trace.knowledge.cache import AnalysisCache
from trace.knowledge.store import KnowledgeStore
from trace.llm.service import LLMService
from trace.models.asset import Asset, AssetType, ParseStatus
from trace.workflow.features import (
    build_knowledge,
    generate_feature_knowledge,
    identify_features,
)

from tests.conftest import FakeLLMClient


def _assets() -> list[Asset]:
    return [
        Asset(rel_path="src/Owner.java", filename="Owner.java", asset_type=AssetType.SOURCE,
              parse_status=ParseStatus.PARSED, size_bytes=10, content="class Owner {}"),
        Asset(rel_path="db/schema.sql", filename="schema.sql", asset_type=AssetType.SQL,
              parse_status=ParseStatus.PARSED, size_bytes=10, content="CREATE TABLE owners"),
    ]


def _features_json(*ids: str) -> str:
    return json.dumps({"features": [
        {"id": i, "title": i.replace("-", " ").title(), "description": "desc",
         "related_sources": ["src/Owner.java"], "rationale": "r"} for i in ids
    ]})


def _body_json(text: str = "# F\n\n본문") -> str:
    return json.dumps({"markdown": text})


def test_identify_features_parses_and_sorts() -> None:
    fake = FakeLLMClient([_features_json("pet-care", "owner-management")])
    features, warnings = identify_features(_assets(), LLMService(fake))
    assert warnings == []
    ids = [f.id for f in features]
    assert ids == sorted(ids)  # 결정적 정렬
    assert "owner-management" in ids


def test_identify_failure_degrades_to_warning() -> None:
    # 항상 무효 JSON → 검증 소진 → 빈 목록 + warning (예외 전파 없음)
    fake = FakeLLMClient(["not json", "still not", "nope"])
    features, warnings = identify_features(_assets(), LLMService(fake))
    assert features == []
    assert warnings and warnings[0].code == "identify_failed"


def test_generate_knowledge_falls_back_on_llm_failure() -> None:
    from trace.models.domain import Feature
    feature = Feature(id="owner-management", title="Owner Management",
                      description="주인 관리", related_sources=["src/Owner.java"])
    fake = FakeLLMClient(["bad", "bad", "bad"])  # 본문 생성 실패
    fk = generate_feature_knowledge(feature, _assets(), LLMService(fake))
    assert fk.feature.id == "owner-management"
    assert "Owner Management" in fk.body_markdown          # 템플릿 폴백 본문
    assert fk.meta.get("knowledge_fallback") is True
    assert fk.claims == [] and fk.conflicts == []          # Q2=A 셸


def test_build_knowledge_caches_second_run(tmp_path: Path) -> None:
    assets = _assets()
    store = KnowledgeStore(tmp_path)
    cache = AnalysisCache(tmp_path)

    fake1 = FakeLLMClient([_features_json("owner-management"), _body_json()])
    summaries1, w1 = build_knowledge(assets, LLMService(fake1), store, cache)
    assert [s.id for s in summaries1] == ["owner-management"]
    assert len(fake1.calls) == 2  # 식별 1 + 지식 1

    # 2회차: 동일 자산 → 캐시 히트 → LLM 미호출
    fake2 = FakeLLMClient([])  # 호출되면 예외
    summaries2, w2 = build_knowledge(assets, LLMService(fake2), store, AnalysisCache(tmp_path))
    assert [s.id for s in summaries2] == ["owner-management"]
    assert len(fake2.calls) == 0


def test_build_knowledge_isolates_feature_failure(tmp_path: Path) -> None:
    assets = _assets()
    # 2개 Feature 식별, 첫 본문 성공 / 둘째 본문은 폴백(실패)이라도 저장은 계속
    fake = FakeLLMClient([
        _features_json("owner-management", "pet-care"),
        _body_json("# Owner"),      # owner-management 본문
        "bad", "bad", "bad",         # pet-care 본문 실패 → 폴백
    ])
    summaries, warnings = build_knowledge(assets, LLMService(fake), KnowledgeStore(tmp_path), AnalysisCache(tmp_path))
    ids = {s.id for s in summaries}
    assert {"owner-management", "pet-care"} <= ids  # 둘 다 저장됨(폴백 포함)

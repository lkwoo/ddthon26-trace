"""UOW-05 코어 래퍼 테스트 — list_features / get_feature_knowledge (NFR-05-IF-1)."""

from __future__ import annotations

from pathlib import Path

from trace.engine import get_feature_knowledge, list_features
from trace.knowledge.store import KnowledgeStore
from trace.models.domain import (
    Conflict,
    ConflictValue,
    Feature,
    FeatureKnowledge,
)


def _seed(root: Path) -> None:
    store = KnowledgeStore(root)
    store.save_feature(FeatureKnowledge(
        feature=Feature(id="owner-management", title="Owner Management", description="주인 관리",
                        related_sources=["src/Owner.java"]),
        conflicts=[Conflict(claim="owner.telephone.max_length",
                            values=[ConflictValue(value="20", source="docs/spec.md", location="p.3"),
                                    ConflictValue(value="10", source="src/Owner.java", location="L42")],
                            interpretation="충돌")],
        meta={"stage": "complete"},
    ))


def test_list_features_returns_summaries(tmp_path: Path) -> None:
    _seed(tmp_path)
    result = list_features(path=str(tmp_path))
    assert result.meta["features_count"] == 1
    assert result.data["features"][0]["id"] == "owner-management"


def test_list_features_empty(tmp_path: Path) -> None:
    result = list_features(path=str(tmp_path))
    assert result.meta["features_count"] == 0


def test_get_feature_knowledge_returns_detail(tmp_path: Path) -> None:
    _seed(tmp_path)
    result = get_feature_knowledge("owner-management", path=str(tmp_path))
    assert result.data["feature"]["id"] == "owner-management"
    assert result.data["resource_uri"] == "trace://feature/owner-management"
    assert len(result.conflicts) == 1


def test_get_feature_knowledge_missing_returns_error_result(tmp_path: Path) -> None:
    result = get_feature_knowledge("does-not-exist", path=str(tmp_path))
    # 부재는 예외 전파가 아니라 오류 Result
    assert result.warnings or "찾을 수 없" in result.summary or result.meta.get("error")

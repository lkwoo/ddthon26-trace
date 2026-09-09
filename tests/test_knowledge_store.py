"""UOW-02 KnowledgeStore 테스트 (BR-STORE)."""

from __future__ import annotations

from pathlib import Path

import pytest

from trace.common.errors import StorageError
from trace.knowledge.store import KnowledgeStore


def test_save_and_load_round_trip(tmp_path: Path, sample_feature_knowledge) -> None:  # type: ignore[no-untyped-def]
    store = KnowledgeStore(tmp_path)
    path = store.save_feature(sample_feature_knowledge)
    assert Path(path).exists()
    # 저장 경로는 프로젝트 루트 하위 (.trace/knowledge/features)
    assert Path(path).resolve().is_relative_to((tmp_path / ".trace").resolve())

    loaded = store.load_feature(sample_feature_knowledge.feature.id)
    assert loaded.feature.id == sample_feature_knowledge.feature.id
    assert loaded.feature.title == sample_feature_knowledge.feature.title
    assert len(loaded.conflicts) == len(sample_feature_knowledge.conflicts)


def test_list_feature_summaries_skips_corrupt(tmp_path: Path, sample_feature_knowledge) -> None:  # type: ignore[no-untyped-def]
    store = KnowledgeStore(tmp_path)
    store.save_feature(sample_feature_knowledge)
    # 손상 파일 1개 주입 → 목록은 계속(해당 파일 skip)
    (store.features_dir() / "broken.md").write_text("not a valid knowledge file", encoding="utf-8")

    summaries = store.list_feature_summaries()
    ids = [s.id for s in summaries]
    assert sample_feature_knowledge.feature.id in ids
    assert "broken" not in ids


def test_read_resource_returns_body(tmp_path: Path, sample_feature_knowledge) -> None:  # type: ignore[no-untyped-def]
    store = KnowledgeStore(tmp_path)
    store.save_feature(sample_feature_knowledge)
    uri = f"trace://feature/{sample_feature_knowledge.feature.id}"
    body = store.read_resource(uri)
    assert isinstance(body, str) and len(body) > 0


def test_load_missing_raises(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path)
    with pytest.raises(StorageError):
        store.load_feature("no-such-feature")


def test_read_resource_bad_uri_raises(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path)
    with pytest.raises(StorageError):
        store.read_resource("http://feature/x")


def test_empty_store_lists_nothing(tmp_path: Path) -> None:
    assert KnowledgeStore(tmp_path).list_feature_summaries() == []

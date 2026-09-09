"""UOW-04 컨텍스트 조립·관련도 랭킹 단위 테스트 (BR-CTX)."""

from __future__ import annotations

from pathlib import Path

from trace.impact.context import build_context, rank_by_relevance
from trace.knowledge.store import KnowledgeStore
from trace.models.domain import (
    Conflict,
    ConflictValue,
    Evidence,
    EvidenceRelation,
    EvidenceType,
    Feature,
    FeatureKnowledge,
)
from trace.models.result import FeatureSummary


def _summary(fid: str, title: str, sources: list[str]) -> FeatureSummary:
    return FeatureSummary(id=fid, title=title, related_sources=sources)


def test_rank_by_relevance_orders_by_token_overlap() -> None:
    summaries = [
        _summary("pet-care", "Pet Care", ["src/Pet.java"]),
        _summary("owner-management", "Owner Management", ["src/Owner.java"]),
    ]
    ranked = rank_by_relevance("add sms verification to owner registration", summaries)
    assert ranked[0] == "owner-management"  # 'owner' 토큰 겹침


def test_rank_is_deterministic_tie_break_by_id() -> None:
    summaries = [
        _summary("b-feat", "Zzz", []),
        _summary("a-feat", "Zzz", []),
    ]
    # 겹침 0 동률 → id 사전순
    assert rank_by_relevance("unrelated task", summaries) == ["a-feat", "b-feat"]


def _save_feature(store: KnowledgeStore, fid: str, sources: list[str]) -> None:
    fk = FeatureKnowledge(
        feature=Feature(id=fid, title=fid.title(), description="d", related_sources=sources),
        evidence=[Evidence(source=sources[0], type=EvidenceType.SOURCE, location="L1",
                           extracted_value="10", relation=EvidenceRelation.SUPPORTS)] if sources else [],
        conflicts=[Conflict(claim="owner.telephone.max_length",
                            values=[ConflictValue(value="20", source="docs/spec.md", location="p.3"),
                                    ConflictValue(value="10", source=sources[0], location="L1")],
                            interpretation="충돌")] if sources else [],
    )
    store.save_feature(fk)


def test_build_context_focus_by_feature_id(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path)
    _save_feature(store, "owner-management", ["src/Owner.java"])
    _save_feature(store, "pet-care", ["src/Pet.java"])

    ctx, warnings = build_context("task", "owner-management", store)
    assert warnings == []
    assert [fk.feature.id for fk in ctx.focus] == ["owner-management"]
    assert "src/Owner.java" in ctx.known_sources
    assert len(ctx.conflicts) == 1


def test_build_context_no_knowledge(tmp_path: Path) -> None:
    ctx, warnings = build_context("task", None, KnowledgeStore(tmp_path))
    assert ctx.focus == []
    assert ctx.known_sources == set()


def test_build_context_skips_corrupted(tmp_path: Path) -> None:
    store = KnowledgeStore(tmp_path)
    _save_feature(store, "owner-management", ["src/Owner.java"])
    # 손상 파일 주입
    bad = store.features_dir() / "broken.md"
    bad.write_text("---\nnot: valid feature\n---\n본문", encoding="utf-8")

    ctx, warnings = build_context("owner", None, store)
    # 손상 파일은 skip(요약 목록에서도 제외되거나 로드 skip), 정상 Feature는 유지
    assert any(fk.feature.id == "owner-management" for fk in ctx.focus)

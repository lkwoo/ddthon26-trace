"""UOW-02 속성 기반 테스트 (PBT-02-A~D)."""

from __future__ import annotations

from pathlib import Path

from hypothesis import given, settings
from hypothesis import strategies as st

from trace.knowledge.cache import compute_assets_hash
from trace.knowledge.ids import safe_feature_id
from trace.knowledge.store import KnowledgeStore
from trace.models.asset import Asset, AssetType, ParseStatus
from trace.models.domain import Feature, FeatureKnowledge
from trace.workflow.catalog import build_catalog

PBT = settings(derandomize=True, max_examples=60, deadline=None)

_text = st.text(max_size=80)


# PBT-02-A: id 안전화 전결정성
@PBT
@given(raw=_text)
def test_safe_feature_id_is_always_safe(raw: str) -> None:
    fid = safe_feature_id(raw)
    assert fid                                  # 비어있지 않음
    assert "/" not in fid and "\\" not in fid and ".." not in fid
    # Feature.id 검증을 실제로 통과해야 함
    Feature(id=fid, title="t", description="d")


# PBT-02-B: 캐시 해시 안정성(순서 무관 + 내용 민감)
def _asset(rel: str, content: str) -> Asset:
    return Asset(rel_path=rel, filename=rel, asset_type=AssetType.TEXT,
                 parse_status=ParseStatus.PARSED, size_bytes=len(content), content=content)


@PBT
@given(
    items=st.lists(st.tuples(st.text(min_size=1, max_size=10), _text), min_size=1, max_size=6,
                   unique_by=lambda t: t[0]),
)
def test_hash_order_independent_and_content_sensitive(items) -> None:  # type: ignore[no-untyped-def]
    assets = [_asset(rel, content) for rel, content in items]
    import random
    shuffled = list(assets)
    random.Random(0).shuffle(shuffled)
    assert compute_assets_hash(assets) == compute_assets_hash(shuffled)
    # 한 자산의 내용을 바꾸면 해시가 달라진다
    changed = list(assets)
    changed[0] = _asset(changed[0].rel_path, (changed[0].content or "") + "X")
    assert compute_assets_hash(assets) != compute_assets_hash(changed)


# PBT-02-C: 카탈로그 발췌 상한
@PBT
@given(content=st.text(max_size=10000), cap=st.integers(min_value=1, max_value=2000))
def test_catalog_excerpt_respects_cap(content: str, cap: int) -> None:
    a = _asset("a.txt", content)
    entries = build_catalog([a], excerpt_chars=cap)
    assert len(entries) == 1
    assert len(entries[0].excerpt) <= cap
    assert entries[0].excerpt == content[:cap]  # 접두 발췌


# PBT-02-D: 저장 round-trip (셸)
@PBT
@given(title=st.text(min_size=1, max_size=30), body=st.text(min_size=1, max_size=200))
def test_feature_knowledge_round_trip(tmp_path_factory, title: str, body: str) -> None:  # type: ignore[no-untyped-def]
    root = tmp_path_factory.mktemp("kn")
    fid = safe_feature_id(title)
    fk = FeatureKnowledge(
        feature=Feature(id=fid, title=title, description=title),
        body_markdown=f"# {title}\n\n{body}",
    )
    store = KnowledgeStore(root)
    store.save_feature(fk)
    loaded = store.load_feature(fid)
    assert loaded.feature.id == fid
    assert loaded.feature.title == title

    # serialize는 개행을 \n 으로 정규화한다(UOW-0F 결정성 보장) — 정규화 후 비교.
    def _norm(s: str) -> str:
        return s.replace("\r\n", "\n").replace("\r", "\n").strip()

    assert _norm(loaded.body_markdown) == _norm(fk.body_markdown)

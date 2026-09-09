"""UOW-02 AnalysisCache & 콘텐츠 해시 테스트 (BR-CACHE)."""

from __future__ import annotations

from pathlib import Path

from trace.knowledge.cache import AnalysisCache, CacheEntry, compute_assets_hash
from trace.models.asset import Asset, AssetType, ParseStatus


def _asset(rel: str, content: str) -> Asset:
    return Asset(rel_path=rel, filename=rel.split("/")[-1], asset_type=AssetType.TEXT,
                 parse_status=ParseStatus.PARSED, size_bytes=len(content), content=content)


def test_hash_is_order_independent() -> None:
    a = [_asset("a.txt", "x"), _asset("b.txt", "y")]
    b = list(reversed(a))
    assert compute_assets_hash(a) == compute_assets_hash(b)


def test_hash_changes_on_content_change() -> None:
    base = [_asset("a.txt", "x"), _asset("b.txt", "y")]
    changed = [_asset("a.txt", "x"), _asset("b.txt", "y2")]
    assert compute_assets_hash(base) != compute_assets_hash(changed)


def test_put_get_round_trip(tmp_path: Path) -> None:
    cache = AnalysisCache(tmp_path)
    entry = CacheEntry(assets_hash="deadbeef", feature_ids=["owner-management"])
    cache.put(entry)
    got = cache.get("deadbeef")
    assert got is not None and got.feature_ids == ["owner-management"]


def test_get_miss_when_absent(tmp_path: Path) -> None:
    assert AnalysisCache(tmp_path).get("nope") is None


def test_corrupt_cache_is_miss(tmp_path: Path) -> None:
    cache = AnalysisCache(tmp_path)
    cache.put(CacheEntry(assets_hash="h1", feature_ids=[]))
    # 파일을 손상시킴 → 미스로 간주 (Q4=A)
    (tmp_path / ".trace/cache/h1.json").write_text("{ not json", encoding="utf-8")
    assert cache.get("h1") is None

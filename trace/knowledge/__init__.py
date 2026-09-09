"""C4 지식 계층 — 저장소·캐시·id 유틸 (UOW-02)."""

from trace.knowledge.cache import AnalysisCache, CacheEntry, compute_assets_hash
from trace.knowledge.ids import safe_feature_id
from trace.knowledge.store import KnowledgeStore

__all__ = [
    "KnowledgeStore",
    "AnalysisCache",
    "CacheEntry",
    "compute_assets_hash",
    "safe_feature_id",
]

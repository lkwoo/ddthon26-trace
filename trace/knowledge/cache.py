"""분석 캐시 — 콘텐츠 해시 기반 (UOW-02, NFR Design P5, BR-CACHE, Q4=A).

키 = 자산 집합의 콘텐츠 해시(정렬된 rel_path:size:sha256(content)). 순서 무관·내용 민감.
저장 위치 <project_root>/.trace/cache/<hash>.json. 손상/스키마 불일치는 '미스'로 간주(재분석).
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from pydantic import BaseModel, Field, ValidationError

from trace.common.logging import get_logger
from trace.models.asset import Asset

_log = get_logger("trace.knowledge.cache")


def compute_assets_hash(assets: list[Asset]) -> str:
    """자산 집합의 결정적 콘텐츠 해시 (순서 무관, PBT-02-B)."""
    lines = sorted(
        f"{a.rel_path}:{a.size_bytes}:{hashlib.sha256((a.content or '').encode('utf-8')).hexdigest()}"
        for a in assets
    )
    digest = hashlib.sha256("\n".join(lines).encode("utf-8")).hexdigest()
    return digest


class CacheEntry(BaseModel):
    assets_hash: str = Field(..., min_length=1)
    feature_ids: list[str] = Field(default_factory=list)
    meta: dict = Field(default_factory=dict)


class AnalysisCache:
    """<project_root>/.trace/cache 하위 JSON 캐시."""

    def __init__(self, project_root: str | Path, cache_dir: str = ".trace/cache") -> None:
        self._dir = Path(project_root) / cache_dir

    def _path(self, assets_hash: str) -> Path:
        return self._dir / f"{assets_hash}.json"

    def get(self, assets_hash: str) -> CacheEntry | None:
        """캐시 조회. 미존재/손상/스키마 불일치는 None(미스)."""
        path = self._path(assets_hash)
        if not path.exists():
            return None
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            entry = CacheEntry.model_validate(raw)
        except (OSError, json.JSONDecodeError, ValidationError) as exc:
            _log.debug(f"event=cache_miss_corrupt error_type={type(exc).__name__}")
            return None
        if entry.assets_hash != assets_hash:
            return None
        return entry

    def put(self, entry: CacheEntry) -> None:
        """캐시 기록 (디렉터리 자동 생성)."""
        self._dir.mkdir(parents=True, exist_ok=True)
        path = self._path(entry.assets_hash)
        path.write_text(
            json.dumps(entry.model_dump(), ensure_ascii=False, sort_keys=True, indent=2),
            encoding="utf-8",
        )


__all__ = ["compute_assets_hash", "CacheEntry", "AnalysisCache"]

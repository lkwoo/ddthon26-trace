"""overview.md 영속화 — 온보딩 맵의 MD+YAML 단일 진실원 (UOW-07, FR-MAP-006).

대상 프로젝트의 `.trace/knowledge/overview.md`에 저장한다(`KnowledgeStore` base 재사용).
구조화 값(진입점·엣지·Feature 매핑·mermaid)은 YAML front matter에 두어 무손실 왕복(P3)을
보장하고, 사람이 읽는 내러티브 + 임베드 Mermaid는 Markdown 본문으로 렌더한다.
시크릿은 저장 전 `mask_secrets`로 마스킹한다(규칙 7, NFR-SEC-005).
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from traceki.common import KnowledgeNotFoundError, get_logger, mask_secrets
from traceki.knowledge import KnowledgeStore, default_store
from traceki.map.models import OnboardingMap

_log = get_logger("trace.map.overview")

_FRONT_MATTER = re.compile(r"^---\n(.*?)\n---\n?(.*)$", re.DOTALL)


def _overview_path(store: KnowledgeStore) -> Path:
    """`<base>/.trace/knowledge/overview.md`. KnowledgeStore의 features_dir 부모."""
    return store.features_dir.parent / "overview.md"


def overview_exists(store: KnowledgeStore | None = None) -> bool:
    store = store or default_store()
    return _overview_path(store).is_file()


def _render_markdown(omap: OnboardingMap) -> str:
    front = yaml.safe_dump(omap.to_dict(), allow_unicode=True, sort_keys=False, default_flow_style=False)
    lines = [f"---\n{front}---\n", "# 프로젝트 온보딩 맵\n"]
    if omap.narrative:
        lines.append(f"{omap.narrative}\n")
    if omap.entry_points:
        lines.append("## 진입점\n")
        lines.extend(f"- **{e.symbol}** (`{e.file}`) — {e.kind}: {e.reason}" for e in omap.entry_points)
        lines.append("")
    if omap.mermaid.get("dependency"):
        lines.append("## 의존 관계\n")
        lines.append("```mermaid\n" + omap.mermaid["dependency"] + "\n```\n")
    if omap.mermaid.get("sequence"):
        lines.append("## 핵심 흐름\n")
        lines.append("```mermaid\n" + omap.mermaid["sequence"] + "\n```\n")
    if omap.feature_file_maps:
        lines.append("## Feature → 파일\n")
        for m in omap.feature_file_maps:
            files = ", ".join(f"`{f['path']}`" for f in m.files) or "(없음)"
            lines.append(f"- **{m.title}** (`{m.feature_id}`): {files}")
        lines.append("")
    if omap.warnings:
        lines.append("## ⚠️ 경고\n")
        lines.extend(f"- {w}" for w in omap.warnings)
        lines.append("")
    return mask_secrets("\n".join(lines).rstrip() + "\n")


def save_overview(omap: OnboardingMap, store: KnowledgeStore | None = None) -> str:
    """온보딩 맵을 overview.md로 저장하고 경로를 반환한다."""
    store = store or default_store()
    path = _overview_path(store)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(_render_markdown(omap), encoding="utf-8")
    _log.info("온보딩 맵 저장: %s", path)
    return str(path)


def load_overview(store: KnowledgeStore | None = None) -> OnboardingMap:
    """저장된 overview.md를 OnboardingMap으로 복원한다(캐시 재사용, 왕복 P3)."""
    store = store or default_store()
    path = _overview_path(store)
    if not path.is_file():
        raise KnowledgeNotFoundError("저장된 온보딩 맵(overview.md)이 없습니다. refresh=True로 생성하세요.")
    m = _FRONT_MATTER.match(path.read_text(encoding="utf-8"))
    if not m:
        raise KnowledgeNotFoundError("overview.md 형식이 올바르지 않습니다 (YAML front matter 없음).")
    data: dict[str, Any] = yaml.safe_load(m.group(1)) or {}
    return OnboardingMap.from_dict(data)


def overview_path(store: KnowledgeStore | None = None) -> str:
    return str(_overview_path(store or default_store()))


__all__ = ["save_overview", "load_overview", "overview_exists", "overview_path"]

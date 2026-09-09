"""자산 카탈로그 빌더 (UOW-02, NFR Design P1, BR-IDF-002, PBT-02-C).

LLM 입력용으로 자산을 {rel_path, asset_type, excerpt}로 투영한다.
content 있는 자산만 포함, 발췌는 상한(기본 4,000자)으로 절단(토큰 예산).
"""

from __future__ import annotations

from dataclasses import dataclass

from trace.models.asset import Asset, ParseStatus

_DEFAULT_EXCERPT_CHARS = 4000


@dataclass
class CatalogEntry:
    rel_path: str
    asset_type: str
    excerpt: str


def build_catalog(assets: list[Asset], *, excerpt_chars: int = _DEFAULT_EXCERPT_CHARS) -> list[CatalogEntry]:
    """content 있는 자산만 카탈로그 항목으로 (rel_path 정렬, 발췌 상한)."""
    entries: list[CatalogEntry] = []
    for a in assets:
        if a.content is None or a.parse_status in (ParseStatus.SKIPPED, ParseStatus.FAILED):
            continue
        excerpt = a.content[:excerpt_chars]
        entries.append(CatalogEntry(rel_path=a.rel_path, asset_type=a.asset_type.value, excerpt=excerpt))
    entries.sort(key=lambda e: e.rel_path)
    return entries


def render_catalog(entries: list[CatalogEntry]) -> str:
    """카탈로그를 프롬프트 삽입용 텍스트로 렌더."""
    blocks: list[str] = []
    for e in entries:
        blocks.append(
            f"### {e.rel_path}  [{e.asset_type}]\n{e.excerpt}".rstrip()
        )
    return "\n\n".join(blocks) if blocks else "(빈 프로젝트: 분석할 자산 없음)"


__all__ = ["CatalogEntry", "build_catalog", "render_catalog"]

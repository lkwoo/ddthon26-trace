"""C3 AI 워크플로우 — 구조화 출력 LLM step (UOW-02 부분).

UOW-02 담당 step:
- `identify_features`      : 자산에서 Feature 자동 검출 (FR-KNOWLEDGE-001)
- `generate_feature_knowledge`: Feature별 서술 지식 생성 (FR-KNOWLEDGE-002)

UOW-03이 `extract_claims`/`group_evidence`/`assign_confidence`를 이 모듈에 추가한다.

각 step은 `LLMService.structured(step_key, prompt)`로 파싱된 JSON을 받는다. replay 백엔드는
`step_key`로 사전 응답을 재생하고, live 백엔드는 `prompts.get_prompt(...)`로 렌더한 프롬프트를 쓴다.
근거 그라운딩(NFR-AI-002)을 위해 프롬프트에 자산 발췌를 주입한다.
"""

from __future__ import annotations

from typing import Any

from trace.common import get_logger
from trace.engine.assets import Asset
from trace.knowledge import slugify
from trace.llm import LLMService
from trace.models import Feature, FeatureKnowledge
from trace.prompts import get_prompt

_log = get_logger("trace.workflow")

# 프롬프트에 넣을 자산당 최대 발췌 길이 (토큰·비용 방어)
_EXCERPT_CHARS = 2000


def render_assets(assets: list[Asset], limit: int = _EXCERPT_CHARS) -> str:
    """자산 목록을 프롬프트용 텍스트 블록으로 렌더 (경로·유형·발췌)."""
    blocks: list[str] = []
    for a in assets:
        excerpt = (a.content or "")[:limit]
        blocks.append(f"### {a.path} ({a.type})\n{excerpt}")
    return "\n\n".join(blocks)


def identify_features(assets: list[Asset], llm: LLMService) -> list[Feature]:
    """자산 집합에서 Feature 후보를 자동 검출한다 (FR-KNOWLEDGE-001).

    replay step_key: ``identify_features``.
    """
    prompt = get_prompt("identify_features", assets=render_assets(assets))
    raw = llm.structured("identify_features", prompt)
    features = _coerce_features(raw)
    _log.info("Feature 검출: %d개", len(features))
    return features


def generate_feature_knowledge(
    feature: Feature,
    assets: list[Asset],
    llm: LLMService,
    claims: list | None = None,
    conflicts: list | None = None,
) -> FeatureKnowledge:
    """Feature의 서술 지식(overview·business_rules·dependencies)을 생성한다.

    claims/conflicts는 UOW-03 파이프라인이 채워 넘긴다(UOW-02 단독 실행 시 빈 목록).
    replay step_key: ``generate_knowledge.<feature_id>``.
    """
    related = [a for a in assets if a.path in set(feature.related_sources)] or assets
    prompt = get_prompt(
        "generate_knowledge",
        feature_title=feature.title,
        feature_description=feature.description,
        assets=render_assets(related),
    )
    raw = llm.structured(f"generate_knowledge.{feature.id}", prompt)
    data = raw if isinstance(raw, dict) else {}
    from trace.models import Confidence

    return FeatureKnowledge(
        feature=feature,
        overview=str(data.get("overview", "")),
        business_rules=[str(r) for r in data.get("business_rules", [])],
        claims=list(claims or []),
        conflicts=list(conflicts or []),
        dependencies=[str(d) for d in data.get("dependencies", [])],
        confidence=Confidence.MEDIUM,
    )


# ------------------------------------------------------------------ 강제 변환
def _coerce_features(raw: Any) -> list[Feature]:
    """LLM 원시 출력을 Feature 목록으로 관대하게 변환한다."""
    items = raw.get("features") if isinstance(raw, dict) else raw
    if not isinstance(items, list):
        return []
    out: list[Feature] = []
    for i, item in enumerate(items):
        if not isinstance(item, dict) or not (item.get("title") or item.get("id")):
            continue
        title = str(item.get("title") or item.get("id"))
        fid = slugify(str(item.get("id") or title))
        out.append(
            Feature(
                id=fid,
                title=title,
                description=str(item.get("description", "")),
                related_sources=[str(s) for s in item.get("related_sources", [])],
            )
        )
    return out


__all__ = ["identify_features", "generate_feature_knowledge", "render_assets"]

"""Feature 식별 & 지식 셸 생성 (UOW-02, C3, NFR Design P2/P6, BR-IDF/KN/FAIL).

- identify_features: 카탈로그 → FeatureCandidateList (구조화·검증·재시도, 실패 시 warning 강등).
- generate_feature_knowledge: 지식 셸(body_markdown) 생성. claims/evidence/conflicts=[] (Q2=A, UOW-03 보강).
- build_knowledge: cache-first 오케스트레이션 + Feature별 실패 격리.
"""

from __future__ import annotations

from collections.abc import Sequence

from trace.common.errors import TraceError, sanitize_error
from trace.common.logging import get_logger
from trace.knowledge.cache import AnalysisCache, CacheEntry, compute_assets_hash
from trace.knowledge.ids import dedupe_ids, safe_feature_id
from trace.knowledge.store import KnowledgeStore
from trace.llm.service import LLMService
from trace.models.asset import Asset
from trace.models.domain import (
    Claim,
    ClaimConfidence,
    Conflict,
    Evidence,
    Feature,
    FeatureKnowledge,
)
from trace.models.feature_candidate import FeatureCandidateList, KnowledgeBody
from trace.models.result import FeatureSummary, Warning
from trace.prompts.loader import get_prompt
from trace.workflow.catalog import build_catalog, render_catalog

_log = get_logger("trace.workflow.features")


def identify_features(
    assets: list[Asset],
    llm: LLMService,
    *,
    max_features: int | None = None,
) -> tuple[list[Feature], list[Warning]]:
    """자산에서 Feature를 자동 식별한다 (실패 시 빈 목록 + warning, BR-FAIL-002)."""
    catalog = build_catalog(assets)
    prompt = get_prompt(
        "identify_features",
        catalog=render_catalog(catalog),
        max_features=str(max_features) if max_features else "제한 없음",
    )
    try:
        out = llm.complete_structured(prompt, FeatureCandidateList)
    except TraceError as exc:
        _log.warning("event=identify_failed")
        return [], [Warning(code="identify_failed",
                            message=f"Feature 식별 실패: {sanitize_error(exc)}",
                            source="catalog")]

    candidates = out.features
    if max_features is not None:
        candidates = candidates[:max_features]

    raw_ids = [safe_feature_id(c.id or c.title) for c in candidates]
    unique_ids = dedupe_ids(raw_ids)
    features: list[Feature] = []
    for c, fid in zip(candidates, unique_ids):
        features.append(Feature(
            id=fid,
            title=c.title,
            description=c.description or c.title,
            related_sources=list(c.related_sources),
        ))
    features.sort(key=lambda f: f.id)
    return features, []


def generate_feature_knowledge(
    feature: Feature,
    assets: list[Asset],
    llm: LLMService,
    *,
    claims: Sequence[Claim] = (),
    evidence: Sequence[Evidence] = (),
    confidence: Sequence[ClaimConfidence] = (),
    conflicts: Sequence[Conflict] = (),
) -> FeatureKnowledge:
    """Feature 지식 뷰(셸)를 생성한다. 본문 LLM 실패 시 템플릿 폴백 (BR-KN-002).

    claims/evidence/conflicts는 UOW-03이 채워 재호출할 수 있도록 인자로 받는다(기본 빈값).
    """
    related = [a for a in assets if a.rel_path in set(feature.related_sources)]
    sources_text = render_catalog(build_catalog(related)) if related else "(연결된 자산 없음)"
    warnings_meta: dict = {}
    try:
        prompt = get_prompt(
            "feature_knowledge",
            title=feature.title,
            description=feature.description,
            sources=sources_text,
        )
        body = llm.complete_structured(prompt, KnowledgeBody).markdown.strip()
        if not body:
            body = _fallback_body(feature)
            warnings_meta["knowledge_fallback"] = True
    except TraceError:
        _log.warning(f"event=knowledge_fallback id={feature.id}")
        body = _fallback_body(feature)
        warnings_meta["knowledge_fallback"] = True

    return FeatureKnowledge(
        feature=feature,
        claims=list(claims),
        evidence=list(evidence),
        confidence=list(confidence),
        conflicts=list(conflicts),
        body_markdown=body,
        meta={"sources": len(feature.related_sources), "stage": "knowledge-shell", **warnings_meta},
    )


def _fallback_body(feature: Feature) -> str:
    srcs = "\n".join(f"- {s}" for s in feature.related_sources) or "- (없음)"
    return (
        f"# {feature.title}\n\n{feature.description}\n\n"
        f"## 관련 자산\n{srcs}\n\n"
        f"> 상세 근거(Claim·Evidence·Conflict)는 분석 진행 중입니다."
    )


def build_knowledge(
    assets: list[Asset],
    llm: LLMService,
    store: KnowledgeStore,
    cache: AnalysisCache,
    *,
    max_features: int | None = None,
) -> tuple[list[FeatureSummary], list[Warning]]:
    """cache-first 지식 구축. 자산 불변 시 LLM 미호출(NFR-PERF-003, BR-CACHE-002)."""
    assets_hash = compute_assets_hash(assets)
    hit = cache.get(assets_hash)
    if hit is not None:
        _log.info("event=cache_hit")
        return store.list_feature_summaries(), []

    features, warnings = identify_features(assets, llm, max_features=max_features)
    saved_ids: list[str] = []
    for feature in features:  # Feature별 실패 격리 (BR-FAIL-001)
        try:
            fk = generate_feature_knowledge(feature, assets, llm)
            store.save_feature(fk)
            saved_ids.append(fk.feature.id)
        except Exception as exc:  # noqa: BLE001
            warnings.append(Warning(code="knowledge_failed",
                                    message=f"지식 생성 실패: {sanitize_error(exc)}",
                                    source=feature.id))

    cache.put(CacheEntry(assets_hash=assets_hash, feature_ids=saved_ids))
    return store.list_feature_summaries(), warnings


__all__ = ["identify_features", "generate_feature_knowledge", "build_knowledge"]

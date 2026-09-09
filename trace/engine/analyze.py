"""전체 분석 파이프라인 & 충돌 조회 (UOW-03, C2 공개, NFR Design P5/P6, BR-PIPE/OUT).

- analyze_project(path): validate→scan→build_knowledge(cache-first)→셸 완본화→충돌 집계→Result.
- get_conflicts(feature_id, path): 저장된 지식에서 충돌을 조회(FR-CONFLICT-OUT-001/002).

프로젝트 루트는 명시 인자 `path`로 받는다(기본 "."). MCP 어댑터(UOW-06)가 세션 루트를 주입한다.
"""

from __future__ import annotations

from trace.common.errors import PathValidationError, error_to_result, sanitize_error
from trace.common.logging import get_logger
from trace.config.settings import get_llm_settings
from trace.conflict.summarize import summarize_conflicts
from trace.engine.scan import scan_project_assets
from trace.knowledge.cache import AnalysisCache
from trace.knowledge.store import KnowledgeStore
from trace.llm.client import AnthropicClient
from trace.llm.service import LLMService
from trace.models.result import Result, Warning, build_result
from trace.workflow.claims import enrich_feature_knowledge
from trace.workflow.features import build_knowledge

_log = get_logger("trace.engine.analyze")


def _build_llm_service() -> LLMService:
    """실제 Anthropic 기반 LLMService 조립 (키는 호출 직전 late lookup)."""
    return LLMService(AnthropicClient(), get_llm_settings())


def analyze_project(path: str, *, llm: LLMService | None = None) -> Result:
    """프로젝트를 스캔·지식화·충돌검출해 완본 지식을 저장하고 Result를 반환한다 (Q5=A, BR-PIPE-001).

    자산 불변 재실행은 캐시 히트 + 완본 스테이지로 LLM을 호출하지 않는다(BR-PIPE-003).
    Feature별 완본화 실패는 warning으로 강등되고 전체는 계속된다(BR-PIPE-002).
    `llm`은 테스트 주입용(미지정 시 실제 클라이언트).
    """
    try:
        assets, warnings = scan_project_assets(path)
    except PathValidationError as exc:
        _log.info("event=analyze_path_invalid")
        return error_to_result(exc)

    service = llm or _build_llm_service()
    store = KnowledgeStore(path)
    cache = AnalysisCache(path)

    summaries, wk = build_knowledge(assets, service, store, cache)
    warnings = list(warnings) + list(wk)

    all_conflicts = []
    complete_ids: list[str] = []
    for summary in summaries:
        try:
            fk = store.load_feature(summary.id)
        except Exception as exc:  # noqa: BLE001 — 손상/누락 격리 (NFR-03-REL-4)
            warnings.append(Warning(code="feature_load_failed",
                                    message=f"지식 로드 실패: {sanitize_error(exc)}",
                                    source=summary.id))
            continue

        if fk.meta.get("stage") != "complete":
            try:
                fk, we = enrich_feature_knowledge(fk, assets, service)
                store.save_feature(fk)
                warnings.extend(we)
            except Exception as exc:  # noqa: BLE001 — Feature 격리 (BR-PIPE-002)
                _log.warning(f"event=enrich_failed id={summary.id}")
                warnings.append(Warning(code="enrich_failed",
                                        message=f"완본화 실패: {sanitize_error(exc)}",
                                        source=summary.id))
        complete_ids.append(fk.feature.id)
        all_conflicts.extend(fk.conflicts)

    conflicts_out = summarize_conflicts(all_conflicts)
    features_data = [
        {"id": s.id, "title": s.title, "conflicts_count": s.conflicts_count}
        for s in store.list_feature_summaries()
    ]
    summary_text = (
        f"{len(features_data)}개 Feature 분석 완료 "
        f"(자산 {len(assets)}개, 충돌 {len(conflicts_out)}건)"
    )
    return build_result(
        summary_text,
        data={
            "features": features_data,
            "assets_count": len(assets),
            "conflicts_count": len(conflicts_out),
        },
        conflicts=conflicts_out,
        warnings=warnings,
    )


def get_conflicts(feature_id: str | None = None, *, path: str = ".") -> Result:
    """저장된 지식에서 충돌을 조회한다 (FR-CONFLICT-OUT-001/002, BR-OUT).

    feature_id 지정 시 해당 Feature만, 미지정 시 전체 Feature 합산.
    손상 파일은 skip + warning(목록 계속, NFR-03-REL-4).
    """
    store = KnowledgeStore(path)
    warnings: list[Warning] = []
    conflicts = []

    if feature_id is not None:
        try:
            fk = store.load_feature(feature_id)
            conflicts.extend(fk.conflicts)
        except Exception as exc:  # noqa: BLE001
            return build_result(
                f"Feature '{feature_id}' 지식을 찾을 수 없습니다.",
                warnings=[Warning(code="feature_not_found",
                                  message=sanitize_error(exc), source=feature_id)],
                meta={"conflicts_count": 0},
            )
    else:
        for summary in store.list_feature_summaries():
            try:
                fk = store.load_feature(summary.id)
            except Exception as exc:  # noqa: BLE001
                warnings.append(Warning(code="feature_load_skip",
                                        message="지식 로드 skip", source=summary.id))
                continue
            conflicts.extend(fk.conflicts)

    conflicts_out = summarize_conflicts(conflicts)
    scope = feature_id or "전체"
    summary_text = f"{scope} 충돌 {len(conflicts_out)}건"
    return build_result(
        summary_text,
        conflicts=conflicts_out,
        warnings=warnings,
        meta={"conflicts_count": len(conflicts_out)},
    )


__all__ = ["analyze_project", "get_conflicts"]

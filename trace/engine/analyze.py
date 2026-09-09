"""전체 분석 파이프라인 & 충돌 조회 (UOW-03, C2 공개, NFR Design P5/P6, BR-PIPE/OUT).

- analyze_project(path): validate→scan→build_knowledge(cache-first)→셸 완본화→충돌 집계→Result.
- get_conflicts(feature_id, path): 저장된 지식에서 충돌을 조회(FR-CONFLICT-OUT-001/002).

프로젝트 루트는 명시 인자 `path`로 받는다(기본 "."). MCP 어댑터(UOW-06)가 세션 루트를 주입한다.
"""

from __future__ import annotations

from trace.common.errors import PathValidationError, error_to_result, sanitize_error
from trace.common.logging import get_logger
from trace.config.settings import get_llm_settings
from trace.common.errors import TraceError
from trace.conflict.summarize import summarize_conflicts
from trace.engine.scan import scan_project_assets
from trace.impact.analyze import analyze_task, to_impact_out
from trace.impact.context import build_context
from trace.knowledge.cache import AnalysisCache
from trace.knowledge.store import KnowledgeStore
from trace.llm.client import AnthropicClient
from trace.llm.service import LLMService
from trace.models.result import ImpactOut, Result, Warning, build_result
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


def list_features(*, path: str = ".") -> Result:
    """저장된 Feature 요약 목록을 반환한다 (FR-KNOWLEDGE-OUT, UOW-05 코어 래퍼)."""
    try:
        summaries = KnowledgeStore(path).list_feature_summaries()
    except Exception as exc:  # noqa: BLE001
        return error_to_result(exc)
    return build_result(
        f"Feature {len(summaries)}개",
        data={"features": [s.model_dump() for s in summaries]},
        meta={"features_count": len(summaries)},
    )


def get_feature_knowledge(feature_id: str, *, path: str = ".") -> Result:
    """한 Feature의 지식(구조화 필드)을 반환한다. 본문은 리소스로 조회 (UOW-05 코어 래퍼)."""
    try:
        fk = KnowledgeStore(path).load_feature(feature_id)
    except Exception as exc:  # noqa: BLE001 — 부재/손상은 오류 Result
        return error_to_result(exc)
    return build_result(
        f"{fk.feature.title} — claims {len(fk.claims)}, conflicts {len(fk.conflicts)}",
        data={
            "feature": fk.feature.model_dump(),
            "claims": [c.model_dump() for c in fk.claims],
            "confidence": [c.model_dump() for c in fk.confidence],
            "resource_uri": f"trace://feature/{fk.feature.id}",
        },
        conflicts=summarize_conflicts(fk.conflicts),
        meta={"conflicts_count": len(fk.conflicts)},
    )


def analyze_task_impact(
    task: str,
    feature_id: str | None = None,
    *,
    path: str = ".",
    llm: LLMService | None = None,
) -> Result:
    """자연어 작업의 영향을 저장 지식에 그라운딩해 분석한다 (FR-IMPACT-001~006, BR-PIPE).

    Must/Likely/Review 분류(+근거)·관련 기존 충돌 경고(P1)·순서형 Change Plan을 반환한다.
    **소스 코드를 자동 수정하지 않는다**(자문용, BR-PLAN-002 — 파일 쓰기 없음).
    지식 부재·LLM 실패는 warning으로 강등한다(예외 전파 없음).
    """
    store = KnowledgeStore(path)
    ctx, warnings = build_context(task, feature_id, store)

    if not ctx.focus:  # 저장 지식 없음 (BR-PIPE-003)
        return build_result(
            "분석할 지식이 없습니다. 먼저 analyze_project를 실행하세요.",
            data={"feature_scope": feature_id or "전체", "candidates_count": 0},
            warnings=[Warning(code="no_knowledge",
                              message="저장된 지식이 없습니다(analyze_project 필요)",
                              source=feature_id or "project")],
            meta={"confidence": "LOW"},
        )

    service = llm or _build_llm_service()
    try:
        result = analyze_task(ctx, service)
        impact = to_impact_out(result, ctx)
    except TraceError as exc:  # LLM 실패 강등 (BR-PIPE-002) — 충돌은 그래도 노출
        _log.warning("event=task_analysis_failed")
        warnings.append(Warning(code="task_analysis_failed",
                                message=f"작업 영향 분석 실패: {sanitize_error(exc)}",
                                source=feature_id or "task"))
        impact = ImpactOut(related_conflicts=summarize_conflicts(ctx.conflicts))

    candidates_count = len(impact.must_change) + len(impact.likely_change) + len(impact.review)
    low = any(
        not it.evidence
        for bucket in (impact.must_change, impact.likely_change, impact.review)
        for it in bucket
    )
    summary_text = (
        f"영향 후보 {candidates_count}건 "
        f"(must {len(impact.must_change)} / likely {len(impact.likely_change)} / review {len(impact.review)}), "
        f"관련 충돌 {len(impact.related_conflicts)}건"
    )
    return build_result(
        summary_text,
        data={"feature_scope": feature_id or "전체", "candidates_count": candidates_count},
        impact=impact,
        conflicts=impact.related_conflicts,
        warnings=warnings,
        meta={"confidence": "LOW" if (low or warnings) else "MEDIUM"},
    )


__all__ = [
    "analyze_project", "get_conflicts", "analyze_task_impact",
    "list_features", "get_feature_knowledge",
]

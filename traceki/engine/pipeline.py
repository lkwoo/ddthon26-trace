"""분석 오케스트레이션 (UOW-02, C2) — analyze_project 파이프라인 + 지식 조회.

`analyze_project`는 코어 파이프라인을 배선한다: 스캔·파싱(UOW-01) → Feature 검출·지식 생성(UOW-02)
→ 영속화(C4). Claim/Evidence 추출과 충돌 검출(UOW-03)은 `enrich` 훅으로 주입되어, UOW-03이
파이프라인 본문을 수정하지 않고 확장할 수 있다(개방-폐쇄).

부분 실패는 전체를 중단하지 않고 warning으로 누적한다(FR-ANALYSIS-003). 이미 분석된 지식이 있으면
`refresh=False`에서 재사용한다(NFR-PERF-003 캐시, Q5=A).
"""

from __future__ import annotations

from typing import Callable

from traceki.common import KnowledgeNotFoundError, LLMError, Result, get_logger
from traceki.config import Config
from traceki.engine.assets import Asset
from traceki.engine.scanner import collect_assets
from traceki.knowledge import KnowledgeStore, default_store
from traceki.llm import LLMService
from traceki.models import Feature, FeatureKnowledge
from traceki.workflow import generate_feature_knowledge, identify_features

_log = get_logger("trace.engine.pipeline")

# UOW-03이 등록하는 지식 보강 훅: (feature, assets, llm, fk) -> (fk, conflicts_count)
EnrichHook = Callable[[Feature, "list[Asset]", LLMService, FeatureKnowledge], int]
_enrich_hook: EnrichHook | None = None


def register_enrich_hook(hook: EnrichHook | None) -> None:
    """UOW-03 Claim/Conflict 보강 훅을 등록한다(파이프라인 확장점)."""
    global _enrich_hook
    _enrich_hook = hook


def _resolve_store(store: KnowledgeStore | None) -> KnowledgeStore:
    return store or default_store()


def analyze_project(
    path: str,
    config: Config | None = None,
    store: KnowledgeStore | None = None,
    refresh: bool = False,
) -> Result:
    """전체 분석 파이프라인 (FR-KNOWLEDGE-001/002/003).

    data: {project_name, features:[summary], conflicts_count, assets_count}.
    """
    config = config or Config()
    store = _resolve_store(store)

    # UOW-03 충돌 보강 훅을 소프트 활성화 (있으면 등록, 없어도 UOW-02 단독 동작)
    if _enrich_hook is None:
        try:
            import traceki.conflict  # noqa: F401 — import 시 register_enrich_hook 호출
        except ImportError:
            pass

    # 캐시 재사용 (NFR-PERF-003)
    if not refresh:
        cached = store.list_feature_summaries()
        if cached:
            conflicts_count = sum(f["conflicts"] for f in cached)
            r = Result.ok(
                f"캐시된 분석 재사용: Feature {len(cached)}개, 충돌 {conflicts_count}건 "
                f"(refresh=True로 재분석 가능)",
                data={"features": cached, "conflicts_count": conflicts_count, "cached": True},
                meta={"features_count": len(cached), "cached": True},
            )
            return r

    try:
        assets, warnings = collect_assets(path, config)
    except Exception as exc:  # noqa: BLE001 — 경로 검증 등은 사용자 친화 오류로 변환
        return Result.error(f"프로젝트 스캔 실패: {exc}")

    if not assets:
        return Result.error(f"분석할 자산을 찾지 못했습니다: {path}")

    llm = LLMService(config.llm)
    warn_all = list(warnings)

    try:
        features = identify_features(assets, llm)
    except LLMError as exc:
        return Result.error(f"Feature 검출 실패: {exc}")

    summaries: list[dict] = []
    conflicts_total = 0
    for feature in features:
        try:
            fk = generate_feature_knowledge(feature, assets, llm)
        except LLMError as exc:
            warn_all.append(f"'{feature.title}' 지식 생성 실패: {exc}")
            _log.warning("지식 생성 실패 %s: %s", feature.id, exc)
            continue

        # UOW-03 보강(Claim/Evidence/Conflict) — 등록돼 있으면 실행
        if _enrich_hook is not None:
            try:
                conflicts_total += _enrich_hook(feature, assets, llm, fk)
            except LLMError as exc:
                warn_all.append(f"'{feature.title}' 충돌 분석 실패: {exc}")
                _log.warning("보강 실패 %s: %s", feature.id, exc)

        store.save_feature(fk)
        summaries.append(
            {
                "id": fk.feature.id,
                "title": fk.feature.title,
                "confidence": fk.confidence.value,
                "conflicts": len(fk.conflicts),
                "related_sources": list(fk.feature.related_sources),
            }
        )

    summary = (
        f"'{path}' 분석 완료: Feature {len(summaries)}개, "
        f"충돌 {conflicts_total}건, 자산 {len(assets)}개"
    )
    result = Result.ok(
        summary,
        data={
            "features": summaries,
            "conflicts_count": conflicts_total,
            "assets_count": len(assets),
            "cached": False,
        },
        meta={"features_count": len(summaries), "assets_count": len(assets)},
    )
    result.warnings.extend(warn_all)
    return result


def list_features(store: KnowledgeStore | None = None) -> Result:
    """검출된 Feature 요약 목록 (FR-KNOWLEDGE-002)."""
    store = _resolve_store(store)
    summaries = store.list_feature_summaries()
    if not summaries:
        return Result.ok(
            "아직 분석된 Feature가 없습니다. 먼저 analyze_project를 실행하세요.",
            data={"features": []},
        )
    return Result.ok(
        f"Feature {len(summaries)}개",
        data={"features": summaries},
        meta={"features_count": len(summaries)},
    )


def get_feature_knowledge(feature_id: str, store: KnowledgeStore | None = None) -> Result:
    """단일 Feature 지식 상세 (FR-KNOWLEDGE-002)."""
    store = _resolve_store(store)
    try:
        fk = store.load_feature(feature_id)
    except KnowledgeNotFoundError as exc:
        return Result.error(str(exc))

    body = store.read_resource(feature_id)
    # 본문(front matter 제외) 발췌를 summary로
    marker = "\n---\n"
    body_text = body.split(marker, 1)[-1].strip() if marker in body else body
    return Result.ok(
        body_text[:600] or fk.feature.title,
        data=fk.to_dict(),
        conflicts=[c.to_dict() for c in fk.conflicts],
        evidence=[e.to_dict() for e in fk.all_evidence],
        meta={
            "feature_id": fk.feature.id,
            "confidence": fk.confidence.value,
            "resource_path": store.resource_path(feature_id),
        },
    )


__all__ = [
    "analyze_project",
    "list_features",
    "get_feature_knowledge",
    "register_enrich_hook",
    "EnrichHook",
]

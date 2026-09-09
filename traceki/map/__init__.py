"""C10 프로젝트 온보딩 맵 — generate_onboarding_map 코어 함수 (UOW-07).

신입 개발자가 낯선 프로젝트의 전체 흐름·파일 관계·함수 관계를 온보딩 관점에서 파악하도록 돕는다
(FR-MAP-001~007, US-07.1~5). 정적 추출(사실) + LLM 서술(근거·흐름)을 하이브리드로 병합하고
(규칙 1), Mermaid로 시각화해 `.trace/knowledge/overview.md`에 영속화한다.

설계 원칙(NFR-CORE-001): 이 코어 함수는 C2 엔진 오케스트레이션이며, 어댑터(C1 MCP·C9 CLI)는
이 함수만 호출한다. 기존 모델·서비스(Asset·Evidence·Feature·KnowledgeStore·LLMService·
get_prompt)를 재사용하고, 신규 코드는 이 패키지에 국한한다.
"""

from __future__ import annotations

from traceki.common import Result, get_logger
from traceki.config import Config
from traceki.engine.scanner import collect_assets
from traceki.knowledge import KnowledgeStore, default_store
from traceki.llm import LLMService
from traceki.map.describe import build_context, describe_relations
from traceki.map.mermaid import render_dependency_graph, render_sequence
from traceki.map.models import OnboardingMap
from traceki.map.overview import load_overview, overview_exists, overview_path, save_overview
from traceki.map.relations import extract_relations, find_entry_points, map_features_to_files

_log = get_logger("trace.map")


def _collect_evidence(entry_points, graph) -> list:
    """관계 근거(Evidence)를 수집한다 (FR-MAP-007). 진입점·엣지 근거를 상위 노출용으로 모은다."""
    ev = []
    for e in graph.dep_edges:
        if e.evidence:
            ev.append(e.evidence)
    for c in graph.call_edges:
        if c.evidence:
            ev.append(c.evidence)
    return ev


def generate_onboarding_map(
    path: str,
    feature_id: str | None = None,
    refresh: bool = False,
    config: Config | None = None,
    store: KnowledgeStore | None = None,
) -> Result:
    """프로젝트 온보딩 맵을 생성/조회한다 (코어 함수, FR-MAP-001).

    data: {entry_points, file_graph, feature_file_maps, call_relations, mermaid, overview_path}.
    summary: 온보딩 내러티브. evidence: 관계 근거. warnings: 부분 실패/저신뢰.
    """
    config = config or Config()
    store = store or default_store()

    # 캐시 재사용 (규칙 6, NFR-PERF-003)
    if not refresh and overview_exists(store):
        try:
            cached = load_overview(store)
            _log.info("캐시된 온보딩 맵 재사용: %s", overview_path(store))
            return _to_result(cached, store, cached=True)
        except Exception as exc:  # noqa: BLE001 — 손상 캐시는 재생성으로 폴백
            _log.warning("캐시 로드 실패, 재생성: %s", exc)

    # 자산 수집 (UOW-01 재사용, 경로 검증·제외 포함)
    try:
        assets, warnings = collect_assets(path, config)
    except Exception as exc:  # noqa: BLE001 — 경로 검증 등을 사용자 친화 오류로
        return Result.error(f"온보딩 맵 생성 실패(스캔): {exc}")
    if not assets:
        return Result.error(f"분석할 자산을 찾지 못했습니다: {path}")

    warn_all = list(warnings)

    # 정적 추출 (사실)
    graph = extract_relations(assets)
    entry_points = find_entry_points(assets)
    feature_maps = map_features_to_files(store)
    if not feature_maps:
        warn_all.append("저장된 Feature 지식이 없습니다. analyze_project 후 실행하면 Feature→파일 매핑이 포함됩니다.")
    if graph.unresolved:
        warn_all.append(f"정적 분석 불가 파일 {len(graph.unresolved)}개는 서술 추론에 위임했습니다(저신뢰 가능).")

    # LLM 서술 (근거·핵심 흐름). 실패해도 정적 맵은 유지(부분 실패, 규칙 4)
    described = {"narrative": "", "relation_notes": [], "key_flow": []}
    try:
        llm = LLMService(config.llm)
        described = describe_relations(build_context(entry_points, graph, feature_maps), llm)
    except Exception as exc:  # noqa: BLE001 — LLM/replay 실패는 warning으로 흡수
        warn_all.append(f"온보딩 서술 생성 실패(정적 맵만 제공): {exc}")
        _log.warning("describe_relations 실패: %s", exc)

    narrative = described.get("narrative") or _fallback_narrative(entry_points, graph, feature_maps)
    key_flow = described.get("key_flow", [])

    omap = OnboardingMap(
        entry_points=entry_points,
        file_graph=graph,
        feature_file_maps=feature_maps,
        call_relations=key_flow,
        narrative=narrative,
        mermaid={
            "dependency": render_dependency_graph(graph),
            "sequence": render_sequence(key_flow),
        },
        evidence=_collect_evidence(entry_points, graph),
        warnings=warn_all,
    )

    saved = save_overview(omap, store)
    _log.info(
        "온보딩 맵 생성: 진입점 %d, 노드 %d, 의존 %d, 호출 %d",
        len(entry_points), len(graph.nodes), len(graph.dep_edges), len(graph.call_edges),
    )
    return _to_result(omap, store, cached=False, overview_file=saved)


def _to_result(omap: OnboardingMap, store: KnowledgeStore, cached: bool, overview_file: str | None = None) -> Result:
    result = Result.ok(
        omap.narrative or "온보딩 맵을 생성했습니다.",
        data={
            "entry_points": [e.to_dict() for e in omap.entry_points],
            "file_graph": omap.file_graph.to_dict(),
            "feature_file_maps": [m.to_dict() for m in omap.feature_file_maps],
            "call_relations": list(omap.call_relations),
            "mermaid": dict(omap.mermaid),
            "overview_path": overview_file or overview_path(store),
            "cached": cached,
        },
        evidence=[e.to_dict() for e in omap.evidence],
        meta={
            "entry_points_count": len(omap.entry_points),
            "nodes_count": len(omap.file_graph.nodes),
            "dep_edges_count": len(omap.file_graph.dep_edges),
            "cached": cached,
        },
    )
    result.warnings.extend(omap.warnings)
    return result


def _fallback_narrative(entry_points, graph, feature_maps) -> str:
    """LLM 서술이 없을 때의 정적 요약 내러티브(부분 실패 대비)."""
    parts = [
        f"진입점 {len(entry_points)}개, 파일 {len(graph.nodes)}개, "
        f"의존 관계 {len(graph.dep_edges)}건, 호출 관계 {len(graph.call_edges)}건을 정적으로 확인했습니다."
    ]
    if feature_maps:
        parts.append("Feature: " + ", ".join(m.title for m in feature_maps) + ".")
    if entry_points:
        parts.append("주요 진입점: " + ", ".join(f"{e.symbol}({e.file})" for e in entry_points[:5]) + ".")
    return " ".join(parts)


__all__ = [
    "generate_onboarding_map",
    "extract_relations",
    "find_entry_points",
    "map_features_to_files",
    "describe_relations",
    "render_dependency_graph",
    "render_sequence",
    "save_overview",
    "load_overview",
    "OnboardingMap",
]

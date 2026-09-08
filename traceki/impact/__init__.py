"""C6 Task Impact — 착수 전 영향 범위 분석 (UOW-04).

개발자가 자연어로 "무엇을 하려는지"를 말하면, TRACE는 저장된 Feature 지식(Claim·근거·충돌)에
그라운딩해 **코드를 짜기 전에** 변경 파일을 Must/Likely/Review로 분류하고, 관련 충돌을 함께
경고하며, 순서형 Change Plan을 제시한다(FR-IMPACT-001/002). 소스를 자동 수정하지 않는다
(FR-IMPACT-003 — 제안만).
"""

from __future__ import annotations

from typing import Any

from traceki.common import Result, get_logger
from traceki.config import Config
from traceki.knowledge import KnowledgeStore, default_store, slugify
from traceki.llm import LLMService
from traceki.models import FeatureKnowledge
from traceki.workflow import analyze_task

_log = get_logger("trace.impact")


def _build_context(features: list[FeatureKnowledge]) -> str:
    """Feature 지식을 프롬프트용 그라운딩 컨텍스트로 렌더한다."""
    blocks: list[str] = []
    for fk in features:
        lines = [f"## Feature: {fk.feature.title} (id={fk.feature.id})"]
        if fk.overview:
            lines.append(fk.overview)
        if fk.feature.related_sources:
            lines.append("Sources: " + ", ".join(fk.feature.related_sources))
        for c in fk.claims:
            srcs = ", ".join(e.source for e in c.evidence) or "(no evidence)"
            lines.append(f"- CLAIM {c.key} = {c.value} [{srcs}]")
        for cf in fk.conflicts:
            vals = "; ".join(f"{v.value}({v.source})" for v in cf.values)
            lines.append(f"- CONFLICT {cf.claim}: {vals}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _norm_items(raw: Any) -> list[dict]:
    """LLM 영향 항목을 {path, reason, evidence}로 정규화한다."""
    out: list[dict] = []
    if not isinstance(raw, list):
        return out
    for item in raw:
        if isinstance(item, dict) and item.get("path"):
            out.append(
                {
                    "path": str(item["path"]),
                    "reason": str(item.get("reason", "")),
                    "evidence": [str(e) for e in item.get("evidence", [])],
                }
            )
        elif isinstance(item, str):
            out.append({"path": item, "reason": "", "evidence": []})
    return out


def _gather_features(
    store: KnowledgeStore, feature_id: str | None
) -> list[FeatureKnowledge]:
    if feature_id:
        try:
            return [store.load_feature(feature_id)]
        except Exception:  # noqa: BLE001
            return []
    features: list[FeatureKnowledge] = []
    for summ in store.list_feature_summaries():
        try:
            features.append(store.load_feature(summ["id"]))
        except Exception:  # noqa: BLE001
            continue
    return features


def analyze_task_impact(
    task: str,
    feature_id: str | None = None,
    store: KnowledgeStore | None = None,
    config: Config | None = None,
) -> Result:
    """자연어 작업의 영향 범위를 분석한다 (코어 함수, FR-IMPACT-001).

    impact: {must_change, likely_change, review, change_plan, related_conflicts}.
    관련 충돌은 conflicts로도 상위 노출하고 경고를 남긴다.
    """
    if not task or not task.strip():
        return Result.error("분석할 작업 설명이 비어 있습니다.")

    store = store or default_store()
    config = config or Config()
    features = _gather_features(store, feature_id)
    if not features:
        return Result.error(
            "분석된 지식이 없습니다. 먼저 analyze_project를 실행한 뒤 작업 영향을 분석하세요."
        )

    context = _build_context(features)
    llm = LLMService(config.llm)
    task_id = slugify(task)

    try:
        raw = analyze_task(task, task_id, context, llm)
    except Exception as exc:  # noqa: BLE001 — LLM/replay 실패는 사용자 친화 오류로
        return Result.error(f"작업 영향 분석 실패: {exc}")

    must = _norm_items(raw.get("must_change"))
    likely = _norm_items(raw.get("likely_change"))
    review = _norm_items(raw.get("review"))
    change_plan = [str(s) for s in raw.get("change_plan", [])]

    # 지식에 이미 있는 충돌을 작업과 함께 경고 (충돌 인지)
    all_conflicts: list[dict] = []
    for fk in features:
        for cf in fk.conflicts:
            d = cf.to_dict()
            d["feature_id"] = fk.feature.id
            all_conflicts.append(d)

    related_keys = set(raw.get("related_conflicts", []))
    related = [c for c in all_conflicts if c["claim"] in related_keys] or all_conflicts

    impact = {
        "task": task,
        "must_change": must,
        "likely_change": likely,
        "review": review,
        "change_plan": change_plan,
        "related_conflicts": related,
    }

    summary = (
        f"'{task}' 영향 분석: 반드시 변경 {len(must)}개, 변경 가능 {len(likely)}개, "
        f"검토 {len(review)}개, 계획 {len(change_plan)}단계"
    )
    result = Result.ok(
        summary,
        data={"feature_scope": feature_id or "all"},
        impact=impact,
        conflicts=related,
        meta={
            "must_count": len(must),
            "likely_count": len(likely),
            "review_count": len(review),
            "conflicts_count": len(related),
        },
    )
    if related:
        result.add_warning(
            f"관련 충돌 {len(related)}건이 있습니다. 착수 전 값 불일치를 먼저 확인하세요."
        )
    _log.info("작업 영향 분석 %s: must=%d likely=%d review=%d", task_id, len(must), len(likely), len(review))
    return result


__all__ = ["analyze_task_impact"]

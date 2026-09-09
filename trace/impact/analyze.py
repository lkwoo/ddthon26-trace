"""영향 분석 LLM step & 매핑 (UOW-04, C6, NFR Design P2/P3/P4, BR-IMP/CONFWARN/PLAN).

- analyze_task: 그라운딩 컨텍스트로 1회 구조화 호출(FR-IMPACT-002). 실패는 상위에서 강등(raise).
- to_impact_out: **순수 함수** — 허구 path·근거부족 review 강등, 카테고리별 정렬, 충돌 독립 노출.
"""

from __future__ import annotations

from trace.conflict.summarize import summarize_conflicts
from trace.impact.context import KnowledgeContext
from trace.llm.service import LLMService
from trace.models.domain import FeatureKnowledge, ImpactCategory
from trace.models.impact import TaskImpactResult
from trace.models.result import FeatureSummary, ImpactItem, ImpactOut
from trace.prompts.loader import get_prompt

_EXCERPT_CHARS = 4000  # UOW-02/03 상속 (NFR-04-COST-2)
_INSUFFICIENT = "Insufficient evidence"


def _render_summaries(summaries: list[FeatureSummary]) -> str:
    if not summaries:
        return "(저장된 지식 없음)"
    return "\n".join(
        f"- {s.id}: {s.title} (충돌 {s.conflicts_count}건, confidence {s.confidence or 'N/A'})"
        for s in summaries
    )


def _render_focus(focus: list[FeatureKnowledge]) -> str:
    if not focus:
        return "(상세 지식 없음)"
    blocks: list[str] = []
    for fk in focus:
        claims = "\n".join(f"    - {c.subject}.{c.predicate} = {c.value}" for c in fk.claims) or "    - (없음)"
        evid = "\n".join(
            f"    - {e.source} @ {e.location}: {e.extracted_value or ''} ({e.relation.value})"
            for e in fk.evidence
        ) or "    - (없음)"
        conf = "\n".join(f"    - {c.claim} ({c.type.value})" for c in fk.conflicts) or "    - (없음)"
        blocks.append(
            f"### {fk.feature.id} — {fk.feature.title}\n"
            f"{fk.body_markdown[:_EXCERPT_CHARS]}\n"
            f"  Claims:\n{claims}\n  Evidence:\n{evid}\n  기존 충돌:\n{conf}"
        )
    return "\n\n".join(blocks)


def analyze_task(ctx: KnowledgeContext, llm: LLMService) -> TaskImpactResult:
    """그라운딩 컨텍스트로 영향 후보·Change Plan을 1회 구조화 호출로 산출한다 (FR-IMPACT-002).

    검증 소진 시 LLMValidationError(TraceError)를 raise — 상위 analyze_task_impact가 warning 강등.
    """
    prompt = get_prompt(
        "analyze_task",
        task=ctx.task,
        features=_render_summaries(ctx.features),
        knowledge=_render_focus(ctx.focus),
        known_sources="\n".join(f"- {s}" for s in sorted(ctx.known_sources)) or "(없음)",
    )
    return llm.complete_structured(prompt, TaskImpactResult)


def to_impact_out(result: TaskImpactResult, ctx: KnowledgeContext) -> ImpactOut:
    """LLM 결과를 ImpactOut로 매핑한다 (순수·결정적, BR-IMP-003/004/005, BR-CONFWARN).

    - 허구 path(known_sources 밖) → review 강등(환각 억제, PBT-04-A).
    - 근거 부족(evidence 없음) → review + Insufficient evidence(NFR-AI-003, PBT-04-B).
    - 카테고리별 path 안정 정렬(PBT-04-C).
    """
    buckets: dict[ImpactCategory, list[ImpactItem]] = {
        ImpactCategory.MUST_CHANGE: [],
        ImpactCategory.LIKELY_CHANGE: [],
        ImpactCategory.REVIEW: [],
    }
    for c in result.candidates:
        cat = c.category
        reason = c.reason
        if c.path not in ctx.known_sources:
            cat = ImpactCategory.REVIEW
            reason = f"[근거 밖 추정] {reason}"
        if not c.evidence:
            cat = ImpactCategory.REVIEW
            if _INSUFFICIENT not in reason:
                reason = f"{reason} ({_INSUFFICIENT})"
        buckets[cat].append(ImpactItem(path=c.path, reason=reason, evidence=list(c.evidence)))

    # 완전 결정적 정렬: path 동률 시 reason·근거로 tie-break (입력 순서 무관, PBT-04-C)
    for items in buckets.values():
        items.sort(key=lambda it: (it.path, it.reason,
                                   tuple((e.source, e.location, e.relation) for e in it.evidence)))

    return ImpactOut(
        must_change=buckets[ImpactCategory.MUST_CHANGE],
        likely_change=buckets[ImpactCategory.LIKELY_CHANGE],
        review=buckets[ImpactCategory.REVIEW],
        related_conflicts=summarize_conflicts(ctx.conflicts),   # LLM 독립(PBT-04-D, P4)
        change_plan=list(result.change_plan),
    )


__all__ = ["analyze_task", "to_impact_out"]

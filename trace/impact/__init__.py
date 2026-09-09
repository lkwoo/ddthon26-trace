"""C6 Task Impact — 지식 그라운딩 영향 분석 (UOW-04).

저장된 FeatureKnowledge·Evidence를 컨텍스트로 자연어 작업의 영향을 분석한다.
일반 LLM 추측이 아닌 근거 참조·기존 충돌 경고가 결과에 박히는 것이 차별점(FR-IMPACT-002).
"""

from trace.impact.analyze import analyze_task, to_impact_out
from trace.impact.context import KnowledgeContext, build_context, rank_by_relevance

__all__ = [
    "KnowledgeContext",
    "build_context",
    "rank_by_relevance",
    "analyze_task",
    "to_impact_out",
]

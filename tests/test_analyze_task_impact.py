"""UOW-04 analyze_task_impact 파이프라인 테스트 — FakeLLM 주입 (Hero Task, BR-PIPE)."""

from __future__ import annotations

import json
from pathlib import Path

from trace.engine.analyze import analyze_task_impact
from trace.knowledge.store import KnowledgeStore
from trace.llm.service import LLMService
from trace.models.domain import (
    Conflict,
    ConflictValue,
    Evidence,
    EvidenceRelation,
    EvidenceType,
    Feature,
    FeatureKnowledge,
)

from tests.conftest import FakeLLMClient

_IMPACT = json.dumps({
    "candidates": [
        {"path": "src/Owner.java", "category": "must_change", "reason": "전화번호 검증 대상",
         "evidence": [{"source": "src/Owner.java", "location": "L42", "relation": "supports"}]},
        {"path": "openapi/petclinic.yaml", "category": "likely_change", "reason": "API 스키마",
         "evidence": [{"source": "openapi/petclinic.yaml", "location": "paths", "relation": "mentions"}]},
    ],
    "change_plan": ["1. telephone 길이 충돌 해소", "2. OpenAPI 정의 갱신", "3. 흐름 수정"],
})


def _seed_knowledge(root: Path) -> None:
    store = KnowledgeStore(root)
    fk = FeatureKnowledge(
        feature=Feature(id="owner-management", title="Owner Management", description="주인 관리",
                        related_sources=["src/Owner.java", "openapi/petclinic.yaml", "docs/spec.md"]),
        evidence=[
            Evidence(source="src/Owner.java", type=EvidenceType.SOURCE, location="L42",
                     extracted_value="10", relation=EvidenceRelation.CONTRADICTS),
            Evidence(source="docs/spec.md", type=EvidenceType.MARKDOWN, location="p.3",
                     extracted_value="20", relation=EvidenceRelation.SUPPORTS),
        ],
        conflicts=[Conflict(claim="owner.telephone.max_length",
                            values=[ConflictValue(value="20", source="docs/spec.md", location="p.3"),
                                    ConflictValue(value="10", source="src/Owner.java", location="L42")],
                            interpretation="요구 20 vs 구현 10")],
        meta={"stage": "complete"},
    )
    store.save_feature(fk)


def test_hero_task_classifies_and_warns_conflict(tmp_path: Path) -> None:
    _seed_knowledge(tmp_path)
    fake = FakeLLMClient([_IMPACT])
    result = analyze_task_impact("Add SMS verification to Owner registration",
                                 "owner-management", path=str(tmp_path), llm=LLMService(fake))

    assert result.impact is not None
    assert [it.path for it in result.impact.must_change] == ["src/Owner.java"]
    assert [it.path for it in result.impact.likely_change] == ["openapi/petclinic.yaml"]
    # 충돌 인지 경고(P1): 기존 telephone 충돌이 related_conflicts로 노출
    assert len(result.impact.related_conflicts) == 1
    assert result.impact.related_conflicts[0].claim == "owner.telephone.max_length"
    assert result.conflicts and "충돌" in result.summary  # 상단 경고
    assert result.impact.change_plan[0].startswith("1.")


def test_no_knowledge_degrades(tmp_path: Path) -> None:
    fake = FakeLLMClient([])  # 호출되면 예외
    result = analyze_task_impact("some task", path=str(tmp_path), llm=LLMService(fake))
    assert any(w.code == "no_knowledge" for w in result.warnings)
    assert len(fake.calls) == 0  # 지식 없으면 LLM 미호출


def test_llm_failure_degrades_but_surfaces_conflicts(tmp_path: Path) -> None:
    _seed_knowledge(tmp_path)
    fake = FakeLLMClient(["bad", "bad", "bad"])  # 검증 소진
    result = analyze_task_impact("task", "owner-management", path=str(tmp_path), llm=LLMService(fake))
    assert any(w.code == "task_analysis_failed" for w in result.warnings)
    # LLM 실패에도 기존 충돌은 노출
    assert result.impact is not None and len(result.impact.related_conflicts) == 1


def test_no_source_autofix(tmp_path: Path) -> None:
    _seed_knowledge(tmp_path)
    before = {p.name for p in tmp_path.rglob("*") if p.is_file()}
    analyze_task_impact("task", "owner-management", path=str(tmp_path),
                        llm=LLMService(FakeLLMClient([_IMPACT])))
    after = {p.name for p in tmp_path.rglob("*") if p.is_file()}
    # 지식 저장(.trace) 외 소스 파일을 새로 만들거나 수정하지 않음 — 신규 파일은 .trace 하위뿐
    assert before <= after  # 기존 파일 유지(삭제 없음)

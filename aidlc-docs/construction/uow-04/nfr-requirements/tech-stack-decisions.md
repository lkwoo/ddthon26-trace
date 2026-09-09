# UOW-04 (Task Impact Analysis) — Tech Stack Decisions

**단계**: CONSTRUCTION / NFR Requirements (UOW-04)
**작성일**: 2026-09-09

---

## 상속 (변경 없음)
- **언어/런타임**: Python 3.11+, Pydantic v2 (UOW-0F).
- **LLM**: Anthropic Claude, `LLMService.complete_structured` (UOW-0F, temp=0 결정성).
- **저장 지식 소비**: `KnowledgeStore.load_feature/list_feature_summaries` (UOW-02), `summarize_conflicts` (UOW-03).
- **출력 DTO**: `ImpactOut/ImpactItem/EvidenceRef`, `build_result` (UOW-0F) — **재사용, 신규 코어 모델 없음**.
- **테스트**: pytest + hypothesis, FakeLLM(conftest), `llm_integration` 마커 재사용.

## 신규 (UOW-04)
| 항목 | 결정 |
|---|---|
| LLM 중간 스키마 | `trace/models/impact.py`: `ImpactCandidate`, `TaskImpactResult` (Pydantic). |
| 모듈 | `trace/impact/{context,analyze}.py` (C6), `engine/analyze.analyze_task_impact` 추가. |
| 프롬프트 | `prompts/templates/analyze_task.md` (C8). |
| focus 상한 | 관련도 상위 **N=3** 상세 포함(상수, MAINT-2 국소화). 발췌 4,000자 상속. |

## 비결정 / 유지
- **신규 런타임 의존성 없음** — 표준 라이브러리 + 기존 스택만.
- 프로젝트 루트는 `analyze_task_impact(..., path=".")` 명시 인자(UOW-03 analyze_project와 정합, UOW-06 어댑터 주입).
- 관련도 랭킹은 토큰 겹침 기반 경량 휴리스틱(외부 임베딩·검색 라이브러리 미도입 — 결정성·의존성 최소).

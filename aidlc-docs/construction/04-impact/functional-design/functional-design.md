# UOW-04 Task Impact — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: component-methods.md(C6·C3 analyze_task), unit-of-work.md(UOW-04), 요구사항 §2(Hero)·§11(영향)
**스토리**: FR-IMPACT-001(영향 분류), FR-IMPACT-002(지식 그라운딩), FR-IMPACT-003(자동수정 금지)
**의존**: UOW-0F(models·Result·LLM), UOW-02(지식 저장소), UOW-03(충돌)

## 1. 목적

개발자가 자연어로 착수할 작업을 말하면, **코드를 짜기 전에** 저장된 Feature 지식에 그라운딩해
영향 파일을 Must/Likely/Review로 분류하고, 관련 충돌을 경고하며, 순서형 Change Plan을 낸다.
이것이 Hero 시나리오("Add SMS verification to Owner registration")의 최종 산출이다.

## 2. 함수

- **C3 `analyze_task(task, task_id, context, llm)`**: 지식 컨텍스트를 넣어 LLM 구조화 출력을 받는다
  (step_key `analyze_task.<slug>`).
- **C6 `analyze_task_impact(task, feature_id=None)`** (코어 함수):
  1) 지식 로드·컨텍스트 렌더(Claim·근거·충돌) → 2) analyze_task 호출 → 3) 항목 정규화
  {path, reason, evidence} → 4) 관련 충돌 병합 → 5) Result 조립.
  - impact: {task, must_change, likely_change, review, change_plan, related_conflicts}.

## 3. 비즈니스 규칙

1. **지식 그라운딩**(FR-IMPACT-002): 지식이 없으면 오류로 `analyze_project` 선행을 안내. 모든
   항목은 근거(evidence) 소스를 동반.
2. **충돌 인지**(요구 §2): 지식에 있는 value_mismatch를 작업과 함께 상위 노출(conflicts)하고
   warning으로 "착수 전 확인"을 남긴다.
3. **자동 수정 금지**(FR-IMPACT-003): 소스를 편집하지 않고 제안(Change Plan)만 낸다. (테스트로 불변 검증.)
4. **결정성**(NFR-AI-004): replay step_key로 Hero 작업을 API 키 없이 재현.

## 4. 검증

`tests/test_impact.py` 5개 통과: 빈 작업 오류·지식 없음 안내·Hero 분류/계획·충돌 인지·소스 불변.
E2E(replay): Hero 작업 → OwnerRestController가 must_change, 전화번호 길이 충돌 경고, 5단계 계획.
전체 52개 통과.

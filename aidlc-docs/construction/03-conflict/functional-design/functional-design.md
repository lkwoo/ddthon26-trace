# UOW-03 Claims/Evidence/Conflict — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: component-methods.md(C3·C5), unit-of-work.md(UOW-03), 요구사항 §1.3(차별점)·§9(충돌)·§8.3(신뢰도)
**스토리**: FR-CLAIM-001, FR-EVIDENCE-001, FR-CONFIDENCE-001, FR-CONFLICT-001, FR-CONFLICT-OUT-001/002
**의존**: UOW-0F(models), UOW-01(assets), UOW-02(파이프라인 register_enrich_hook 확장점)

## 1. 왜 이 단위가 핵심인가 (구조적 차별점, 창의성)

RAG류 도구는 임베딩 유사도로 '비슷한 것'을 검색한다. TRACE는 자산에서 **정규화 Claim
(subject·predicate·value)** 을 뽑고, 같은 `key = subject.predicate`에 붙은 서로 다른 value를
**결정적 코드**로 비교해 `value_mismatch`를 1급 산출물로 검출한다. 즉 "어긋난 것"을 능동적으로
찾아 착수 전에 경고한다. LLM은 추출까지만, **판정은 순수 함수**라 재현 가능하다(NFR-AI-004).

## 2. 컴포넌트/함수

- **C3 추출(`trace/workflow`)**: `extract_claims(feature, assets, llm)`(step_key `extract_claims.<id>`),
  `group_evidence(claims)`(동일 key·value 병합 + Evidence 중복 제거).
- **C5 검출/신뢰도(`trace/conflict`)** — 모두 결정적 순수 함수:
  - `normalize_value(v)`: 공백·대소문자·후행 구두점 정규화(멱등).
  - `assign_confidence(claim)`: 근거 일치도 기반(FR-CONFIDENCE-001).
  - `detect_conflicts(claims)`: key별 정규화 값 ≥2 → `value_mismatch`(P0), 각 (값·소스) 인용.
  - `summarize_conflicts`/`get_conflicts(feature_id=None)`: 저장 지식에서 충돌 수집·Result 노출.
- **파이프라인 통합**: `enrich_feature`를 import 시 `register_enrich_hook`으로 등록 →
  `analyze_project`가 UOW-02 본문 수정 없이 Claim/Conflict를 채운다(개방-폐쇄).

## 3. 비즈니스 규칙

1. **정규화 우선**: 서로 다른 자산이 같은 개념을 같은 subject.predicate로 말하도록 프롬프트가 강제 →
   비교 가능성 확보(차별점의 전제).
2. **결정성**: 충돌·신뢰도는 LLM 비의존 순수 함수. 안정 정렬로 입력 순서와 무관하게 동일 출력.
3. **신뢰도(FR-CONFIDENCE-001)**: 반박 근거 있으면 LOW; direct/supporting ≥2 HIGH; 1 MEDIUM; 0 LOW.
4. **소스 우선순위 미가정**(요구 §9): 충돌 해석은 "어느 쪽이 옳다"가 아니라 "확인 필요"로 서술.
5. **Feature 신뢰도**: 충돌 존재 시 LOW로 하향(불확실 신호).

## 4. 확장 준수

- **PBT(전면)**: 합의 시 무충돌·불일치 시 대칭 검출·결정성(순서 무관)·normalize 멱등 속성 테스트.
- **Resiliency**: LLM 실패는 파이프라인 warning으로 흡수(FR-ANALYSIS-003), 전체 중단 없음.

## 5. 검증

`tests/test_conflict.py` 7개 통과(속성 4 + 신뢰도 2 + Hero E2E 1). E2E: replay로 demo 분석 시
`Owner.telephone.max_length`에 20(PDF 요구) vs 10(OpenAPI·SQL·Java) **value_mismatch 1건**을
근거 인용과 함께 검출. 전체 47개 통과.

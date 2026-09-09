# UOW-04 (Task Impact Analysis) — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (UOW-04)
**작성일**: 2026-09-09
**책임(unit-of-work.md)**: `analyze_task_impact(task, feature_id?)` — 저장된 지식·근거 그라운딩 → Must/Likely/Review(+이유·근거),
충돌 인지 경고(P1), 순서형 Change Plan. 소스 자동수정 없음(자문용). `analyze_task`(C3) step.
**스토리**: US-04.1(지식 기반 분석)·US-04.2(3범주+근거)·US-04.3(충돌 경고)·US-04.4(Change Plan).
**요구사항**: FR-IMPACT-001~006, NFR-AI-003(근거 부족→Review/LOW).
**소비 계약(기존)**: `ImpactOut{must_change,likely_change,review,related_conflicts,change_plan}`,
`ImpactItem{path,reason,evidence}`, `EvidenceRef{source,location,relation}`(result.py, UOW-0F 동결),
`KnowledgeStore.load_feature/list_feature_summaries`, `summarize_conflicts`, `LLMService.complete_structured`, `build_result`.

---

## 계획 스텝 (체크박스)
- [x] S1. 도메인 — TaskImpact LLM 중간 스키마(analyze_task step 출력) 설계 (기존 ImpactOut로 매핑)
- [x] S2. 지식 컨텍스트 조립 — feature_id 유무별 대상 지식·근거 선별(그라운딩, FR-IMPACT-002)
- [x] S3. 영향 분류 규칙 — Must/Likely/Review 판정·근거 참조·근거부족 강등(BR, NFR-AI-003)
- [x] S4. 충돌 인지 경고(P1) — 대상 지식의 기존 conflicts를 related_conflicts로 노출(FR-IMPACT-004)
- [x] S5. Change Plan — 순서형 단계 생성 규칙(충돌 해소 우선), 소스 자동수정 금지(FR-IMPACT-006)
- [x] S6. analyze_task_impact 조립 — 컨텍스트→LLM→ImpactOut→build_result, 실패 강등(BR-PIPE)
- [x] S7. 배치/알고리즘 — impact/ 모듈·시그니처·데이터 흐름·DoD·테스트 전략
- [x] S8. 산출물 3종 작성(domain-entities/business-rules/business-logic-model)

---

## 확정 필요 질문 (답변은 [Answer]: A (권장) 태그에 기입)

### Q1. 영향 후보 범위 — 무엇을 Must/Likely/Review 대상으로?
- **A. 저장된 지식(대상 Feature의 related_sources·evidence 소스)에 한정** (권장) — 근거 그라운딩·재현성, 환각 억제(FR-IMPACT-002)
- **B. 전체 스캔 자산까지 확장** — 더 광범위하나 근거 없는 추측 위험
- **C. 기타(직접 지정)**

[Answer]: A (권장)

### Q2. feature_id 미지정 시 지식 컨텍스트 선택
- **A. 전체 Feature 요약을 컨텍스트로 주고, 작업과 관련도 높은 Feature의 상세 지식을 우선 포함** (권장) — 광범위+집중 절충
- **B. 작업 텍스트와 매칭되는 Feature만 자동 선택(단일/소수)** — 토큰 절약, 매칭 실패 위험
- **C. 기타(직접 지정)**

[Answer]: A (권장)

### Q3. 충돌 인지 경고(P1) — related_conflicts 판정 기준
- **A. 대상 Feature(들)의 기존 conflicts를 그대로 related_conflicts로 노출** (권장) — 결정적·저장 지식 재사용(UOW-03 산출)
- **B. 작업 텍스트/영향 대상과 claim_key 매칭으로 필터링** — 정밀하나 매칭 규칙 복잡
- **C. 기타(직접 지정)**

[Answer]: A (권장)

### Q4. Change Plan 생성 방식
- **A. LLM이 근거 기반 순서 단계 생성(관련 충돌 해소를 앞 순서로), 소스 자동수정 없음** (권장, FR-IMPACT-006/US-04.4)
- **B. 규칙 기반 고정 템플릿 순서(정책→API→흐름→설정→테스트→문서)** — 결정적이나 경직
- **C. 기타(직접 지정)**

[Answer]: A (권장)

### Q5. LLM 실패/근거 부족 처리
- **A. analyze_task 1회 구조화 호출, 실패 시 warning 강등(빈 ImpactOut+안내), 근거 부족 항목은 Review+Confidence LOW 표기** (권장, NFR-AI-003·BR-PIPE-002)
- **B. 기타(직접 지정)**

[Answer]: A (권장)

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-04/functional-design/domain-entities.md`
- `aidlc-docs/construction/uow-04/functional-design/business-rules.md`
- `aidlc-docs/construction/uow-04/functional-design/business-logic-model.md`

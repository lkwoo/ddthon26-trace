# UOW-03 (Claims / Evidence / Conflict) — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (per-unit: UOW-03)
**작성일**: 2026-09-09
**앞 단계 반영**:
- UOW-02 지식 셸(FeatureKnowledge, claims/evidence/conflicts=[])을 **완본화**한다(Q2=A 경계 이어받음).
- UOW-0F 모델: Claim(subject/predicate/value/feature_id)·Evidence(source/type/location/extracted_value/relation)
  ·ClaimConfidence·Conflict(type/claim/values/interpretation)·`claim_key`·`normalize_value`·`ConflictType`.
- component-methods: `extract_claims`·`group_evidence`·`assign_confidence`·`detect_conflicts`·`summarize_conflicts`·`get_conflicts`.
- 요구: FR-CLAIM-001(원자), FR-EVIDENCE-001, FR-CONFIDENCE-001(근거 일치도), FR-CONFLICT-001(value_mismatch P0),
  FR-CONFLICT-OUT-001/002. **핵심 차별점**: 정규화 Claim↔Evidence 비교로 어긋남을 1급 산출물로 검출.

> UOW-03은 파이프라인 後반부: Feature별로 **원자 Claim 추출 → Evidence 연결 → 근거 일치도 Confidence →
> value_mismatch(및 확장) Conflict 검출**을 수행해 지식을 완본화하고, `analyze_project` 전체 파이프라인과
> `get_conflicts` 조회를 완성한다.

---

## 계획 스텝 (체크박스)
- [ ] S1. `extract_claims(feature, assets, llm)` — 원자 Claim(subject+predicate+value) 추출 스키마/알고리즘
- [ ] S2. `group_evidence(claims, assets, llm)` — Claim별 Evidence(소스·유형·위치·추출값·관계) 연결
- [ ] S3. `assign_confidence(claim, evidence)` — **근거 일치도** 규칙(비-LLM) 정의(HIGH/MEDIUM/LOW)
- [ ] S4. `detect_conflicts(fk)` — claim_key별 Evidence 값 비교 → value_mismatch (결정적) + 확장 유형
- [ ] S5. ConflictType 확장 여부(stale_knowledge·policy_conflict, P1) 및 검출 규칙
- [ ] S6. `get_conflicts(feature_id)`·`summarize_conflicts` 조회 계약 + FeatureKnowledge 완본화·재저장
- [ ] S7. `analyze_project(path)` 전체 파이프라인 완성(스캔→지식→claim/evidence/conflict→저장) 범위
- [ ] S8. business-logic-model / business-rules / domain-entities 산출물 작성

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. ConflictType 확장 — 데모 3충돌을 모두 검출할까?
현재 `ConflictType`은 `value_mismatch`(P0)만. UOW-00 데모는 3충돌 설계(C-1 value_mismatch, C-2 stale_knowledge,
C-3 policy_conflict) — 3 페르소나 재현 전제.
- **A. ConflictType에 `stale_knowledge`·`policy_conflict`(P1) 추가 → 데모 3충돌 모두 검출** (권장) — 3 페르소나 walkthrough 성립, 차별점 강화
- **B. value_mismatch(P0)만 유지 → C-2/C-3는 이번 범위 밖(warning/추후)** — 최소 범위, 그러나 P2/P3 시연 약화
- **C. 기타(직접 지정)**

[Answer]:

### Q2. detect_conflicts 방식 — 결정적 비교 vs LLM?
- **A. 결정적(rule-based)**: 같은 claim_key(subject+predicate)에 서로 다른 normalize_value가 2개 이상이면 value_mismatch.
  stale_knowledge/policy_conflict도 관계(contradicts)·존재/부재 규칙으로 판정 (권장) — 재현성·검증 용이, RAG와의 구조적 차별점을 코드로 입증
- **B. LLM 기반 충돌 판정** — 유연하나 비결정·검증 곤란, 차별점 희석
- **C. 혼합(직접 지정)**

[Answer]:

### Q3. Claim/Evidence 추출 호출 구조 — 몇 번의 LLM 호출?
- **A. Feature당 1회 구조화 호출로 Claim+각 Claim의 Evidence를 함께 산출**(관계·추출값 포함) (권장) — 일관성↑·호출 수·비용↓
- **B. extract_claims → group_evidence 2단계 별도 호출** — 책임 분리 명확하나 호출·비용↑, 정합 관리 필요
- **C. 기타(직접 지정)**

[Answer]:

### Q4. Confidence 규칙 (FR-CONFIDENCE-001, 근거 일치도)
- **A. 규칙: 동일 claim_key에 대해 모든 Evidence가 일치(≥2 supporting, contradicting 없음)=HIGH,
  단일 근거 또는 부분 일치=MEDIUM, contradicting 존재(=충돌)=LOW** (권장) — 근거 기반·결정적, LLM 자기확신 배제
- **B. 다른 임계/정책(직접 지정)**

[Answer]:

### Q5. `analyze_project` 완성 범위 — 이번 단위에서 전체 파이프라인을 닫을까?
- **A. UOW-03에서 `analyze_project(path)` 전체(스캔→build_knowledge→claim/evidence/conflict 완본화→저장)를 완성**
  + `get_conflicts` 제공 (권장) — UOW-04(Impact)·UOW-05(MCP)가 곧바로 소비, Hero E2E 앞당김
- **B. step 함수만 만들고 analyze_project 조립은 UOW-04/05로 미룸** — 범위 최소, 그러나 통합 지연

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-03/functional-design/business-logic-model.md` — 추출→연결→confidence→충돌→완본화 알고리즘·analyze_project
- `aidlc-docs/construction/uow-03/functional-design/business-rules.md` — 원자성/정규화/근거일치/충돌 규칙
- `aidlc-docs/construction/uow-03/functional-design/domain-entities.md` — (확장 시) ConflictType·추출 스키마 + 기존 모델 매핑

# UOW-03 (Claims/Evidence/Conflict) — 비즈니스 규칙 (business-rules)

**단계**: CONSTRUCTION / Functional Design (UOW-03)
**작성일**: 2026-09-09
**출처**: FR-CLAIM-001·FR-EVIDENCE-001·FR-CONFIDENCE-001·FR-CONFLICT-001·FR-CONFLICT-OUT-001/002

---

## BR-CLAIM — 원자 Claim 추출 (FR-CLAIM-001, Q3=A)
- **BR-CLAIM-001**: Claim은 **원자적** — `subject`(무엇의) + `predicate`(어떤 속성) + `value`(값) 하나.
  복합 문장 금지(예: "telephone은 20자이고 필수" → 2개 Claim으로 분리).
- **BR-CLAIM-002**: 추출은 Feature당 1회 LLM 구조화 호출(ExtractedClaim 목록). 각 ExtractedClaim은
  자신의 근거 Evidence를 내장한다.
- **BR-CLAIM-003 (정규화)**: subject/predicate는 소문자·트림 정규화(claim_key 안정). value 비교는 `normalize_value`.
- **BR-CLAIM-004**: content 없는(skipped/failed) 자산은 근거가 될 수 없다(카탈로그 발췌 기반, UOW-02와 동일).

## BR-EVID — Evidence 연결 (FR-EVIDENCE-001)
- **BR-EVID-001**: Evidence = `source(rel_path)·type(EvidenceType)·location·extracted_value·relation`.
  relation ∈ {supports, contradicts, mentions}.
- **BR-EVID-002**: extracted_value는 그 소스에서 관측된 값(예: pdf="20", code="10"). 없으면 None(mentions).
- **BR-EVID-003 (부재 표현)**: 요구되는 대상이 소스에 존재하지 않으면 extracted_value를 부재 토큰
  (`absent`)으로 표기하고 relation=contradicts (정책 충돌 검출 근거, C-3).
- **BR-EVID-004**: source는 반드시 스캔된 자산의 rel_path(허구 소스 금지). 위반 Evidence는 드롭+warning.

## BR-CONF — Confidence (FR-CONFIDENCE-001, 근거 일치도, Q4=A) — **비-LLM**
claim의 evidence 집합으로 결정(모델 자기확신 사용 금지):
- distinct = 서로 다른 정규화 extracted_value(부재 토큰 포함, None 제외) 개수.
- has_contradiction = (relation=contradicts 존재) 또는 (distinct ≥ 2).
- **규칙**:
  - has_contradiction → **LOW** (충돌/불일치)
  - not has_contradiction ∧ supports ≥ 2 ∧ distinct ≤ 1 → **HIGH**
  - 그 외(단일 근거·mentions 위주) → **MEDIUM**
- reason 문자열 필수(BR-CONF-002): 근거 수·일치 여부를 한 줄로.

## BR-CONFLICT — 충돌 검출 (FR-CONFLICT-001, Q2=A 결정적)
- **BR-CONFLICT-001 (존재, 결정적·핵심 차별점)**: 한 claim_key(subject+predicate)의 evidence에서
  **정규화 extracted_value가 서로 다른 값 2개 이상**이면 Conflict 성립. LLM 판단 아님 — 구조적 비교.
- **BR-CONFLICT-002 (값 목록)**: Conflict.values = 각 distinct 값별 대표 ConflictValue(value, source, location).
  최소 2개(모델 검증과 정합).
- **BR-CONFLICT-003 (유형 분류, 결정적 순서)**:
  1. 어떤 값이 **부재 토큰**(`absent/none/missing/n/a/null/없음/부재`)이고 다른 값이 요구(문서/요구 소스)면 → `policy_conflict`.
  2. 아니고, 값이 **검증/규칙/행위 서술**(예: `검증함/없음/rejected/enforced/validated` 계열)이며 문서(pdf/markdown)와
     코드/DB/openapi가 상충하면 → `stale_knowledge`.
  3. 그 외(구체 값의 스칼라 불일치, 예: 20 vs 10) → `value_mismatch`.
- **BR-CONFLICT-004 (해석)**: interpretation은 사람이 읽는 한 줄(무엇이 어디서 어긋났는지·리스크). 필수.
- **BR-CONFLICT-005 (P0 우선)**: value_mismatch는 P0. stale_knowledge·policy_conflict는 P1(확장).
  검출 실패/모호 시 P1 유형은 최소한 value_mismatch로라도 노출(누락 금지).

## BR-OUT — 조회 출력 (FR-CONFLICT-OUT-001/002)
- **BR-OUT-001**: get_conflicts는 conflicts_count(구조화 필드) 제공, 각 값의 source 파일 참조 포함.
- **BR-OUT-002**: feature_id 지정 시 해당 Feature만, 미지정 시 전체 Feature 합산.
- **BR-OUT-003**: Result 조립은 build_result(충돌 상위 노출, 핵심 우선) 사용(UOW-0F).

## BR-PIPE — analyze_project 완성 (Q5=A)
- **BR-PIPE-001**: `analyze_project(path)` = validate→scan_project_assets→(cache-first) build_knowledge(셸)→
  Feature별 extract_claims→assign_confidence→detect_conflicts→FeatureKnowledge 완본화→save→캐시 갱신.
- **BR-PIPE-002 (부분 실패)**: 추출/충돌 단계의 Feature별 실패는 warning 강등(그 Feature는 셸 유지), 전체 계속.
- **BR-PIPE-003 (캐시)**: 완본 FeatureKnowledge 저장 후 CacheEntry 갱신. 자산 불변 재실행은 캐시 히트(LLM 미호출).

## BR-DET / BR-SEC
- **BR-DET-001**: 충돌 검출·Confidence는 결정적(정렬·정규화). 동일 추출 입력 → 동일 conflicts.
- **BR-DET-002**: conflicts/claims/evidence는 안정 정렬(claim_key, source)로 저장(재현성).
- **BR-SEC-001**: 경고/로그에 원문·시크릿 비노출. Evidence.location은 파일 내 위치 표기(원문 복사 금지).

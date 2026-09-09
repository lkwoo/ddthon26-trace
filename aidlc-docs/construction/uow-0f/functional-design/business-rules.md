# UOW-0F — 비즈니스 규칙 (Business Rules)

**단계**: CONSTRUCTION / Functional Design — UOW-0F (Foundation)
**작성일**: 2026-09-09

> Foundation이 동결하는 검증·판정·불변식 규칙. 이후 단위는 이 규칙을 재정의하지 않고 준수한다.
> 각 규칙은 Property-Based Testing(활성, Blocking) 대상 후보다 — 관련 속성을 명시한다.

---

## §ID — feature_id 생성 규칙 (Q1=A slug)

- **BR-ID-001**: `feature_id`는 `title`을 kebab-case slug로 변환해 생성. 소문자화 → 영숫자/공백만 유지 → 공백을 `-`로 → 연속 `-` 축약 → 양끝 `-` 제거.
- **BR-ID-002**: 빈 slug(제목이 비영숫자뿐) → `feature`로 대체.
- **BR-ID-003**: 같은 분석 내 slug 충돌 시 `-2`, `-3` … 접미사로 유일화.
- **BR-ID-004**: `feature_id`는 파일명·리소스 URI로 안전해야 함(경로 구분자·상위참조 금지). 검증 실패 → `StorageError`.
- *속성*: slug(slug(x)) == slug(x) (멱등), 결과는 `^[a-z0-9-]+$`.

## §정규화 — 값 비교 정규화 (충돌 검출 전제)

- **BR-NORM-001**: `Claim.value`·`Evidence.extracted_value` 비교 시 앞뒤 공백 제거, 따옴표 제거, 대소문자 무시(단, 순수 숫자는 숫자 동등성으로 비교: `"20"` vs `"20.0"` → 동일). 원본 값은 표시용으로 보존.
- **BR-NORM-002**: `claim_key = f"{subject}.{predicate}"` (신뢰도·충돌 그룹핑 키). subject/predicate는 trim만, 값 변형 없음.
- *속성*: normalize는 멱등; 표시값 ≠ 비교값이어도 표시값은 손실 없이 보존.

## §검증 — 도메인 객체 필수 필드 검증

- **BR-VAL-001**: `Feature`는 `id, title, description` 필수(비어있으면 안 됨).
- **BR-VAL-002**: `Claim`은 `subject, predicate, value, feature_id` 모두 필수. 하나라도 공백 → 무효(생성 거부).
- **BR-VAL-003**: `Evidence`는 `source, type, location, relation` 필수. `type`은 EvidenceType enum, `relation`은 EvidenceRelation enum 밖 값이면 무효.
- **BR-VAL-004**: `Conflict.values`는 **2개 이상**의 서로 다른 값을 가져야 성립(단일 값은 충돌 아님).
- **BR-VAL-005**: 역직렬화 시 필수 필드 누락/enum 위반 → `StorageError`(부분 손상 파일은 로드 거부, 어댑터가 warning으로 전환).
- *속성*: 유효 객체 → serialize → deserialize == 원본(round-trip 동등, 표시값·순서 보존).

## §신뢰도 — Confidence 판정 규칙 (Q2=B, 스켈레톤 수준)

- **BR-CONF-001**: 신뢰도는 근거 일치도로 판정한다(구체 알고리즘은 UOW-03 소관). Foundation은 **표현 계약**만 고정: `ConfidenceAssessment = {level: Confidence, reason: str}`.
- **BR-CONF-002**: `reason`은 필수(비어있으면 안 됨) — 왜 그 등급인지 사람이 읽을 수 있어야 함.
- **BR-CONF-003**(가이드, 03에서 구현): 다수 근거가 supports & 상충 없음 → HIGH; 근거 희소/단일 → MEDIUM; contradicts 존재 또는 근거 없음 → LOW.

## §충돌 — Conflict 성립 규칙 (P0=value_mismatch)

- **BR-CONFLICT-001**: 같은 `claim_key`에 대해 정규화 후 **서로 다른 값**이 2개 이상 근거로 존재하면 `value_mismatch` 성립.
- **BR-CONFLICT-002**: `Conflict.interpretation`은 필수 — 어떤 값들이 왜 어긋나며 무엇에 영향을 주는지 사람이 읽는 설명.
- **BR-CONFLICT-003**: 충돌은 Result에서 **상위 노출**(build_result 규칙 2).

## §시크릿 — 키 취급 규칙 (NFR-SEC-001, US-06.4)

- **BR-SEC-001**: API 키·비밀은 **코드/설정 파일/지식 파일/로그 어디에도 평문 저장 금지**. `LLMSettings`는 키 **값**이 아니라 **환경변수 이름(`api_key_env`)**만 보관.
- **BR-SEC-002**: 키는 소비 직전 `os.environ`에서 조회. 미설정 → `ConfigError`(명확한 안내 메시지, 값 노출 없음).
- **BR-SEC-003**: 로깅 시 값 필드·문서 원문은 마스킹/생략.

## §경로 — 경로 검증 규칙 (NFR-SEC-004)

- **BR-PATH-001**: 스캔·저장 경로는 지정된 프로젝트 루트/`.trace` 하위로 제한. 상위 참조(`..`)로 루트 이탈 시 `PathValidationError`.
- **BR-PATH-002**: 심볼릭 링크·접근 불가 경로는 skip + `Warning(code=PATH_SKIPPED)`. (전체 중단 아님 — FR-ANALYSIS-003)

## §결정성 — 재현성 규칙 (Q7=A, NFR-CORE-001)

- **BR-DET-001**: LLM 결정성 파라미터(temperature=0, seed)는 `get_llm_settings()`에서만 관리. 호출부 하드코딩 금지.
- **BR-DET-002**: 직렬화 출력은 필드/리스트 순서 고정 → 동일 입력 시 바이트 동일 파일. (Hero 데모 재현성)
- *속성*: 같은 입력·같은 config → serialize 결과 동일.

## §오류 — 오류 분류·변환 규칙 (Q8=A, Resiliency Baseline)

- **BR-ERR-001**: 모든 도메인/서비스 오류는 `TraceError` 하위 타입으로 raise(§도메인 계층).
- **BR-ERR-002**: 어댑터(C1/C9)는 `TraceError`를 잡아 사용자용 `Result.warnings` 또는 오류 요약으로 변환. **stack trace·내부 경로 원문 노출 금지**.
- **BR-ERR-003**: 부분 실패(파싱·LLM 일부)는 예외를 warning으로 강등하고 파이프라인 계속. 치명 오류(경로 이탈·키 부재)는 즉시 중단 + 명확한 요약.

## §Warning — 경고 구조 규칙 (Q5=B)

- **BR-WARN-001**: `Warning`은 `{code, message, source?}` 구조. `code`는 사전 정의 집합에서(예: `PARSE_PARTIAL, LLM_LOW_CONFIDENCE, PATH_SKIPPED, LLM_RETRY_EXHAUSTED`).
- **BR-WARN-002**: Result.summary에는 warnings의 사람이 읽는 합본을 반영하되, 구조화 warnings 필드는 원형 유지.

---

## 요구사항 추적 매트릭스

| 규칙군 | FR/NFR | 스토리 |
|---|---|---|
| §ID, §정규화, §검증 | NFR-CORE-002, FR-CLAIM-001, FR-EVIDENCE-001 | US-02.3, US-03.1, US-03.2 |
| §신뢰도 | FR-CONFIDENCE-001 | US-03.2 |
| §충돌 | FR-CONFLICT-001 | US-03.3 |
| §시크릿 | NFR-SEC-001 | US-06.4 |
| §경로 | NFR-SEC-004, FR-ANALYSIS-003 | US-01.x |
| §결정성 | NFR-CORE-001, NFR-AI-004 | US-06.1 |
| §오류/§Warning | FR-ANALYSIS-003, NFR-LOG-001 (Resiliency Baseline) | US-06.2 |

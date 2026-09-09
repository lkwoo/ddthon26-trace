# UOW-0F Foundation — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (Part 1 — Planning)
**단위**: UOW-0F (Foundation, enabler)
**작성일**: 2026-09-09
**전제**: unit-of-work.md(§UOW-0F), component-methods.md(공통 Result envelope·C4 모델·C7/C8), Extension: Resiliency Baseline·Property-Based Testing 활성(Blocking)

> UOW-0F는 이후 모든 단위가 임포트하는 **계약을 동결**하는 enabler 단위다. 여기서 잘못 정하면
> 01~06 전 트랙이 흔들리므로, 도메인 모델·Result envelope·직렬화 스키마·config·프롬프트 로더·
> LLMService 스켈레톤의 **필드/시그니처/불변식**을 이 단계에서 확정한다. (인프라·기술구현 세부는
> NFR Design/Code Generation으로 미룸.)

---

## 설계 범위 (Foundation이 동결할 계약)

1. **C4 도메인 모델** — `Feature, Claim, Evidence, Confidence, Conflict, FeatureKnowledge` + 출력 DTO(`ConflictOut, ImpactOut, EvidenceRef, FeatureSummary`)
2. **공통 `Result` envelope** — summary/data/conflicts/impact/evidence/warnings/meta
3. **MD+YAML Front Matter 직렬화 스키마** — `.trace/knowledge/features/<id>.md`의 단일 진실원(구조=YAML, 본문=Markdown)
4. **C7 `config`** — `load_config / get_exclusions / get_llm_settings`, 시크릿(env), 결정성 파라미터
5. **C8 프롬프트 로더** — `get_prompt(name, **vars)` (템플릿 내용 아님, 로더 계약만)
6. **S4 `LLMService` 스켈레톤** — Claude 호출·구조화(JSON) 출력 검증·제약 교정 재시도·결정성 고정 인터페이스
7. **공통 로깅(NFR-LOG-001)·오류 타입 계층**

---

## 실행 체크리스트

- [x] Step A: 도메인 엔티티 정의 (`domain-entities.md`) — 각 엔티티 필드·타입·필수/선택·enum·관계·불변식
- [x] Step B: 비즈니스 로직 모델 (`business-logic-model.md`) — Result 조립 규칙, 직렬화/역직렬화 흐름, config 로딩 순서, LLMService 호출 계약(검증→재시도→warning), 프롬프트 로더 렌더 흐름
- [x] Step C: 비즈니스 규칙 (`business-rules.md`) — 필드 검증 규칙, feature_id 생성 규칙, Confidence 판정 입력 규칙(스켈레톤 수준), 오류 분류 규칙, 시크릿 취급 규칙, 결정성 규칙
- [x] Step D: 질문 답변 반영(Q1~Q8 프리필 승인) 후 산출물 3종 생성 완료 → 완료 메시지 → 승인 대기

---

## 질문 (Q — `[Answer]:` 태그에 기입해 주세요)

> 답이 이미 요구사항/설계에 있으면 **권장안**을 프리필했습니다. 그대로 두면 권장안 채택으로 간주합니다.

### Q1. `Feature`/`FeatureKnowledge` 식별자(`feature_id`) 생성 규칙
Feature는 자동 검출(Q4=완전자동)됩니다. 지식 파일명(`<id>.md`)·MCP 리소스 URI에 쓰이는 안정적 ID가 필요합니다.
- A) 사람이 읽는 slug (제목 기반, 예: `owner-registration`) — 리소스 URI 가독성 우선 (권장)
- B) 짧은 해시/UUID (예: `feat-a1b2c3`) — 충돌 없음, 가독성 낮음
- C) slug + 짧은 해시 접미사 (예: `owner-registration-a1b2`) — 가독성 + 충돌 회피

[Answer]: A

### Q2. `Confidence` 표현 방식
근거 일치도 기반 3단계(HIGH/MEDIUM/LOW)가 요구사항입니다. 모델 표현을 어떻게 동결할까요?
- A) enum(HIGH/MEDIUM/LOW)만 — 단순, 결정적 (권장)
- B) enum + 사유 문자열(`reason`) 필드 — 왜 그 등급인지 근거 노출(에이전트 설명력↑)
- C) enum + 수치 score(0~1) + reason — 정렬·임계 조정 가능하나 LLM 수치 안정성 낮음

[Answer]: B

### Q3. `Evidence`의 `relation`(근거가 Claim을 어떻게 뒷받침/반박하는지) 값 집합
component-methods에 Evidence(…relation) 필드가 있습니다. 이 값의 도메인을 고정할까요?
- A) enum 고정: `supports / contradicts / mentions` — 충돌 검출·신뢰도 판정이 일관 (권장)
- B) 자유 문자열 — 유연하나 하위 로직이 파싱 불안정
- C) enum: `supports / contradicts / partially_supports / mentions` — 더 세분

[Answer]: A

### Q4. MD+YAML 직렬화에서 "단일 진실원"의 구체 형태
지식 파일은 구조=YAML Front Matter, 설명=Markdown 본문입니다. 역직렬화 시 진실원은?
- A) YAML Front Matter가 구조적 진실원, 본문은 사람이 읽는 렌더(파생) — 로드 시 YAML만 파싱 (권장)
- B) 본문과 YAML 양쪽을 모두 파싱해 교차검증
- C) 전체를 YAML로, 본문 Markdown은 YAML 내 문자열 필드

[Answer]: A

### Q5. `Result.warnings` / 부분 실패의 표현 세분도 (Resiliency Baseline 활성)
부분 실패·저신뢰는 warnings로 노출(FR-ANALYSIS-003)됩니다. warnings 항목 구조는?
- A) 사람이 읽는 문자열 리스트(`list[str]`) — 단순, 에이전트가 그대로 설명 (권장, component-methods 현재안)
- B) 구조화 객체 리스트(`{code, message, source?}`) — 기계 필터링·집계 가능, 관측성↑
- C) 둘 다: 구조화 저장 + summary에 사람이 읽는 합본

[Answer]: B

### Q6. `LLMService` 스켈레톤이 이 단계에서 동결할 계약 범위
S4는 0F에서 "스켈레톤"입니다. 어디까지를 계약으로 고정할까요?
- A) 인터페이스만: `complete_structured(prompt, schema, *, retries) -> validated_obj`, 결정성 파라미터(temperature=0 등)·재시도 정책·검증 실패 시 예외 타입까지 고정. 실제 Claude 호출 구현은 Code Generation에서. (권장)
- B) 인터페이스 + 실동작 Claude 호출까지 0F에서 구현
- C) 최소 추상만(호출 시그니처), 재시도/검증 정책은 각 AI 단위가 자율 결정

[Answer]: A

### Q7. 결정성(재현성) 파라미터 노출 위치
데모 재현성이 중요합니다(Hero 시나리오). 결정성 파라미터(temperature, seed 등)를?
- A) `get_llm_settings()`(config)에서 중앙 관리, LLMService가 소비 — 한 곳에서 제어 (권장)
- B) 각 호출부에서 개별 지정
- C) 환경변수로만

[Answer]: A

### Q8. 오류 타입 계층 (Resiliency Baseline)
공통 오류 타입을 어떻게 동결할까요?
- A) 베이스 `TraceError` + 하위: `ConfigError, PathValidationError(NFR-SEC-004), ParseError, LLMValidationError, StorageError` — 단위별로 적절히 raise, 어댑터(C1/C9)에서 Result.warnings/오류요약으로 변환 (권장)
- B) 단일 `TraceError`만
- C) 표준 예외(ValueError 등) 재사용, 커스텀 없음

[Answer]: A

### Q9. 이 계획 자체 승인
- [Answer]: (예: "승인" 또는 변경요청 내용)

---

## 다음 단계
답변 반영 후 `aidlc-docs/construction/uow-0f/functional-design/`에 3종 산출물 생성 → 완료 메시지 → 승인 시 UOW-0F **NFR Requirements**로 진행.

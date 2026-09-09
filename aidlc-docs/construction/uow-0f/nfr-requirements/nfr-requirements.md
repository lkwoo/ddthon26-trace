# UOW-0F — NFR Requirements

**단계**: CONSTRUCTION / NFR Requirements — UOW-0F (Foundation)
**작성일**: 2026-09-09
**활성 확장**: Resiliency Baseline · Property-Based Testing (Blocking)

> UOW-0F는 로컬 stdio 단일 프로세스에서 임포트되는 **기반 라이브러리 계층**이다. 서비스형 NFR
> (확장성·가용성)은 개념상 성립하지 않으므로 N/A로 두고, 이 단위가 실제로 책임지는
> **재현성·신뢰성·보안·유지보수·테스트가능성·관측성**을 측정 가능한 기준으로 고정한다.

---

## 카테고리 적용성 요약

| 카테고리 | 상태 | 사유 |
|---|---|---|
| Scalability | **N/A** | 로컬 단일 프로세스, 동시 부하 없음 |
| Availability | **N/A** | 상시 서비스 아님(도구 호출형) |
| Performance | 부분 | 대용량은 UOW-01/02. 0F는 선형·비차단이면 충족 |
| Reliability | 적용 | 오류 계층·부분 실패 강등·결정성 |
| Security | 적용 | 시크릿 env-only·경로 검증·로그 마스킹 |
| Maintainability | 적용 | 계약 안정성·타입 명료·모듈 경계 |
| Testability | 적용 | PBT 속성·주입 가능 경계 |
| Observability | 적용 | 구조화 로깅·구조화 warnings |

---

## NFR 목록 (UOW-0F 귀속, 측정 가능 기준)

### 재현성 / 결정성 (NFR-CORE-001)
- **NFR-0F-DET-1**: 동일 `FeatureKnowledge` + 동일 config → `serialize()` 결과 **바이트 동일**. 필드·리스트 순서 고정, YAML `sort_keys=True`.
  - *검증*: Hypothesis round-trip 속성 `deserialize(serialize(x)) == x`, `serialize(x) == serialize(deserialize(serialize(x)))`.
- **NFR-0F-DET-2**: LLM 결정성 파라미터(`temperature=0`, `seed`)는 `get_llm_settings()`에서만 공급. 호출부 하드코딩 0건.

### 신뢰성 (Resiliency Baseline)
- **NFR-0F-REL-1**: 모든 실패는 `TraceError` 하위 타입으로 표현. 예외 계층 밖의 raw 예외가 어댑터 경계를 넘지 않음.
- **NFR-0F-REL-2**: 부분 실패(파싱·LLM 일부)는 `Warning(code,message,source?)`로 강등되어 파이프라인 지속(치명: 경로 이탈·키 부재만 중단).
- **NFR-0F-REL-3**: `LLMService.complete_structured`는 스키마 검증 실패 시 제약 교정으로 **최대 2회** 재시도, 소진 시 `LLMValidationError`.

### 보안 (NFR-SEC-001/004/005)
- **NFR-0F-SEC-1**: API 키·비밀은 코드/설정/지식/로그에 평문 저장 0건. `LLMSettings`는 **환경변수 이름**만 보관, 소비 직전 `os.environ` 조회, 미설정 시 `ConfigError`.
- **NFR-0F-SEC-2**: 경로 검증 계약(`PathValidationError`) 제공 — 지정 루트/`.trace` 이탈 차단(구현은 UOW-01, 계약·예외는 0F).
- **NFR-0F-SEC-3**: 로깅 시 문서 원문·키·값 필드 마스킹/생략(경로·카운트·요약만).
- **NFR-0F-SEC-4**: YAML은 `safe_load`만 사용(임의 객체 역직렬화 금지).

### 유지보수성 (NFR-MAINT-002)
- **NFR-0F-MNT-1**: 공개 계약(모델 필드·함수 시그니처·예외)은 타입 힌트 100% 표기. 하위 단위가 임포트하는 공개 심볼은 단일 모듈 경로에서 노출.
- **NFR-0F-MNT-2**: config·프롬프트 경로·기본값은 상수/설정으로 분리(하드코딩 산재 금지).

### 테스트 가능성 (Property-Based Testing)
- **NFR-0F-TST-1**: `LLMService`의 Claude 호출부는 **주입 가능**(스텁/모의로 대체 가능)해야 함 — 네트워크 없이 검증.
- **NFR-0F-TST-2**: 핵심 불변식은 PBT로: slug 멱등성(BR-ID-001), 정규화 멱등성(BR-NORM-001), 직렬화 round-trip(BR-VAL-005), Conflict 성립(값≥2, BR-CONFLICT-001).

### 관측성 (NFR-LOG-001)
- **NFR-0F-OBS-1**: 구조화 로그(키=값): 단계·자산카운트·재시도횟수·소요시간. 레벨 env(`TRACE_LOG_LEVEL`)로 조정.
- **NFR-0F-OBS-2**: `Warning`은 구조화(`code` 사전 집합) → 상위 단위가 집계·필터 가능.

### 성능 (부분)
- **NFR-0F-PERF-1**: 직렬화·검증·정규화는 입력 크기에 **선형(O(n))**, 이벤트 루프/호출 블로킹 없음. (대용량 스캔 성능은 UOW-01 소관)

---

## 추적 매트릭스

| NFR | 상위 요구사항 | 검증 방법 | 관련 BR |
|---|---|---|---|
| DET-1/2 | NFR-CORE-001 | Hypothesis round-trip | BR-DET-001/002 |
| REL-1/2/3 | Resiliency, FR-ANALYSIS-003 | 단위테스트(예외·강등·재시도) | BR-ERR-*, BR-WARN-* |
| SEC-1~4 | NFR-SEC-001/004/005 | 정적점검·단위테스트 | BR-SEC-*, BR-PATH-* |
| MNT-1/2 | NFR-MAINT-002 | 타입체크(mypy/pyright) | — |
| TST-1/2 | PBT 확장 | Hypothesis·모의주입 | BR-ID/NORM/VAL/CONFLICT |
| OBS-1/2 | NFR-LOG-001 | 로그 형식 검사 | BR-WARN-* |
| PERF-1 | NFR-PERF(간접) | 계약 리뷰 | — |

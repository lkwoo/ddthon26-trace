# UOW-0F Foundation — NFR Design 계획

**단계**: CONSTRUCTION / NFR Design (Part 1 — Planning)
**단위**: UOW-0F (Foundation, enabler)
**작성일**: 2026-09-09
**전제**: NFR Requirements(UOW-0F) 승인. NFR-0F-DET/REL/SEC/MNT/TST/OBS/PERF 확정. 스택: Pydantic v2·PyYAML·Hypothesis·표준 logging.

> UOW-0F는 인프라(큐·캐시·서킷브레이커) 없는 in-process 라이브러리 계층이다. 따라서 NFR "패턴"은
> 분산 시스템 패턴이 아니라 **코드 구조 패턴**(주입 경계·직렬화 결정성·오류 변환·로깅 횡단·설정 로딩)이다.
> 이 단계에서 NFR을 실제로 만족시키는 **설계 패턴과 논리 컴포넌트 배치**를 확정한다.

---

## 실행 체크리스트

- [x] Step A: 패턴 확정 (`nfr-design-patterns.md`) — 주입 경계·직렬화 결정성·오류→Result 변환·로깅 횡단·설정 로딩·재시도
- [x] Step B: 논리 컴포넌트 배치 (`logical-components.md`) — 0F 서브모듈 내부 구성과 협력, 주입 지점
- [x] Step C: 질문 답변 반영(Q1~Q6 승인) → 산출물 2종 생성 완료 → 완료 메시지 → 승인 대기

## 카테고리 적용성 (권장 사전판단)

| 카테고리 | 적용성 | 사유 |
|---|---|---|
| Resilience Patterns | **적용** | 재시도(제약교정)·부분실패 강등·오류 변환 경계 |
| Scalability Patterns | **N/A** | in-process 단일 프로세스 |
| Performance Patterns | 최소 | 선형·비차단 유지, 지연 캐싱은 UOW-02 |
| Security Patterns | **적용** | 시크릿 조회 경계·safe_load·경로 검증 계약·로그 마스킹 |
| Logical Components | **적용** | 큐/캐시 없음 → 순수 코드 컴포넌트(주입 경계·직렬화기·로거) |

---

## 질문 (Q — `[Answer]:` 태그) — 권장안 프리필

### Q1. LLMService 주입 경계 패턴 (NFR-0F-TST-1)
Claude 호출부를 테스트에서 대체 가능하게 하려면?
- A) **Protocol(인터페이스) + 생성자 주입** — `LLMClient` Protocol을 `LLMService`에 주입, 테스트는 fake 주입. 표준적·경량 (권장)
- B) 전역 싱글턴 + monkeypatch
- C) 팩토리 함수 + 환경 분기

[Answer]: A

### Q2. 오류 → Result 변환 경계 위치 (NFR-0F-REL-1)
TraceError를 사용자용 Result/warnings로 바꾸는 지점은?
- A) **어댑터 경계(C1 MCP / C9 CLI)에서만 변환**, 코어는 예외 raise 유지 — 관심사 분리 (권장, business-rules BR-ERR-002와 정합)
- B) 각 코어 함수가 자체 try/except로 Result 반환
- C) 데코레이터로 코어 함수 감싸 자동 변환

[Answer]: A

### Q3. 부분 실패 강등 패턴 (NFR-0F-REL-2)
파싱/LLM 부분 실패를 warning으로 모으는 방식은?
- A) **Result 빌더에 warning 누적기(collector) 전달** — 파이프라인이 진행하며 append, 마지막에 build_result (권장)
- B) 예외를 각 지점에서 잡아 즉시 로깅만
- C) 전역 warning 컨텍스트

[Answer]: A

### Q4. 로깅 횡단 관심사 적용 방식 (NFR-0F-OBS-1)
단계 타이밍·카운트 로깅을?
- A) **경량 컨텍스트 매니저/데코레이터**(`with log_stage("scan"): ...`) — 호출부 명시적, 의존성 0 (권장)
- B) 각 함수에서 수동 log 호출
- C) AOP 라이브러리

[Answer]: A

### Q5. 직렬화 결정성 보증 구현 패턴 (NFR-0F-DET-1)
- A) **단일 `serialize()` 함수에 정렬 규칙 집약**(YAML sort_keys=True + 리스트 정렬 키 고정) + Hypothesis round-trip 테스트로 계약 고정 (권장)
- B) 각 모델이 자체 직렬화

[Answer]: A

### Q6. 시크릿 조회 패턴 (NFR-0F-SEC-1)
- A) **`get_llm_settings()`가 이름만 반환 → LLMService가 소비 직전 `os.environ` 조회, 미설정 시 ConfigError** — 값이 객체에 머무는 구간 최소화 (권장)
- B) 로드 시점에 값까지 읽어 settings에 보관

[Answer]: A

### Q7. 이 계획 승인
[Answer]: (예: "승인" 또는 변경요청)

---

## 다음 단계
답변 반영 후 `aidlc-docs/construction/uow-0f/nfr-design/`에 `nfr-design-patterns.md`·`logical-components.md` 생성 → 완료 메시지 → 승인 시 UOW-0F **Code Generation**으로 진행(0F는 Infrastructure Design SKIP).

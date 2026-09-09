# UOW-0F Foundation — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (Part 1 — Planning)
**단위**: UOW-0F (Foundation, enabler)
**작성일**: 2026-09-09
**전제**: Functional Design(UOW-0F) 승인 완료. 활성 확장: Resiliency Baseline·Property-Based Testing(Blocking).

> UOW-0F는 라이브러리성 기반 계층(도메인 모델·직렬화·config·LLMService 스켈레톤·오류/로깅)이라
> 처리량·가용성 같은 서비스형 NFR보다 **재현성·계약 안정성·테스트 가능성·보안 위생·관측성**이 핵심이다.
> 기술 스택은 요구사항 단계(Q1~Q7)에서 이미 Python + MCP SDK + Anthropic Claude로 확정 → 여기선 라이브러리 선택을 구체화한다.

---

## 실행 체크리스트

- [ ] Step A: 적용 NFR 카테고리 선별 (성능·확장성은 대부분 N/A, 재현성·신뢰성·보안·유지보수·관측성 집중)
- [ ] Step B: UOW-0F에 귀속되는 NFR 목록화 (요구사항 문서 NFR-* 재매핑 + 측정 가능 기준)
- [ ] Step C: 기술 스택/라이브러리 결정 확정 (`tech-stack-decisions.md`)
- [ ] Step D: 질문 답변 반영 → 산출물 2종 생성 → 완료 메시지 → 승인 대기

## 사전 판단: 카테고리별 적용성 (권장)

| 카테고리 | UOW-0F 적용성 | 근거 |
|---|---|---|
| Scalability | **N/A** | 로컬 stdio 단일 프로세스, 동시 부하 개념 없음 |
| Performance | 부분 | 대용량 처리는 UOW-01/02 소관. 0F는 직렬화·검증이 O(n) 선형·비차단이면 충분 |
| Availability | **N/A** | 상시 서비스 아님(도구 호출형) |
| Security | **적용** | 시크릿=env only, 경로 검증 계약, 로그 마스킹 (NFR-SEC-001/004/005) |
| Reliability | **적용** | 오류 계층·부분 실패 강등·결정성 (Resiliency Baseline) |
| Maintainability | **적용** | 계약 안정성·타입 명료·모듈 경계 (NFR-MAINT-002) |
| Testability | **적용** | PBT 속성(round-trip·멱등), LLMService 주입 가능 경계 |
| Observability | **적용** | 구조화 로깅(NFR-LOG-001)·구조화 warnings |
| Usability | 간접 | Result.summary 핵심 우선 계약(최종 사용자 UX는 UOW-05/06) |

---

## 질문 (Q — `[Answer]:` 태그에 기입) — 권장안 프리필

### Q1. 데이터 모델링 라이브러리
도메인 모델(Feature/Claim/… )과 구조화 검증(LLMService schema)에 무엇을 쓸까요?
- A) **Pydantic v2** — 검증·직렬화·JSON 스키마 생성 일체형, MCP/LLM 구조화 출력과 궁합 좋음 (권장)
- B) 표준 `dataclasses` + 수동 검증 — 의존성 최소, 검증 코드 직접 작성
- C) `attrs` + cattrs

[Answer]: A

### Q2. YAML Front Matter 처리 라이브러리
지식 파일(MD+YAML) 직렬화/역직렬화 도구는?
- A) **PyYAML**(`safe_load`/`safe_dump`) + 직접 Front Matter 분리 — 표준·경량, safe_load로 보안 (권장)
- B) `ruamel.yaml` — 주석/순서 보존 강하나 무거움
- C) `python-frontmatter` 라이브러리 — 편의성↑, 의존성 추가

[Answer]: A

### Q3. 결정성/재현성 보증 수준 (NFR-CORE-001, Hero 데모)
직렬화 산출물의 재현성을 어디까지 계약으로 강제할까요?
- A) **필드·리스트 순서 고정 + `sort_keys` 결정적 정렬** → 같은 입력=바이트 동일, PBT로 검증 (권장)
- B) 논리적 동등만 보장(순서 비보장)
- C) 순서 + 타임스탬프까지 고정(meta의 생성시각을 주입식으로)

[Answer]: A

### Q4. LLMService 구조화 출력 검증 실패 시 재시도 정책 기본값 (Resiliency)
`max_retries` 기본값과 재시도 방식은?
- A) **기본 2회, 제약 교정 프롬프트(스키마 오류 요약 첨부) 재프롬프트, 소진 시 LLMValidationError** (권장)
- B) 재시도 없음(1회) — 단순, 실패율↑
- C) 기본 3회 + 지수 백오프

[Answer]: A

### Q5. 로깅 구현 (NFR-LOG-001, Observability)
공통 로깅을 무엇으로?
- A) **표준 `logging` + 구조화(키=값) 포맷, 레벨 env로 조정** — 의존성 0, 충분 (권장)
- B) `structlog` — 구조화 강력하나 의존성 추가
- C) 커스텀 로거

[Answer]: A

### Q6. 시크릿 취급 재확인 (NFR-SEC-001) — 계약 강제 수준
- A) **`LLMSettings`에 키 값 저장 금지(이름만), 소비 직전 `os.environ` 조회, 미설정 시 ConfigError, 로그 마스킹** — 전부 강제 (권장)
- B) `.env` 파일 로드도 허용(python-dotenv) — 편의성↑
- (A와 B는 병행 가능: .env는 개발 편의, 값은 여전히 env로만 주입)

[Answer]: A (개발 편의용 .env 로드는 UOW-06에서 선택 검토)

### Q7. PBT 프레임워크 (Property-Based Testing 활성)
속성 기반 테스트 도구는?
- A) **Hypothesis** (Python 표준적 선택) — round-trip/멱등 속성 검증 (권장)
- B) 수동 속성 테스트(랜덤 없이 예시 기반)

[Answer]: A

### Q8. Python 버전 하한
- A) **Python 3.11+** — 최신 typing·tomllib 내장, MCP SDK 호환 (권장)
- B) 3.10+
- C) 3.12+

[Answer]: A

### Q9. 이 계획 승인
[Answer]: (예: "승인" 또는 변경요청)

---

## 다음 단계
답변 반영 후 `aidlc-docs/construction/uow-0f/nfr-requirements/`에 `nfr-requirements.md`·`tech-stack-decisions.md` 생성 → 완료 메시지 → 승인 시 UOW-0F **NFR Design**으로 진행.

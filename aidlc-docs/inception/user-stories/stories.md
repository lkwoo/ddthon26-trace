# TRACE — 사용자 스토리 (User Stories)

**단계**: INCEPTION / User Stories
**작성일**: 2026-09-08
**구성**: Epic(=UOW) 기반 + Epic 내부 User-Journey (Q3=A) · 중간 세분도(Q2=A) · Given/When/Then(Q4=A) · 추적성 표기(Q5=A)
**액터**: P1 데브, P2 마이라, P3 피엠, A1 에이전트(Claude Code) — 상세는 `personas.md`

> 규약: 각 스토리는 INVEST를 따르고 `Implements:`(FR/NFR)와 `UOW:` 매핑을 명시한다. 수용 기준은 Given/When/Then.

---

## EPIC UOW-01 — 프로젝트 스캐너 & 파서
*Implements: FR-PROJECT-001/002/003, FR-ANALYSIS-003*

### US-01.1 — 로컬 프로젝트 지정·로딩
**As** A1 에이전트, **I want** 로컬 프로젝트 경로를 지정해 TRACE를 시작 **so that** 대상 저장소를 분석 대상으로 삼는다.
- **AC1** Given 유효한 디렉터리 경로, When `analyze_project(path)` 호출, Then 프로젝트명과 감지된 자산 요약을 구조화 결과로 반환한다.
- **AC2** Given 존재하지 않거나 디렉터리가 아닌 경로, When 호출, Then 명확한 오류 메시지를 반환하고 분석을 시작하지 않는다. *(NFR-SEC-004 경로 검증)*
- *Implements: FR-PROJECT-001 · UOW: 01*

### US-01.2 — 지원 자산 탐색·분류
**As** A1 에이전트, **I want** 소스·MD/텍스트·PDF·OpenAPI·SQL·설정·테스트를 탐색·분류 **so that** 교차소스 근거를 확보한다.
- **AC1** Given 혼합 자산 저장소, When 스캔, Then 각 파일의 경로·산출물 유형·파일명·파싱 상태를 기록한다.
- **AC2** Given PDF 요구사항 문서, When 스캔, Then PDF도 파싱 대상(P0)으로 분류된다. *(Q3=B)*
- **AC3** Given `.git`/`node_modules`/`build`/`dist`/`target`/바이너리, When 스캔, Then 기본 제외 규칙으로 건너뛴다(설정 가능).
- *Implements: FR-PROJECT-002/003 · UOW: 01*

### US-01.3 — 부분 실패 허용
**As** P1 데브, **I want** 한 파일 파싱이 실패해도 분석이 계속되기 **so that** 일부 문제 파일 때문에 전체가 멈추지 않는다.
- **AC1** Given 파싱 불가 파일 1개, When 분석, Then 해당 파일을 경고로 표시·로깅하고 나머지 파일 분석을 계속한다.
- **AC2** Given 경고가 존재, When 분석 완료, Then 결과에 "경고와 함께 완료"임을 알린다.
- *Implements: FR-ANALYSIS-003, NFR-LOG-001 · UOW: 01*

---

## EPIC UOW-02 — Feature & Knowledge 생성
*Implements: FR-ANALYSIS-001, FR-KNOWLEDGE-001/002/003, FR-STORAGE-001*

### US-02.1 — 프로젝트 분석 실행
**As** A1 에이전트, **I want** 단일 도구 호출로 스캔→파싱→추출→Feature→Claim/Evidence→Conflict→지식→영속화를 수행 **so that** 이후 조회의 기반을 만든다.
- **AC1** Given 로드된 프로젝트, When `analyze_project`, Then 위 파이프라인을 수행하고 분석 요약(감지 Feature 수 등)을 반환한다.
- **AC2** Given 재실행, When 이전 지식 존재, Then 불필요한 LLM 재호출 없이 캐시를 활용한다. *(NFR-PERF-003)*
- *Implements: FR-ANALYSIS-001 · UOW: 02*

### US-02.2 — Hero Feature 자동 검출
**As** P1 데브, **I want** 시스템이 의미 있는 Feature를 자동 식별 **so that** 기능 단위로 시스템을 이해한다.
- **AC1** Given Petclinic 데모, When 분석, Then 최소 1개 Hero Feature(예: Owner Registration)를 정확히 식별한다. *(Q4=A 완전 자동)*
- **AC2** Given 식별된 Hero Feature, When 지식 생성, Then 최소 3개 산출물 범주(요구사항/API/코드/DB/설정/테스트)를 연관한다.
- *Implements: FR-KNOWLEDGE-001/003 · UOW: 02*

### US-02.3 — Feature Knowledge 뷰 생성·영속화
**As** P1 데브, **I want** 개요·비즈니스 규칙·코드·API·DB·설정·테스트·충돌·근거·의존성을 담은 지식 뷰 **so that** 여러 파일을 머릿속으로 잇지 않아도 된다.
- **AC1** Given 식별된 Feature, When 지식 생성, Then `knowledge/features/<id>.md`를 YAML Front Matter(구조화)+Markdown(설명)으로 저장한다.
- **AC2** Given 동일 가변 값, When 저장, Then 정규 YAML 필드에 한 번만 표현한다(단일 진실원).
- *Implements: FR-KNOWLEDGE-002, FR-STORAGE-001 · UOW: 02*

---

## EPIC UOW-03 — Claims / Evidence / Conflict
*Implements: FR-CLAIM-001, FR-EVIDENCE-001, FR-CONFIDENCE-001, FR-CONFLICT-001, FR-CONFLICT-OUT-001/002*

### US-03.1 — 정규화 Claim 추출
**As** A1 에이전트, **I want** 규칙을 원자적 `subject+predicate+value` Claim으로 추출 **so that** 교차소스 비교가 가능하다.
- **AC1** Given 요구사항/코드 규칙, When 추출, Then 복합 문장이 아닌 원자 Claim(예: `owner.telephone.max_length = 10`)으로 정규화된다.
- **AC2** Given 추출 결과, When 검증, Then 각 Claim은 subject/predicate/value 필드를 갖는다.
- *Implements: FR-CLAIM-001 · UOW: 03*

### US-03.2 — Evidence 연관
**As** P2 마이라, **I want** 각 중요 Claim에 근거 레코드가 붙기 **so that** 값의 출처를 추적한다.
- **AC1** Given 중요 Claim, When 근거 존재, Then 소스 경로·유형·(가능시)위치·추출값·관계(direct/supporting/related/contradicting)를 포함한 Evidence ≥1개를 연관한다.
- *Implements: FR-EVIDENCE-001, NFR-AI-002 · UOW: 03*

### US-03.3 — 값 불일치(Conflict) 검출
**As** P1 데브, **I want** 동일 Claim에 대한 소스 간 값 불일치를 검출 **so that** 문서-구현 드리프트를 착수 전에 안다.
- **AC1** Given 전화번호 max_length 요구사항 20 / OpenAPI 10 / 코드 10, When 분석, Then `value_mismatch` 충돌 1건을 검출한다.
- **AC2** Given 근거가 상충, When Confidence 산정, Then LLM 자기확신이 아닌 근거 일치도 기반으로 HIGH/MEDIUM/LOW를 부여한다. *(FR-CONFIDENCE-001 P1)*
- *Implements: FR-CONFLICT-001, FR-CONFIDENCE-001 · UOW: 03*

### US-03.4 — 충돌 조회·근거 참조
**As** A1 에이전트, **I want** `get_conflicts`로 충돌 수·상세·근거 소스를 조회 **so that** 사람에게 "왜"를 설명한다.
- **AC1** Given 검출된 충돌, When `get_conflicts(feature_id?)`, Then 충돌 수를 구조화 필드로, 상세(Claim/상충 값들/소스/위치/짧은 해석)를 반환한다.
- **AC2** Given 각 상충 값, When 결과 확인, Then 뒷받침 소스 파일 경로를 확인할 수 있다.
- *Implements: FR-CONFLICT-OUT-001/002, NFR-MCP-UX-001 · UOW: 03*

---

## EPIC UOW-04 — Task Impact Analysis
*Implements: FR-IMPACT-001~006*

### US-04.1 — 자연어 작업 입력·지식 기반 분석
**As** P3 피엠, **I want** 자연어 변경 요청을 넣으면 기존 지식·근거를 컨텍스트로 분석 **so that** 일반 추측이 아닌 근거로 영향을 본다.
- **AC1** Given "Add SMS verification to Owner registration", When `analyze_task_impact(task, feature_id?)`, Then 기존 Feature Knowledge/Evidence를 컨텍스트로 사용한다(일반 LLM 프롬프트 단독 금지).
- *Implements: FR-IMPACT-001/002 · UOW: 04*

### US-04.2 — 영향 분류(Must/Likely/Review) + 근거
**As** P1 데브, **I want** 영향 후보가 Must Change/Likely Change/Review로 분류되고 이유가 붙기 **so that** 무엇을 먼저 볼지 안다.
- **AC1** Given Hero Task, When 분석, Then 각 후보 파일/컴포넌트가 세 범주로 분류되고 각각 이유·근거 참조를 포함한다.
- **AC2** Given 근거 부족 항목, When 분류, Then 확신 대신 `Review`/`Insufficient evidence`/`Confidence: LOW`로 표기한다. *(NFR-AI-003)*
- *Implements: FR-IMPACT-003/005, NFR-AI-003 · UOW: 04*

### US-04.3 — 충돌 인지 영향 분석
**As** P2 마이라, **I want** 제출 작업과 관련된 기존 충돌을 변경 권고 전에 경고받기 **so that** 잘못된 명세 위에 구현하지 않는다.
- **AC1** Given 전화번호 길이 충돌이 미해소, When SMS 인증 작업 분석, Then 구현 권고 전에 해당 충돌을 강조·경고한다.
- *Implements: FR-IMPACT-004 (P1) · UOW: 04*

### US-04.4 — Change Plan 생성
**As** P1 데브, **I want** 순서형 Change Plan **so that** 안전한 착수 순서를 얻는다.
- **AC1** Given 영향 분석 완료, When 결과 반환, Then 근거 기반의 순서형 단계 목록(예: 검증 정책 해소→API 정의→흐름 수정→설정→테스트→문서)을 제공한다.
- **AC2** Given Change Plan, When 확인, Then 소스 코드를 자동 수정하지 않는다(자문용).
- *Implements: FR-IMPACT-006 · UOW: 04*

---

## EPIC UOW-05 — MCP 서버 인터페이스
*Implements: FR-STORAGE-002, FR-MCP-001~004, §12*

### US-05.1 — MCP 도구 노출(스키마+구조화 결과)
**As** A1 에이전트, **I want** 5개 도구를 명확한 입력 스키마와 JSON 결과로 호출 **so that** 안정적으로 소비한다.
- **AC1** Given MCP 연결, When 도구 목록 조회, Then `analyze_project`/`list_features`/`get_feature_knowledge`/`get_conflicts`/`analyze_task_impact`가 노출된다.
- **AC2** Given 각 도구, When 호출, Then 입력 스키마 검증 후 구조화(JSON) 결과를 반환한다.
- **AC3** Given 결과, When 렌더링, Then Feature 요약→Conflict→Impact→Evidence 순으로 핵심을 앞에 둔다. *(NFR-MCP-UX-002)*
- *Implements: FR-MCP-001, NFR-MCP-UX-002 · UOW: 05*

### US-05.2 — 지식 리소스 노출
**As** A1 에이전트, **I want** `knowledge/features/*.md`를 MCP 리소스로 읽기 **so that** 컨텍스트로 활용한다.
- **AC1** Given 생성된 지식, When 리소스 조회, Then YAML 구조화 필드는 도구 결과로, Markdown 본문은 리소스 콘텐츠로 수신한다.
- *Implements: FR-STORAGE-002, FR-MCP-002 · UOW: 05*

### US-05.3 — stdio 전송 & Claude Code 연동
**As** 평가자, **I want** README 스니펫으로 Claude Code에 TRACE를 연결 **so that** ~30초 안에 흐름을 재현한다.
- **AC1** Given README의 `.mcp.json` 스니펫, When 복붙·실행, Then stdio 전송으로 서버가 로컬 기동되고 Claude Code에 도구가 뜬다.
- **AC2** Given 예제 프롬프트, When 실행, Then Hero 흐름을 재현할 수 있다.
- *Implements: FR-MCP-004, NFR-MCP-UX-003 · UOW: 05*

### US-05.4 — 구현 전 검토 프롬프트 (P1)
**As** A1 에이전트, **I want** 재사용 MCP 프롬프트 템플릿 **so that** 코드 작성 전 TRACE 도구를 호출하도록 유도된다.
- **AC1** Given MCP 프롬프트, When 호출, Then "구현 착수 전 충돌·영향 검토" 절차를 안내한다.
- *Implements: FR-MCP-003 (P1) · UOW: 05*

---

## EPIC UOW-06 — 통합, 신뢰성 & 시연
*Implements: NFR-AI-003/004, NFR-REL-001/002, FR-DEMO-001/002, §17/§18/§20*

### US-06.1 — Hero 시나리오 E2E (DoD 앵커)
**As** P1 데브, **I want** Hero 시나리오를 수동 편집 없이 끝까지 통과 **so that** PoC 가치가 반복 시연된다.
- **AC1** Given Petclinic + 의도적 충돌, When analyze_project→get_feature_knowledge→get_conflicts→analyze_task_impact, Then 충돌 경고 + Must/Likely/Review + Change Plan까지 E2E로 완료된다. *(NFR-REL-001)*
- **AC2** Given 반복 실행, When 고정 데이터셋, Then 안정·반복 가능한 출력을 낸다. *(NFR-AI-004)*
- *Implements: NFR-REL-001, NFR-AI-004, §20 · UOW: 06*

### US-06.2 — 실패 처리 & 폴백
**As** P1 데브, **I want** AI/파서 실패 시 사람이 읽을 오류 + 캐시 폴백 **so that** 시연이 무너지지 않는다.
- **AC1** Given LLM 타임아웃/쿼터/오류, When 실패, Then 사용자 친화 오류 반환·이전 지식 보존·진단 로깅하고 가능시 재시도한다.
- **AC2** Given 라이브 실행 실패, When 폴백, Then 캐시된 분석 결과 및/또는 얇은 폴백 CLI로 재현한다. *(Q5=A)*
- *Implements: NFR-REL-002, NFR-AI-004, FR-DEMO-002, §17 · UOW: 06*

### US-06.3 — 턴키 시연 구성 + 스크린샷
**As** 평가자, **I want** 복붙 설정·예제 프롬프트·시연 스크린샷 **so that** 형태(MCP)에 맞는 사용성을 확인한다.
- **AC1** Given README, When 확인, Then 복붙 `.mcp.json` 스니펫과 Hero 예제 프롬프트가 있다.
- **AC2** Given 시연, When 완료, Then `result/`(또는 `screenshots/`)에 도구 호출→충돌 경고→Change Plan 장면 스크린샷이 존재한다.
- *Implements: FR-DEMO-001, §20 · UOW: 06*

### US-06.4 — 보안 위생
**As** 후속 개발자, **I want** 시크릿이 코드에 없고 로그에 노출되지 않기 **so that** 안전하게 이어받는다.
- **AC1** Given LLM API 키, When 설정, Then 환경변수/로컬 설정으로 주입되고 소스·로그에 하드코딩/노출되지 않는다.
- **AC2** Given 원시 프로젝트 파일, When 처리, Then LLM에 명시 전송분 외에는 로컬에 유지된다.
- *Implements: NFR-SEC-001/002/005, NFR-LOG-001 · UOW: 06*

---

## 추적성 요약 (Story → UOW → FR/NFR)

| Epic(UOW) | 스토리 수 | 대표 FR/NFR |
|---|---|---|
| UOW-01 | 3 | FR-PROJECT-001/002/003, FR-ANALYSIS-003 |
| UOW-02 | 3 | FR-ANALYSIS-001, FR-KNOWLEDGE-001/002/003, FR-STORAGE-001 |
| UOW-03 | 4 | FR-CLAIM-001, FR-EVIDENCE-001, FR-CONFIDENCE-001, FR-CONFLICT-001, FR-CONFLICT-OUT-001/002 |
| UOW-04 | 4 | FR-IMPACT-001~006 |
| UOW-05 | 4 | FR-MCP-001~004, FR-STORAGE-002 |
| UOW-06 | 4 | NFR-AI-003/004, NFR-REL-001/002, FR-DEMO-001/002, NFR-SEC-* |

**총 22개 스토리 / 6 Epic.** 모든 P0 FR과 핵심 NFR을 커버.

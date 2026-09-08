# 사용자 스토리 — Dual-Interface Knowledge Store

**출처 요구사항**: `aidlc-docs/inception/requirements/requirements.md`
**페르소나**: `aidlc-docs/inception/user-stories/personas.md` (P1 Agent, P2 Reviewer, P3 Installer)
**구성 방식**: Epic = FR 그룹, 하위에 페르소나 태그가 붙은 작은 스토리 (Epic-Based hybrid)
**형식**: Connextra 서술 + Gherkin(Given/When/Then) 인수 조건 + FR/NFR 추적
**범위**: MVP (요구사항 §6). §5 Out-of-Scope 항목 제외.

> 표기: **[P1]** Agent · **[P2]** Reviewer · **[P3]** Installer
> INVEST: 모든 스토리는 Independent·Negotiable·Valuable·Estimable·Small·Testable를 만족하도록 작성.

---

## Epic 1 — 다포맷 수집 & 청킹 (Multi-format Ingestion & Chunking) · FR-1

### US-1.1 [P1] 다포맷 문서 수집
**As an** Agent, **I want** 코드(다언어)·Markdown·PDF·xlsx·csv 파일을 MCP 도구로 수집 요청할 수 있기를, **so that** 대상 프로젝트의 지식을 저장소에 결정론적으로 적재할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 지원 포맷 파일 수집
  Given 대상 프로젝트에 .md, .pdf, .xlsx, .csv 및 소스 코드 파일이 존재하고
  When Agent가 해당 파일 경로로 수집(ingestion) 도구를 호출하면
  Then 서버는 포맷을 판별하여 텍스트/구조 콘텐츠를 결정론적으로 추출하고
  And 추출 결과를 청크로 저장할 준비 상태로 반환한다

Scenario: 미지원 포맷 처리
  Given PPT/HWP/이미지 등 지원 외 포맷 파일이 주어지고
  When 수집 도구가 호출되면
  Then 서버는 해당 포맷을 미지원으로 명확히 응답하고 저장을 수행하지 않는다
```
**Traceability**: FR-1.1, FR-1.4 · **Persona**: P1

### US-1.2 [P1] PDF 표 및 스프레드시트 데이터 추출
**As an** Agent, **I want** PDF 내 표와 xlsx/csv의 시트·표 데이터를 추출할 수 있기를, **so that** 표 형태 지식도 검색·연결 대상으로 삼을 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: PDF 문서 내 표 추출
  Given 텍스트와 표가 함께 있는 PDF가 주어지고
  When 수집 도구가 호출되면
  Then 본문 텍스트와 함께 표의 행/열 데이터가 별도 콘텐츠로 추출된다

Scenario: xlsx/csv 표 데이터 추출
  Given 다중 시트 xlsx 또는 csv 파일이 주어지고
  When 수집 도구가 호출되면
  Then 각 시트/표의 셀 데이터가 구조를 보존한 형태로 추출된다
```
**Traceability**: FR-1.2 · **Persona**: P1
**참고**: 심화 OCR·복잡한 차트/다이어그램 논리 복원은 §5에 따라 범위 외.

### US-1.3 [P1] 의미 단위 청킹
**As an** Agent, **I want** 수집한 문서가 의미 단위(섹션/문단/표 등)의 청크로 분절되기를, **so that** 이후 관계 연결·검색·요약·버전관리의 최소 단위를 청크로 다룰 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 문서를 의미 단위 청크로 분절
  Given 섹션과 문단, 표를 포함한 문서가 추출되었고
  When 청킹이 수행되면
  Then 각 청크는 의미 단위 경계로 분절되고 고유 식별자를 가진다
  And 각 청크는 원본 문서·위치 메타데이터를 보존한다

Scenario: 청킹 직렬화 왕복 불변 (PBT 대상)
  Given 임의의 유효한 문서 콘텐츠가 주어지고
  When 청킹 결과를 직렬화한 뒤 역직렬화하면
  Then 청크 집합과 메타데이터가 원본과 동일하다
```
**Traceability**: FR-1.3, NFR-8.2 · **Persona**: P1

---

## Epic 2 — 코드 구조 모델링 (Code Structure Modeling) · FR-2

### US-2.1 [P1][P2] tree-sitter 기반 코드 관계 추출
**As an** Agent(및 사람 검토자를 위한 데이터로서), **I want** tree-sitter로 다언어 소스의 파일/함수/클래스 간 관계(정의·호출·의존·상속/포함)를 추출하기를, **so that** 코드의 논리 구조를 LLM 호출 없이 결정론적으로 확보할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 다언어 소스에서 심볼 관계 추출
  Given tree-sitter가 지원하는 언어의 소스 파일들이 수집되었고
  When 구조 모델링이 실행되면
  Then 함수/클래스의 정의, 호출, 의존, 상속/포함 관계가 결정론적으로 추출된다
  And 동일 입력에 대해 실행 결과가 항상 동일하다(LLM-free)
```
**Traceability**: FR-2.1 · **Persona**: P1, P2 · **참고**: Graphify 추출기 로직 참고·이식(NFR-7).

### US-2.2 [P1][P2] 파일 간 심볼 해석 및 그래프 모델링
**As an** Agent, **I want** 파일 간 심볼 해석(symbol resolution)을 통해 코드 구조를 그래프로 저장하기를, **so that** 파일 경계를 넘는 논리적 의존을 조회·시각화할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 파일 간 심볼 참조 해석
  Given 서로 다른 파일에 정의·참조된 심볼들이 있고
  When 심볼 해석이 수행되면
  Then 참조가 정의로 연결되어 노드-엣지 그래프로 저장된다

Scenario: 해석 불가 심볼 처리
  Given 정의를 찾을 수 없는 외부/미해석 심볼이 있고
  When 심볼 해석이 수행되면
  Then 해당 참조는 미해석 상태로 표시되며 그래프 구성이 중단되지 않는다
```
**Traceability**: FR-2.2 · **Persona**: P1, P2

---

## Epic 3 — 관계 구축: 코드 ↔ 문서 청크 (Relationship Construction) · FR-3

### US-3.1 [P1] 임베딩/벡터 유사도 기반 연결
**As an** Agent, **I want** 서버 내장 로컬 임베딩 모델로 코드·청크 임베딩을 생성하고 sqlite-vec 유사도로 연결하기를, **so that** 외부 LLM/임베딩 API 없이 의미적으로 가까운 코드-문서를 연결할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 로컬 임베딩으로 코드-청크 연결
  Given 코드 심볼과 문서 청크가 저장되어 있고
  When 로컬 임베딩 모델이 각 임베딩을 생성하면
  Then 임베딩이 sqlite-vec에 저장되고 유사도 상위 관계가 연결로 기록된다
  And 임베딩 생성 과정에서 외부 네트워크 API 호출이 발생하지 않는다
```
**Traceability**: FR-3.1, NFR-3.1 · **Persona**: P1

### US-3.2 [P1] 마크다운 링크 파싱 기반 연결
**As an** Agent, **I want** 청크 내 명시적 마크다운 링크(`[[wikilink]]`·일반 링크)를 파싱해 참조 관계를 연결하기를, **so that** 저자가 의도한 명시적 참조를 지식 그래프에 반영할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: wikilink 및 일반 링크 파싱
  Given [[wikilink]]과 일반 마크다운 링크를 포함한 청크가 있고
  When 링크 파싱이 실행되면
  Then 각 링크가 대상 청크/문서로 해석되어 참조 관계로 저장된다

Scenario: 깨진 링크 처리
  Given 대상이 존재하지 않는 링크가 있고
  When 링크 파싱이 실행되면
  Then 해당 링크는 미해석 참조로 표시되고 처리가 계속된다
```
**Traceability**: FR-3.2 · **Persona**: P1

### US-3.3 [P1] 태그 기반 연결
**As an** Agent, **I want** 코드/청크의 태그 매칭으로 관계를 연결하기를, **so that** 동일 주제의 코드와 문서를 태그로 묶어 탐색할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 태그 매칭 연결
  Given 동일 태그를 가진 코드 심볼과 문서 청크가 있고
  When 태그 기반 관계 구축이 실행되면
  Then 같은 태그를 공유하는 항목들이 관계로 연결된다
```
**Traceability**: FR-3.3 · **Persona**: P1

---

## Epic 4 — 문서 버전 관리 (Document Versioning) · FR-4

### US-4.1 [P1] 청크 단위 대응 판별 (해시/텍스트 유사도)
**As an** Agent, **I want** 문서 추가 시 기존 청크와의 대응을 텍스트 유사도/해시(MinHash·편집거리)로 판별하기를, **so that** LLM 비용 없이 어떤 청크가 갱신되었는지 식별할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 유사 청크 대응 판별
  Given 기존 청크와 내용이 유사한 새 청크가 수집되고
  When 대응 판별이 수행되면
  Then 해시/텍스트 유사도 임계값에 따라 대응되는 기존 청크가 식별된다

Scenario: 해시 매칭 결정성 (PBT 대상)
  Given 동일한 청크 콘텐츠가 두 번 주어지고
  When 각각 해시/유사도 시그니처를 계산하면
  Then 두 시그니처가 동일하며 대응 판별 결과가 재현 가능하다
```
**Traceability**: FR-4.1, FR-4.2, NFR-2.2, NFR-8.2 · **Persona**: P1

### US-4.2 [P1] 청크 신규 버전 업데이트
**As an** Agent, **I want** 대응되는 기존 청크(OLD)가 존재하면 신규 버전(NEW)으로 업데이트되기를, **so that** 청크 이력을 보존하면서 최신 내용을 반영할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 대응 청크를 신규 버전으로 갱신
  Given 새 청크가 기존 청크(OLD ver)에 대응 판별되었고
  When 버전 업데이트가 수행되면
  Then 기존 청크는 신규 버전(NEW ver)으로 갱신되고 이전 버전 이력이 보존된다

Scenario: 대응 없는 신규 청크
  Given 어떤 기존 청크와도 대응되지 않는 새 청크가 있고
  When 버전 처리가 수행되면
  Then 해당 청크는 새로운 항목(버전 1)으로 저장된다
```
**Traceability**: FR-4.3 · **Persona**: P1

---

## Epic 5 — 요약 (Summarization, Agent 주도) · FR-5

### US-5.1 [P1] 요약 대상 콘텐츠 추출
**As an** Agent, **I want** 요약 대상 코드/문서 청크의 콘텐츠를 추출하는 도구를 호출하기를, **so that** 내가 그 내용을 받아 요약 텍스트를 생성할 수 있다(서버는 LLM 미호출).

**Acceptance Criteria**
```gherkin
Scenario: 요약 대상 콘텐츠 반환
  Given 저장된 청크/심볼 식별자가 주어지고
  When Agent가 요약 대상 추출 도구를 호출하면
  Then 서버는 해당 콘텐츠를 반환하며 자체적으로 LLM을 호출하지 않는다
```
**Traceability**: FR-5.2, NFR-3.1 · **Persona**: P1

### US-5.2 [P1] 요약 저장 및 조회
**As an** Agent, **I want** 내가 생성한 요약을 도구로 저장하고 다시 조회할 수 있기를, **so that** 요약이 지식 저장소에 영속화되어 이후 컨텍스트 제공에 재사용된다.

**Acceptance Criteria**
```gherkin
Scenario: Agent 생성 요약 저장
  Given Agent가 특정 청크에 대한 요약 텍스트를 생성했고
  When 요약 저장 도구를 청크 식별자와 함께 호출하면
  Then 요약이 해당 청크에 연결되어 저장된다

Scenario: 저장된 요약 조회
  Given 요약이 저장된 청크가 있고
  When 요약 조회가 요청되면
  Then 저장된 요약 텍스트가 반환된다
```
**Traceability**: FR-5.1 · **Persona**: P1

---

## Epic 6 — Agent 인터페이스: MCP Server (stdio) · FR-6

### US-6.1 [P1] MCP Resources 노출
**As an** Agent, **I want** 프로젝트 구조(Structure)·요약(Summary)·관계(Relationship) 데이터를 URI 형태의 MCP Resource로 접근하기를, **so that** 필요한 지식을 표준 방식으로 조회할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 리소스 URI 조회
  Given 지식 저장소에 구조/요약/관계 데이터가 있고
  When Agent가 해당 Resource URI를 요청하면
  Then 서버는 stdio를 통해 해당 데이터를 반환한다
```
**Traceability**: FR-6.1 · **Persona**: P1

### US-6.2 [P1] Semantic Query Tool
**As an** Agent, **I want** 의도(Intent) 기반으로 정보를 검색하는 도구를 호출하기를, **so that** 키워드가 아닌 의미로 관련 지식을 찾을 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 의도 기반 검색
  Given 임베딩과 관계가 구축된 지식 저장소가 있고
  When Agent가 자연어 의도로 Semantic Query 도구를 호출하면
  Then 의미적으로 관련된 청크/심볼이 관련도 순으로 반환된다
```
**Traceability**: FR-6.2, NFR-1.2 · **Persona**: P1

### US-6.3 [P1] Smart Snippet Tool (토큰 예산 인지)
**As an** Agent, **I want** 요청 컨텍스트의 토큰 양을 고려해 최적 코드 범위(Scope)를 잘라 받기를, **so that** 컨텍스트 윈도를 낭비하지 않고 필요한 코드만 확보한다.

**Acceptance Criteria**
```gherkin
Scenario: 토큰 예산에 맞춘 스니펫 반환
  Given 대상 심볼과 토큰 예산이 주어지고
  When Agent가 Smart Snippet 도구를 호출하면
  Then 반환 스니펫은 주어진 토큰 예산을 초과하지 않으면서 의미 단위 경계를 보존한다

Scenario: 예산이 매우 작을 때
  Given 전체 심볼보다 훨씬 작은 토큰 예산이 주어지고
  When Smart Snippet 도구가 호출되면
  Then 가장 관련성 높은 최소 범위가 반환되며 예산을 초과하지 않는다
```
**Traceability**: FR-6.2, NFR-1.2 · **Persona**: P1

### US-6.4 [P1] Ingestion/Update Tools
**As an** Agent, **I want** 문서·코드 수집, 청킹, 요약 저장, 위키 반영을 수행하는 도구를 호출하기를, **so that** interactive 방식으로 지식 저장소를 갱신할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 수집-청킹-저장-위키반영 파이프라인 호출
  Given 갱신할 파일 경로가 주어지고
  When Agent가 Ingestion/Update 도구를 호출하면
  Then 서버가 결정론적으로 파싱·청킹·저장하고 위키에 반영한다
  And 요약 텍스트가 필요한 부분은 Agent에게 위임된다(서버 LLM 미호출)
```
**Traceability**: FR-6.2, FR-5.1 · **Persona**: P1

---

## Epic 7 — 사람 인터페이스: Web Viewer (Static HTML + D3) · FR-7

### US-7.1 [P2] 인터랙티브 트리 뷰
**As a** Reviewer, **I want** 디렉토리 및 논리적 의존 구조를 접이식 트리로 시각화해 보기를, **so that** 대규모 코드베이스 구조를 빠르게 파악한다.

**Acceptance Criteria**
```gherkin
Scenario: 접이식 트리 탐색
  Given 지식 저장소에 구조 데이터가 있고
  When Reviewer가 Web Viewer의 트리 뷰를 열면
  Then 디렉토리/모듈이 접이식 D3 트리로 렌더링되고 노드를 펼치고 접을 수 있다
```
**Traceability**: FR-7.1 · **Persona**: P2 · **참고**: Graphify `tree_html.py` 스타일.

### US-7.2 [P2] 의존 관계 그래프 시각화
**As a** Reviewer, **I want** 코드 간 관계를 그래프로 시각화해 보기를, **so that** 컴포넌트 간 의존을 시각적으로 이해한다.

**Acceptance Criteria**
```gherkin
Scenario: 의존 그래프 렌더링
  Given 관계 데이터가 저장되어 있고
  When Reviewer가 의존 그래프 뷰를 열면
  Then 노드(심볼/파일)와 엣지(관계)가 D3 그래프로 렌더링된다
```
**Traceability**: FR-7.2 · **Persona**: P2

### US-7.3 [P2] 위키 콘텐츠 뷰어
**As a** Reviewer, **I want** 마크다운 기반 위키 콘텐츠를 렌더링해 읽기를, **so that** 요약·문서 지식을 사람이 읽기 좋은 형태로 확인한다.

**Acceptance Criteria**
```gherkin
Scenario: 마크다운 위키 렌더링
  Given 위키 콘텐츠(마크다운)가 저장되어 있고
  When Reviewer가 위키 뷰어에서 항목을 열면
  Then 마크다운이 HTML로 렌더링되어 표시된다
```
**Traceability**: FR-7.3 · **Persona**: P2

### US-7.4 [P2] 자동 갱신 결과 검토
**As a** Reviewer, **I want** 엔진/Agent가 자동 생성·업데이트한 위키 내용을 검토·확인하기를, **so that** 자동 갱신의 정확성과 최신성을 신뢰할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 자동 갱신 내용 확인
  Given Agent/엔진이 위키 청크를 갱신했고
  When Reviewer가 해당 항목을 위키 뷰어에서 열면
  Then 최신 버전 내용이 표시되고 갱신되었음을 확인할 수 있다
```
**Traceability**: FR-7.4, NFR-2.1 · **Persona**: P2
**참고**: 실시간 파일 감시/자동 동기화는 §5에 따라 범위 외(재인덱싱은 US-8.4 참조).

---

## Epic 8 — 배포 & 설치 (Deployment & Installation) · FR-8

### US-8.1 [P3] 복사형 설치 스크립트
**As an** Installer, **I want** 시스템을 대상 프로젝트 폴더에 복사하고 설정하는 설치 스크립트를 실행하기를, **so that** 복잡한 수동 설정 없이 도입할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 스크립트 실행 수준의 설치
  Given 대상 프로젝트 폴더와 최소 사전 요구사항이 충족되고
  When Installer가 설치 스크립트를 실행하면
  Then 시스템 파일이 대상 프로젝트에 복사되고 실행 가능한 상태로 설정된다
```
**Traceability**: FR-8.1, NFR-4.1 · **Persona**: P3

### US-8.2 [P3] 지식 저장소 위치 격리 (`.knowledge-store/`)
**As an** Installer, **I want** 지식 데이터가 대상 프로젝트 내부 숨김 디렉토리 `.knowledge-store/`에 저장되기를, **so that** 프로젝트 소스와 지식 데이터가 분리·격리된다.

**Acceptance Criteria**
```gherkin
Scenario: 숨김 디렉토리에 데이터 저장
  Given 설치가 완료된 대상 프로젝트가 있고
  When 지식 저장소(SQLite + sqlite-vec)가 초기화되면
  Then 데이터가 <target>/.knowledge-store/ 내부에 생성된다
```
**Traceability**: FR-8.2 · **Persona**: P3

### US-8.3 [P1][P3] MCP 클라이언트 자동 설정
**As an** Installer, **I want** Claude Code(`.mcp.json`)와 opencode에 MCP 설정이 자동 추가되기를, **so that** Agent가 즉시 시스템을 발견·사용할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 감지된 클라이언트 자동 설정
  Given 대상 환경에 Claude Code 또는 opencode가 감지되고
  When 설치 스크립트가 실행되면
  Then 해당 클라이언트의 MCP 설정에 이 서버(stdio) 항목이 자동 추가된다

Scenario: 감지 실패 시 수동 안내
  Given MCP 클라이언트가 감지되지 않고
  When 설치 스크립트가 실행되면
  Then README에 수동 설정 스니펫이 안내된다
```
**Traceability**: FR-8.3, NFR-5.1 · **Persona**: P3, P1

### US-8.4 [P3] Agent가 읽을 수 있는 설치 설명서 (README)
**As an** Installer, **I want** 사전 요구사항과 설치 절차가 `README.md`에 Agent가 읽고 수행 가능한 형태로 기술되기를, **so that** 사람이든 Agent든 최소 정보로 설치를 완료할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: Agent-readable 설치 설명서
  Given README.md가 제공되고
  When Agent 또는 사람이 README를 읽으면
  Then 최소화된 사전 요구사항과 단계별 설치·설정·재인덱싱 절차가 명확히 기술되어 있다
```
**Traceability**: FR-8.4, NFR-4.2, NFR-2.1 · **Persona**: P3

---

## Epic 9 — 사용자 관찰 가능 NFR 스토리 (User-observable NFRs)

### US-9.1 [P1] Agent Discoverability (자율 발견·활용)
**As an** Agent, **I want** 모든 Tools/Resources에 용도·입력·출력·사용 시점이 담긴 명확한 설명이 제공되기를, **so that** 별도 수동 안내 없이 시스템을 스스로 발견하고 적절한 시점에 호출할 수 있다.

**Acceptance Criteria**
```gherkin
Scenario: 자기설명적 도구 메타데이터
  Given MCP 서버가 연결되고
  When Agent가 도구/리소스 목록을 조회하면
  Then 각 항목에 용도·입력 스키마·출력·사용 시점을 설명하는 description이 포함되어 있다
  And Agent는 추가 수동 안내 없이 어떤 도구를 언제 쓸지 판단할 수 있다
```
**Traceability**: NFR-5.1, FR-6.3 · **Persona**: P1

### US-9.2 [P1] 저지연 핵심 조회
**As an** Agent, **I want** 핵심 조회 MCP 도구가 1초 이내로 응답하기를, **so that** 에이전트 루프가 지연으로 끊기지 않는다.

**Acceptance Criteria**
```gherkin
Scenario: 핵심 조회 응답 시간
  Given 대표 규모의 지식 저장소가 구축되어 있고
  When Agent가 Semantic Query 또는 Smart Snippet 등 핵심 조회 도구를 호출하면
  Then 응답이 1초 이내에 반환된다(목표치)
```
**Traceability**: NFR-1.1 · **Persona**: P1

### US-9.3 [P1] 토큰 효율적 결과
**As an** Agent, **I want** 모든 Resource·Tool 결과가 Smart Chunking·요약으로 불필요한 토큰을 최소화하기를, **so that** 제한된 컨텍스트 윈도를 효율적으로 사용한다.

**Acceptance Criteria**
```gherkin
Scenario: 토큰 낭비 최소화
  Given 조회 대상 지식이 있고
  When 어떤 Resource/Tool이 결과를 반환하면
  Then 전체 원문 대신 청크·요약·범위 제한된 콘텐츠가 반환되어 토큰 사용이 최소화된다
```
**Traceability**: NFR-1.2 · **Persona**: P1

### US-9.4 [P3] 간편 설치 (최소 사전 요구사항)
**As an** Installer, **I want** 설치가 스크립트 실행 수준으로 단순하고 사전 요구사항이 최소·명확하기를, **so that** 도입 장벽을 낮춘다.

**Acceptance Criteria**
```gherkin
Scenario: 최소 사전 요구사항으로 설치
  Given 문서화된 최소 사전 요구사항만 충족된 환경에서
  When Installer가 설치 스크립트를 실행하면
  Then 추가 수동 설정 없이 설치가 완료되고, 요구되는 사전 조건이 README에 명확히 문서화되어 있다
```
**Traceability**: NFR-4.1, NFR-4.2 · **Persona**: P3

---

## 추적성 요약 (Story → 요구사항)

| Story | 요구사항 | Persona |
|---|---|---|
| US-1.1 | FR-1.1, FR-1.4 | P1 |
| US-1.2 | FR-1.2 | P1 |
| US-1.3 | FR-1.3, NFR-8.2 | P1 |
| US-2.1 | FR-2.1 | P1, P2 |
| US-2.2 | FR-2.2 | P1, P2 |
| US-3.1 | FR-3.1, NFR-3.1 | P1 |
| US-3.2 | FR-3.2 | P1 |
| US-3.3 | FR-3.3 | P1 |
| US-4.1 | FR-4.1, FR-4.2, NFR-2.2, NFR-8.2 | P1 |
| US-4.2 | FR-4.3 | P1 |
| US-5.1 | FR-5.2, NFR-3.1 | P1 |
| US-5.2 | FR-5.1 | P1 |
| US-6.1 | FR-6.1 | P1 |
| US-6.2 | FR-6.2, NFR-1.2 | P1 |
| US-6.3 | FR-6.2, NFR-1.2 | P1 |
| US-6.4 | FR-6.2, FR-5.1 | P1 |
| US-7.1 | FR-7.1 | P2 |
| US-7.2 | FR-7.2 | P2 |
| US-7.3 | FR-7.3 | P2 |
| US-7.4 | FR-7.4, NFR-2.1 | P2 |
| US-8.1 | FR-8.1, NFR-4.1 | P3 |
| US-8.2 | FR-8.2 | P3 |
| US-8.3 | FR-8.3, NFR-5.1 | P3, P1 |
| US-8.4 | FR-8.4, NFR-4.2, NFR-2.1 | P3 |
| US-9.1 | NFR-5.1, FR-6.3 | P1 |
| US-9.2 | NFR-1.1 | P1 |
| US-9.3 | NFR-1.2 | P1 |
| US-9.4 | NFR-4.1, NFR-4.2 | P3 |

**요구사항 커버리지**: FR-1…FR-8 전부, 사용자 관찰 가능 NFR(NFR-1, NFR-4, NFR-5) 및 관련 NFR-2/NFR-3/NFR-8 참조 반영. §5 Out-of-Scope 항목은 스토리에서 제외(관련 스토리에 명시).

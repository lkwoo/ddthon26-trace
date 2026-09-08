# Requirements Verification Questions — Dual-Interface Knowledge Store

각 질문의 `[Answer]:` 태그 뒤에 알파벳(A, B, C ...)을 적어 답변해 주세요.
제시된 옵션이 맞지 않으면 마지막 옵션(Other)을 선택하고 설명을 적어 주세요.
모든 질문에 답한 뒤 "완료" 또는 "done"이라고 알려 주시면 다음 단계로 진행합니다.

---

## Question 1
구현 언어/런타임(Knowledge Engine + MCP Server의 주 언어)은 무엇으로 하시겠습니까? (참고 레퍼런스 Graphify/obsidian-wiki는 모두 Python 기반입니다.)

A) Python (참고 레퍼런스와 동일 — tree-sitter, MCP Python SDK 등 재사용 용이)

B) TypeScript / Node.js (MCP TS SDK, 웹 뷰어와 언어 통일)

C) Python(엔진/MCP) + TypeScript(웹 뷰어) 하이브리드

X) Other (please describe after [Answer]: tag below)

[Answer]: Python (참고 레퍼런스와 동일 — tree-sitter, MCP Python SDK 등 재사용 용이)

---

## Question 2
지식 저장소(코드 구조 그래프 + 문서 청크 + 관계)의 저장 백엔드는 무엇을 선호하십니까? (제약: 설치 간편성 우선, 로컬 파일시스템 환경)

A) 임베디드/파일 기반 (SQLite + 파일) — 별도 서버 불필요, 설치 최소화 (설치 간편성에 유리)

B) SQLite + 벡터 확장(sqlite-vec 등)으로 벡터 유사도까지 로컬 처리

C) 전용 그래프 DB(Neo4j 등) — 별도 실행 필요하나 그래프 질의 강력

D) 전용 벡터 DB(Chroma/Qdrant 등) + 그래프는 파일/SQLite 조합

X) Other (please describe after [Answer]: tag below)

[Answer]: SQLite + 벡터 확장(sqlite-vec 등)으로 벡터 유사도까지 로컬 처리

---

## Question 3
임베딩(벡터 유사도) 및 요약(Summarization)에 사용할 LLM/임베딩 제공자는 무엇으로 하시겠습니까? (제약: API 비용/지연 발생 가능)

A) Anthropic Claude (요약) + 외부 임베딩 API 조합

B) 로컬/오프라인 모델 우선 (예: 로컬 임베딩 모델, 요약도 로컬) — API 비용/외부 의존 최소화

C) 사용자가 설정으로 provider를 교체 가능한 추상화 계층(pluggable) — 기본값은 로컬, 옵션으로 API

D) OpenAI 등 특정 상용 API 고정

X) Other (please describe after [Answer]: tag below)

[Answer]: 별도 LLM 을 호출하지 않고, 대상 프로젝트에서 동작하는 Agent가 직접 임베딩(벡터 유사도) 및 요약(Summarization)하도록 함

---

## Question 4
MCP Server의 전송 방식(transport)은 무엇을 우선하시겠습니까?

A) stdio (로컬 에이전트/Claude Desktop·CLI 연동 표준, 설치 간편) — 참고 Graphify `serve.py`와 동일

B) HTTP/SSE (원격/네트워크 접근 가능)

C) 둘 다 지원 (stdio 기본 + HTTP 옵션)

X) Other (please describe after [Answer]: tag below)

[Answer]: stdio (로컬 에이전트/Claude Desktop·CLI 연동 표준, 설치 간편) — 참고 Graphify `serve.py`와 동일

---

## Question 5
Human Interface(Web Viewer)의 구현 방식은 무엇을 선호하십니까?

A) 정적 HTML + D3.js (빌드 도구 불필요, Graphify `tree_html.py` 스타일 — 설치/서빙 단순)

B) 경량 백엔드가 서빙하는 SPA (React/Vue 등) — 인터랙티브하지만 빌드 필요

C) 로컬 웹서버(FastAPI 등) + 서버 렌더링 마크다운 + D3 시각화

X) Other (please describe after [Answer]: tag below)

[Answer]: 정적 HTML + D3.js (빌드 도구 불필요, Graphify `tree_html.py` 스타일 — 설치/서빙 단순)

---

## Question 6
배포/설치 방식(요구사항 3.4 "Easy Installation")은 무엇을 1순위로 지향하시겠습니까?

A) 패키지 매니저 단일 설치 (예: `pip install` / `pipx` / `npx`)

B) 컨테이너(Docker) 원클릭 실행 (`docker run` / `docker compose up`)

C) 원클릭 설치 스크립트 (`curl | sh` 등)

D) 위를 복수 제공하되 A(패키지 매니저)를 기본으로

X) Other (please describe after [Answer]: tag below)

[Answer]: Agent를 사용해 설치하는 사용자들을 위해 Agent가 읽고 수행 가능한 설치 설명서를 README.md에 기술해야 하고, 설치 방식은 만들어진 시스템 구조를 대상 프로젝트 폴더 안에 복사한 후 환경에 맞는 mcp 설정 등을 자동으로 추가해 주는 스크립트 실행 방식이었으면 좋겠어. 모호한 점이 있다면 추가로 질문해줘.

---

## Question 7
코드 구조 관계 모델링(정의/호출/의존/상속)에서 MVP가 우선 지원할 프로그래밍 언어 범위는 어디까지로 하시겠습니까? (Graphify는 tree-sitter로 약 40개 언어 지원)

A) 소수 핵심 언어 우선 (예: Python, JavaScript/TypeScript) — MVP 집중

B) tree-sitter 기반으로 다수 언어 폭넓게 지원 (Graphify 추출기 재사용)

C) 이 프로젝트 자신을 파싱할 수 있는 언어 1개 우선(예: Python)부터 시작

X) Other (please describe after [Answer]: tag below)

[Answer]: tree-sitter 기반으로 다수 언어 폭넓게 지원 (Graphify 추출기 재사용)

---

## Question 8
참고 오픈소스(부록 B)의 활용 방향은 어떻게 하시겠습니까?

A) 두 레포(Graphify + obsidian-wiki)의 로직을 적극 참고·부분 이식 (라이선스 고지 준수)

B) 개념만 참고하고 코드는 신규 작성 (의존/이식 최소화)

C) 한쪽 위주로 활용 — 답변란에 어느 쪽(Graphify/obsidian-wiki) 우선인지 기재

X) Other (please describe after [Answer]: tag below)

[Answer]: 두 레포(Graphify + obsidian-wiki)의 로직을 적극 참고·부분 이식 (라이선스 고지 준수)

---

## Question 9
문서 청크 버전 관리에서 "기존 청크와 대응 판별(내용 비교)" 방식은 무엇을 기본으로 하시겠습니까? (제약 2.2: 판별 정확도에 따라 결과가 달라짐)

A) 임베딩 유사도 기반 매칭 (의미적으로 가장 가까운 기존 청크에 새 버전 연결)

B) 텍스트 유사도/해시 기반 매칭 (예: MinHash/편집거리 — LLM 비용 없음)

C) 두 방식 조합 (해시로 후보 축소 후 임베딩으로 확정)

X) Other (please describe after [Answer]: tag below)

[Answer]: 텍스트 유사도/해시 기반 매칭 (예: MinHash/편집거리 — LLM 비용 없음)

---

## Question: Security Extensions
Should security extension rules be enforced for this project?

A) Yes — enforce all SECURITY rules as blocking constraints (recommended for production-grade applications)

B) No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

X) Other (please describe after [Answer]: tag below)

[Answer]: No — skip all SECURITY rules (suitable for PoCs, prototypes, and experimental projects)

---

## Question: Property-Based Testing Extension
Should property-based testing (PBT) rules be enforced for this project?

A) Yes — enforce all PBT rules as blocking constraints (recommended for projects with business logic, data transformations, serialization, or stateful components)

B) Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

C) No — skip all PBT rules (suitable for simple CRUD applications, UI-only projects, or thin integration layers with no significant business logic)

X) Other (please describe after [Answer]: tag below)

[Answer]: Partial — enforce PBT rules only for pure functions and serialization round-trips (suitable for projects with limited algorithmic complexity)

---

## Question: Resiliency Extensions
Should the resiliency baseline be applied to this project?

**What this extension is.** Enabling it applies a set of **directional, design-time best practices** for building resilient systems, derived from the **AWS Well-Architected Framework (Reliability Pillar)** and resilience-review guidance. It steers requirements, design, and code toward fault tolerance, high availability, observability, and recoverability.

**What this extension is NOT.** Enabling it does **not** make your workload production-ready, nor does it certify or guarantee any availability, RTO, or RPO target. It is a **starting point**.

A) Yes — apply the resiliency baseline as directional best practices and design-time guidance (recommended for business-critical workloads)

B) No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

X) Other (please describe after [Answer]: tag below)

[Answer]: No — skip the resiliency baseline (suitable for PoCs, prototypes, and experimental projects where rapid iteration matters more than reliability)

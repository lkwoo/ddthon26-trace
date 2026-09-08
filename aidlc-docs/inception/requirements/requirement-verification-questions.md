# 요구사항 확인 질문 (Requirements Verification Questions)

각 질문의 `[Answer]:` 태그 뒤에 해당하는 **알파벳**을 적어주세요.
보기 중 맞는 것이 없으면 마지막 옵션(Other)을 고르고 `[Answer]:` 뒤에 직접 설명을 적어주세요.
답변이 모두 끝나면 "완료" 또는 "done"이라고 알려주세요.

---

## 기술 스택 (Technical Stack)

## Question 1
MCP 서버와 Knowledge Engine의 주 구현 언어/런타임은 무엇으로 할까요?

A) Python (MCP 파이썬 SDK + LLM/파싱 생태계 활용)

B) TypeScript / Node.js (MCP 공식 TS SDK 활용)

C) 혼합 — 엔진/파싱은 Python, 웹 뷰어는 TypeScript

X) Other (please describe after [Answer]: tag below)

[Answer]: Python (MCP 파이썬 SDK + LLM/파싱 생태계 활용)

## Question 2
Agent가 접근하는 MCP 서버의 전송 방식(Transport)은 무엇으로 할까요?

A) stdio (로컬 단일 사용자, Claude Desktop/Claude Code 등에서 직접 실행)

B) HTTP / SSE (네트워크를 통한 원격 접근 가능)

C) 둘 다 지원 (stdio + HTTP)

X) Other (please describe after [Answer]: tag below)

[Answer]: stdio (로컬 단일 사용자, Claude Desktop/Claude Code 등에서 직접 실행)

## Question 3
생성된 지식(요약, 구조, 관계 그래프)의 저장 방식(Persistence)은 무엇을 선호하시나요?

A) 파일 기반 (Markdown + JSON, Git 친화적)

B) SQLite (단일 파일 임베디드 DB)

C) 그래프 DB (Neo4j 등)

D) 벡터 DB + 메타데이터 DB 조합

X) Other (please describe after [Answer]: tag below)

[Answer]: 파일 기반 (Markdown + JSON, Git 친화적)

---

## LLM 및 시맨틱 검색 (LLM & Semantic Search)

## Question 4
코드/문서 요약 및 지능형 분석에 사용할 LLM 제공자는 무엇으로 할까요?

A) Anthropic Claude

B) OpenAI

C) 로컬 LLM (Ollama 등)

D) 제공자 추상화 — 설정으로 교체 가능하게 설계

X) Other (please describe after [Answer]: tag below)

[Answer]: 제공자 추상화 — 설정으로 교체 가능하게 설계

## Question 5
MVP에서 "의미 기반 검색(Semantic Query)"을 어느 수준까지 구현할까요?

A) 임베딩 기반 벡터 검색 완전 구현 (semantic similarity)

B) 키워드 + 코드 구조(그래프) 기반 검색부터 시작, 임베딩은 이후 단계

C) 하이브리드 (키워드 + 임베딩 혼합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 키워드 + 코드 구조(그래프) 기반 검색부터 시작, 임베딩은 이후 단계

---

## 인제스천 및 그래프 (Ingestion & Graph)

## Question 6
MVP에서 코드 관계 그래프(Call Graph, 의존성) 분석 대상 언어 범위는 어디까지로 할까요?

A) Python 한 가지만

B) Python + JavaScript/TypeScript

C) 다국어 확장형 (tree-sitter 등 파서 기반으로 언어 추가 가능한 구조)

X) Other (please describe after [Answer]: tag below)

[Answer]: 다국어 확장형 (tree-sitter 등 파서 기반으로 언어 추가 가능한 구조)

## Question 7
제약사항 문서에 따르면 MVP 인제스천 포맷은 "소스 코드 + Markdown"이 필수이고 PDF/HTML/PPT는 이후 단계로 명시되어 있습니다. 이 범위가 맞나요?

A) 예 — MVP는 코드 + Markdown만 (확인)

B) 아니오 — 코드 + Markdown + PDF까지 MVP에 포함

C) 아니오 — 전체 포맷(PDF/HTML/PPT 포함) MVP에 포함

X) Other (please describe after [Answer]: tag below)

[Answer]: 예 — MVP는 코드 + Markdown만 (확인)

---

## 웹 뷰어 (Human Interface)

## Question 8
사람용 Web Viewer의 기술 스택은 무엇을 선호하시나요?

A) React / Next.js 기반 SPA (인터랙티브 트리 + 그래프 시각화에 유리)

B) 경량 서버사이드 렌더링 (Markdown 정적 렌더 위주, 최소 의존성)

C) 미정 — 추천을 원함

X) Other (please describe after [Answer]: tag below)

[Answer]: 경량 서버사이드 렌더링 (Markdown 정적 렌더 위주, 최소 의존성)

---

## 사용 환경 및 정책 (Environment & Policy)

## Question 9
이 시스템의 주 사용 환경/사용자 모델은 무엇인가요?

A) 단일 개발자의 로컬 환경

B) 팀 공유 (네트워크 드라이브 또는 서버에서 다수 사용자 접근)

C) 둘 다 지원

X) Other (please describe after [Answer]: tag below)

[Answer]: 단일 개발자의 로컬 환경

## Question 10
사람이 위키를 수동 수정(Manual Edit)한 내용과 엔진의 자동 업데이트가 충돌할 때, 어떤 정책을 기본으로 할까요?

A) 사람 편집 우선 — 수동 수정 내용을 보존, 자동 업데이트가 덮어쓰지 않음

B) 엔진 우선 — 소스 코드 기준으로 자동 재생성(수동 수정은 재동기화 시 사라질 수 있음)

C) 수동 재동기화 트리거 방식 — 명시적 재동기화 명령 시에만 병합/갱신

X) Other (please describe after [Answer]: tag below)

[Answer]: B) 엔진 우선 — 소스 코드 기준으로 자동 재생성(수동 수정은 재동기화 시 사라질 수 있음)

---

## 확장 기능 옵트인 (Extension Opt-In)

## Question 11: 보안 확장 (Security Extensions)
이 프로젝트에 보안 확장 규칙(Security Baseline)을 강제 적용할까요?

A) 예 — 모든 SECURITY 규칙을 차단(blocking) 제약으로 강제 적용 (프로덕션 등급 애플리케이션 권장)

B) 아니오 — 모든 SECURITY 규칙 생략 (PoC, 프로토타입, 실험적 프로젝트에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 아니오 — 모든 SECURITY 규칙 생략 (PoC, 프로토타입, 실험적 프로젝트에 적합)

## Question 12: 복원력 확장 (Resiliency Extensions)
이 프로젝트에 복원력 기준(Resiliency Baseline)을 적용할까요?

**이 확장이 하는 것:** AWS Well-Architected Framework(Reliability Pillar)에서 도출된 **설계 시점의 방향성 있는 모범 사례**를 적용합니다. 요구사항/설계/코드를 결함 허용성, 고가용성, 관측성, 복구성 방향으로 유도합니다.

**이 확장이 하지 않는 것:** 워크로드를 프로덕션 준비 완료로 만들거나, 특정 가용성/RTO/RPO 목표를 보증하지 않습니다. 정식 Well-Architected Review를 대체하지 않는 **출발점**입니다.

A) 예 — 복원력 기준을 설계 시점 방향성 지침으로 적용 (비즈니스 크리티컬 워크로드 권장)

B) 아니오 — 복원력 기준 생략 (빠른 반복이 중요한 PoC/프로토타입에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 아니오 — 복원력 기준 생략 (빠른 반복이 중요한 PoC/프로토타입에 적합)

## Question 13: 속성 기반 테스트 확장 (Property-Based Testing)
이 프로젝트에 속성 기반 테스트(PBT) 규칙을 강제 적용할까요?

A) 예 — 모든 PBT 규칙을 차단 제약으로 강제 (비즈니스 로직, 데이터 변환, 직렬화, 상태 저장 컴포넌트가 있는 프로젝트 권장)

B) 부분 — 순수 함수와 직렬화 왕복(round-trip)에만 PBT 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

C) 아니오 — 모든 PBT 규칙 생략 (단순 CRUD, UI 전용, 얇은 통합 계층에 적합)

X) Other (please describe after [Answer]: tag below)

[Answer]: 부분 — 순수 함수와 직렬화 왕복(round-trip)에만 PBT 적용 (알고리즘 복잡도가 제한적인 프로젝트에 적합)

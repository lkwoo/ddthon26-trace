# Unit of Work — 정의 및 코드 조직 전략

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Units Generation (Part 2: Generation)
> **작성일**: 2026-09-08
> **입력 산출물**: `unit-of-work-plan.md`(승인됨), `application-design/*`, `stories.md`
> **분해 결정(플랜 확정)**: Q1=서브시스템별, Q2=공유 서비스는 Engine Core, Q3=CLI·Assembly 독립 Unit, Q4=**4개 Unit**, Q5=U1→U2→U3→U4, Q6=Unit 내부 테스트+공용 PBT는 U1, Q7=**src-layout**
> **정의**: Unit of Work = 개발 목적의 스토리 논리 그룹. 본 프로젝트는 **모놀리식 단일 패키지(단일 배포)** 이므로 각 Unit은 독립 배포 서비스가 아닌 **논리 모듈(Module)** 이다.

---

## 1. Unit 개요 (4-Unit 분해)

| Unit | 이름 | 유형 | 핵심 책임 | 의존 |
|---|---|---|---|---|
| **U1** | **Engine Core** | 논리 모듈(코어) | 순수 도메인 + 포트 + 아웃바운드 어댑터 + Application 서비스(Sync/Read/Query/Snippet/Update) | 없음 |
| **U2** | **MCP Server** | 논리 모듈(인바운드 어댑터) | stdio MCP Resources/Tools/Prompts로 U1 서비스 노출 | U1 |
| **U3** | **Web Viewer** | 논리 모듈(인바운드 어댑터) | SSR 웹(트리/위키/그래프/검토)으로 U1 읽기 서비스 노출 | U1 |
| **U4** | **CLI & Assembly** | 논리 모듈(조립 루트/진입점) | 서브커맨드 CLI + DI 조립(config/`__main__`)로 전 Unit 통합·기동 | U1, U2, U3 |

**개발 순서(Q5=A)**: **U1 → U2 → U3 → U4** (의존 순). 각 Unit은 per-unit 설계·코드 루프를 완료한 뒤 다음 Unit으로 진행.

---

## 2. Unit별 상세 정의

### U1 — Engine Core
- **범위(모듈)**:
  - `domain/` — Models, GraphBuilder, StructuredExtractor, ChunkingService, QueryEngine (순수·결정적·LLM 미호출·I/O 없음)
  - `ports/` — FileSourcePort, LanguageParserPort, KnowledgeStorePort (추상 계약)
  - `adapters/outbound/` — FileSystemSource, ParserRegistry+TreeSitter, FileSystemKnowledgeStore (포트 구현)
  - `application/` — SyncService, KnowledgeReadService, QueryService, SnippetService, UpdateService (유즈케이스 조율)
  - `testing/` — 공용 PBT 설정·제너레이터(Q6=A, US-N6, 도메인 모델/직렬화용)
- **책임**: 인제스천·그래프·구조 추출·저장·검색·스니펫·에이전트 노트 병합의 **모든 로직**. 인터페이스와 독립적으로 완성·테스트 가능(PBT 대상 격리).
- **주 스토리**: US-E1~E5, US-A2/A3/A4(서비스 로직), US-N2~N7
- **핵심 원칙**: 도메인은 무엇에도 의존하지 않음. 파일/전송/외부 상호작용은 아웃바운드 어댑터에 격리(NFR-C3, US-N6 PBT 지점 명확화).

### U2 — MCP Server
- **범위(모듈)**: `adapters/inbound/mcp/` — ResourcesProvider, ToolsProvider(query/snippet/update/sync), PromptsProvider, StdioTransport
- **책임**: U1의 Read/Query/Snippet/Update/Sync 서비스를 **얇은 MCP 어댑터**로 노출. 로직 미보유(위임만).
- **주 스토리**: US-A1, US-A5, US-A6, US-N1(표면 계측)
- **의존**: U1 (Application 서비스 인터페이스)

### U3 — Web Viewer
- **범위(모듈)**: `adapters/inbound/web/` — SSR 라우트/렌더러(트리 뷰, 위키 콘텐츠, 의존성 그래프, 콘텐츠 검토)
- **책임**: U1의 KnowledgeReadService를 **SSR 웹 UI**로 노출. 최소 의존성 서버사이드 Markdown 렌더 위주.
- **주 스토리**: US-H1~H4 (FR-H5 SSR 포함)
- **의존**: U1 (KnowledgeReadService)

### U4 — CLI & Assembly
- **범위(모듈)**: `adapters/inbound/cli/`, `config.py`, `__main__.py`
- **책임**: 서브커맨드(`ingest`/`sync`/`serve-mcp`/`serve-web`) 진입점 + **DI 조립 루트**(구현체 바인딩·주입). 컴포넌트 직접 결합 방지.
- **주 스토리**: US-A6(serve), US-E1/E5(ingest/sync), US-N7(규모·소요 출력)
- **의존**: U1, U2(serve-mcp 조립), U3(serve-web 조립)

---

## 3. 코드 조직 전략 (Greenfield, Q7=A src-layout)

> **CRITICAL(CLAUDE.md)**: 애플리케이션 코드는 워크스페이스 루트에 위치(절대 `aidlc-docs/` 내부 금지). 문서만 `aidlc-docs/`.

```
<workspace-root>/
├── pyproject.toml                 # 패키징·의존성(hatchling/pdm 등), Hypothesis 등 dev 의존
├── README.md
├── src/
│   └── agentic_kb/                # 단일 배포 패키지 (모놀리식)
│       ├── __init__.py
│       ├── __main__.py            # [U4] 진입점 (python -m agentic_kb)
│       ├── config.py              # [U4] 설정 + DI 조립 루트
│       ├── domain/                # [U1] 순수 도메인 (models, graph_builder, extractor, chunking, query_engine)
│       │   └── __init__.py
│       ├── ports/                 # [U1] 추상 포트 (file_source, language_parser, knowledge_store)
│       │   └── __init__.py
│       ├── application/           # [U1] 서비스 (sync, read, query, snippet, update)
│       │   └── __init__.py
│       ├── adapters/
│       │   ├── outbound/          # [U1] 포트 구현 (filesystem_source, parser_registry, filesystem_store)
│       │   │   └── __init__.py
│       │   └── inbound/
│       │       ├── mcp/           # [U2] MCP 어댑터
│       │       │   └── __init__.py
│       │       ├── web/           # [U3] SSR 웹 뷰어
│       │       │   └── __init__.py
│       │       └── cli/           # [U4] CLI 서브커맨드
│       │           └── __init__.py
│       └── testing/               # [U1] 공용 PBT 설정·제너레이터(US-N6)
│           └── __init__.py
└── tests/                         # 각 Unit 내부 테스트를 미러 구조로 배치(Q6=A)
    ├── conftest.py                # 공용 fixture (Hypothesis 프로파일 등)
    ├── unit/
    │   ├── domain/                # [U1] 순수 로직 + PBT (round-trip PBT-02, invariant PBT-03)
    │   ├── application/           # [U1] 서비스 단위 테스트(포트 목/스텁)
    │   ├── adapters_outbound/     # [U1] 아웃바운드 어댑터 테스트
    │   ├── mcp/                   # [U2]
    │   ├── web/                   # [U3]
    │   └── cli/                   # [U4]
    └── integration/               # Build & Test 단계: Unit 간 상호작용(조립 후 end-to-end)
```

**전략 요지**
- **단일 패키지·헥사고날**: 하나의 배포 단위 안에서 Unit은 디렉토리(모듈) 경계로 표현. 의존은 안쪽(도메인)으로만.
- **테스트 배치(Q6=A)**: 각 Unit의 테스트는 `tests/unit/<unit>` 아래에 두고, **공용 PBT 설정/제너레이터는 `src/agentic_kb/testing/`(U1)** 에 둔다. 통합 테스트는 Build & Test 단계에서 `tests/integration/`.
- **PBT 강제(부분)**: PBT-02/03/07/08/09는 차단. Hypothesis 사용, 실패 시 shrinking + 재현 시드(PBT-08/09). 대상은 U1 도메인 모델 직렬화(round-trip)·순수 변환 불변식.
- **조립 격리(U4)**: 구현체 선택·주입은 `config.py`/`__main__.py`에서만. 서비스는 포트 추상에만 의존.

---

## 4. Unit 경계·의존 검증

- **의존 방향**: U2/U3/U4(어댑터·조립) → U1(코어). U1은 어느 Unit에도 의존하지 않음.
- **순환 없음**: U1은 leaf(의존 대상 없음). U2, U3는 U1만 의존. U4는 U1/U2/U3를 조립하지만 U2/U3는 U4를 참조하지 않음 → 단방향(DAG). ✔
- **인터페이스 안정성**: U2/U3는 U1의 **Application 서비스 인터페이스**에만 결합. U1 내부 도메인 변경이 어댑터로 새지 않음.
- **테스트 독립성**: U1은 인터페이스(U2/U3/U4) 없이 완성·검증 가능 → 개발 순서 U1 선행이 타당.

상세 매트릭스·다이어그램은 `unit-of-work-dependency.md` 참조.

---

## 5. 스토리 배정 완결성

모든 MVP 스토리(US-A/H/E/N)가 정확히 하나의 주 Unit에 배정됨. Backlog(US-F1~F5)는 MVP 범위 밖으로 명시. 전수 매핑은 `unit-of-work-story-map.md` 참조.

---

## 6. 확장(Extension) 컴플라이언스 요약

| Extension | 상태 | 본 단계 적용 판정 |
|---|---|---|
| Security Baseline | Disabled(Opt-out) | N/A — 미적용 확장 |
| Resiliency Baseline | Disabled(Opt-out) | N/A — 미적용 확장 |
| Property-Based Testing (Partial) | Enabled(Partial) | **적용** — Q6=A로 PBT 대상(U1 도메인 직렬화 round-trip/순수 변환 불변식)을 U1에 격리 배치하고 공용 PBT 설정을 `src/agentic_kb/testing/`에 둠. PBT-02/03(대상 명확화) 충족, PBT-07/08/09(프레임워크·생성기·재현성)는 Code Generation/NFR 단계 강제로 인계. 본 분해 단계 차단 위반 없음. |

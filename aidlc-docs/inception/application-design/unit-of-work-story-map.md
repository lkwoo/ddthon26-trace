# Unit of Work — 스토리 매핑

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Units Generation (Part 2: Generation)
> **작성일**: 2026-09-08
> **목적**: 모든 사용자 스토리(US-A/H/E/N)를 Unit에 배정하고 커버리지 완결성을 검증한다.
> **입력**: `stories.md`, `unit-of-work.md`, `component-dependency.md`

---

## 1. 스토리 → Unit 배정표

| 스토리 | 요약 | 주 Unit | 보조 Unit(표면/계측) | 근거 |
|---|---|---|---|---|
| **US-A1** | MCP Resources 노출(구조·요약·관계) | **U2** | U1(KnowledgeReadService 로직) | MCP ResourcesProvider가 U1 읽기 서비스를 노출 |
| **US-A2** | Semantic Query Tool | **U1** | U2(Tool 표면) | 검색 로직=QueryService/QueryEngine(U1), MCP는 위임 |
| **US-A3** | Smart Snippet Tool | **U1** | U2(Tool 표면) | 스니펫 로직=SnippetService/ChunkingService(U1) |
| **US-A4** | Update Tool(에이전트 노트 저장) | **U1** | U2(Tool 표면) | 검증·저장 로직=UpdateService(U1), 별도 네임스페이스 |
| **US-A5** | MCP Prompts(온보딩·작업별) | **U2** | — | PromptsProvider(MCP 어댑터 전용) |
| **US-A6** | MCP 서버 stdio 연결 | **U2** | U4(serve-mcp 조립) | StdioTransport(U2), 기동은 CLI 조립(U4) |
| **US-H1** | Interactive Tree View | **U3** | U1(구조 데이터) | Web SSR 트리 렌더 |
| **US-H2** | Wiki Content Viewer(SSR) | **U3** | U1(위키 콘텐츠) | Markdown SSR 렌더(FR-H5) |
| **US-H3** | Dependency Visualization | **U3** | U1(관계 그래프) | Web 그래프 시각화 |
| **US-H4** | Content Review(엔진 산출 검토) | **U3** | U1(읽기 서비스) | Web 검토 + 엔진 우선 고지 |
| **US-E1** | Multi-format Ingestion | **U1** | U4(ingest 진입점) | SyncService + FileSystemSource(U1) |
| **US-E2** | Graph Construction(tree-sitter) | **U1** | — | ParserRegistry+GraphBuilder(U1) |
| **US-E3** | 결정적 구조 추출(LLM 미호출) | **U1** | — | StructuredExtractor(U1, 순수) |
| **US-E4** | Persistence(Markdown+JSON) | **U1** | — | FileSystemKnowledgeStore(U1) |
| **US-E5** | Re-sync(재동기화, 엔진 우선) | **U1** | U2(sync_tool 표면), U4(sync 진입점) | SyncService(resync)=U1 |
| **US-N1** | 응답 지연 최소화 | **U1** | U2(표면 계측) | KnowledgeReadService 계측 훅(U1) |
| **US-N2** | 토큰 효율 | **U1** | — | ChunkingService/요약(U1) |
| **US-N3** | 엔진 로컬성/결정성 | **U1** | — | 순수 도메인 + 어댑터 격리(U1) |
| **US-N4** | 파서 확장성 | **U1** | — | LanguageParserPort + ParserRegistry(U1) |
| **US-N5** | Git 친화 로컬 저장 | **U1** | — | 결정적 Markdown+JSON 직렬화(U1) |
| **US-N6** | 속성 기반 테스트(부분 PBT) | **U1** | — | 공용 PBT 설정=`src/agentic_kb/testing/`, 대상=U1 도메인 |
| **US-N7** | 자원 인지(SyncReport) | **U1** | U4(CLI 출력) | SyncReport 생성=U1, 표시=CLI(U4) |

---

## 2. Unit별 스토리 집계

| Unit | 주 배정 스토리 | 개수 |
|---|---|---|
| **U1 Engine Core** | US-A2, US-A3, US-A4, US-E1, US-E2, US-E3, US-E4, US-E5, US-N1, US-N2, US-N3, US-N4, US-N5, US-N6, US-N7 | **15** |
| **U2 MCP Server** | US-A1, US-A5, US-A6 | **3** |
| **U3 Web Viewer** | US-H1, US-H2, US-H3, US-H4 | **4** |
| **U4 CLI & Assembly** | (주 배정 없음 — 조립/진입점 Unit) | **0** |

> **U4 참고**: U4는 신규 기능 스토리를 "소유"하지 않고 US-A6(serve), US-E1/E5(ingest/sync 진입점), US-N7(출력)을 **보조(진입점·조립)** 로 실현한다. 순수 조립 Unit의 성격상 주 배정 0은 정상이며, per-unit 코드 생성 시 U1/U2/U3 조립·CLI 표면으로 다뤄진다.

---

## 3. 커버리지 완결성 검증

- **MVP 스토리 총계**: US-A(6) + US-H(4) + US-E(5) + US-N(7) = **22개**
- **배정 완료**: 22/22 — 모든 스토리가 정확히 하나의 주 Unit(또는 조립 Unit U4)에 배정됨. ✔
- **미배정 스토리**: 없음. ✔
- **중복/모호 배정**: 없음(로직은 U1, 표면은 U2/U3, 조립은 U4로 일관 규칙 적용). ✔

### 범위 밖(Backlog, MVP 제외)
| 스토리 | 요약 | 처리 |
|---|---|---|
| US-F1 | 임베딩 벡터 시맨틱 검색 | Backlog — Unit 미배정(범위 밖) |
| US-F2 | PDF/HTML/PPT 인제스천 | Backlog — Unit 미배정(범위 밖) |
| US-F3 | 실시간 파일 감시·자동 재동기화 | Backlog — Unit 미배정(범위 밖) |
| US-F4 | CI/CD 파이프라인 통합 | Backlog — Unit 미배정(범위 밖) |
| US-F5 | 메신저 알림 연동 | Backlog — Unit 미배정(범위 밖) |

---

## 4. 배정 규칙 요약(일관성 근거)

1. **로직은 코어(U1)**: 검색/스니펫/업데이트/읽기/동기화의 실제 로직은 모두 U1 Application 서비스에 위치.
2. **표면은 어댑터(U2/U3)**: MCP·Web은 U1 서비스를 노출하는 얇은 인바운드 어댑터.
3. **진입·조립은 U4**: CLI 서브커맨드와 DI 조립은 U4가 담당(기능 로직 미보유).
4. **NFR/교차관심사**: 대부분 U1에 계측·구현, 사용자 표면 노출은 해당 어댑터/조립 Unit에서.

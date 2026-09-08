# Services — Application Design

> **프로젝트**: Agentic Knowledge Base (MCP-based)
> **단계**: INCEPTION – Application Design (Part 2: Generation)
> **작성일**: 2026-09-08
> **서비스 계층 원칙**: 애플리케이션 서비스는 **유즈케이스 오케스트레이션**만 담당하고, 순수 로직은 도메인에, I/O는 포트/어댑터에 위임한다(헥사고날, Q7=A).

---

## 1. 서비스 인벤토리

| 서비스 | 유형 | 책임 | 의존(포트/도메인) | 소비 어댑터 |
|---|---|---|---|---|
| **SyncService** | 쓰기(파이프라인) | 인제스천→파싱→그래프→추출→저장 조율, 재동기화 | FileSourcePort, ParserRegistry, GraphBuilder, StructuredExtractor, KnowledgeStorePort | CLI(`sync`/`ingest`), MCP `sync_tool`(Q5=B) |
| **KnowledgeReadService** | 읽기(파사드) | 구조/요약/관계 조회, 에이전트 노트 병합, 지연 계측 | KnowledgeStorePort | MCP Resources, Web Viewer (Q2=A 공유) |
| **QueryService** | 읽기 | 키워드+그래프 검색 조율 | KnowledgeStorePort, QueryEngine | MCP `query_tool` |
| **SnippetService** | 읽기 | 토큰 예산 스니펫 조율 | FileSourcePort/Store, ChunkingService | MCP `snippet_tool` |
| **UpdateService** | 쓰기 | 에이전트 노트 검증·별도 네임스페이스 저장 | KnowledgeStorePort | MCP `update_tool` |

> 공유 원칙(Q2=A): **KnowledgeReadService**가 MCP Resources와 Web Viewer의 **단일 읽기 진입점**이다. 두 인터페이스는 저장 파일을 직접 읽지 않는다.

---

## 2. 핵심 오케스트레이션 흐름

### 2.1 SyncService 파이프라인 (US-E1~E5)

```
텍스트 흐름 (SyncService.run):
1. FileSource.discover(root)      → 지원 포맷 필터, 미지원 건너뜀 (US-E1 AC-2)
2. for each file:
     parser = ParserRegistry.for_file(path)
     if parser is None: skip + record (US-E2 AC-3)
     unit = parser.parse(file)
3. graph = GraphBuilder.build(all_units)         (순수/결정적)
4. for each unit: summary = StructuredExtractor.extract(unit)  (LLM 미호출)
5. KnowledgeStore.save_structure/summary/graph   (엔진 생성분: 재생성)
   → 에이전트 노트(별도 네임스페이스)는 보존 (Q6, FR-C1)
6. return SyncReport(규모/건너뜀/실패/소요)        (US-N7)
```

- **재동기화(mode='resync')**: 엔진 우선 — 소스 기준으로 구조/요약/관계 재생성. 에이전트 노트는 대상 소스가 존재하는 한 보존, 조회 시 병합(Q6=A). 명시적 실행만(US-E5 AC-3).
- **결정성**: 2~4단계는 순수 도메인 로직 → 동일 입력 동일 출력(NFR-C3, US-N5 AC-2).

### 2.2 읽기 조회 (US-A1 / US-H1~H4)

```
MCP ResourcesProvider.read_resource(uri)
   → KnowledgeReadService.get_structure / get_summary / get_relationships
       → KnowledgeStore.load_*  (+ 에이전트 노트 병합)
       → 지연 계측 훅 (US-N1 AC-2)

Web Viewer.render_*  → (동일) KnowledgeReadService  ← Q2=A 공유
```

### 2.3 검색 / 스니펫 (US-A2 / US-A3)

```
MCP query_tool  → QueryService.query → QueryEngine.search_keyword / neighbors
MCP snippet_tool → SnippetService.snippet → ChunkingService.select_snippet (토큰 예산)
```

### 2.4 Update Tool (US-A4, 병행 모델)

```
MCP update_tool(payload)
   → UpdateService.apply_note
       → 검증 (실패 시 변경 없음 + 오류, AC-3)
       → KnowledgeStore.save_agent_note  (별도 네임스페이스, Q6)
```

---

## 3. 트랜잭션·일관성 정책

- **엔진 우선(FR-C1)**: 소스가 진실의 원천. 재동기화 시 엔진 생성 산출물 재생성. 에이전트 노트는 별도 네임스페이스로 보존하되, 대상 소스 제거 시 정리 정책은 Functional Design에서 확정.
- **결정성(NFR-C3)**: 저장 직렬화는 안정 정렬/정규화로 diff 노이즈 최소화(US-N5).
- **부분 실패 격리**: 파싱 실패/미지원 파일은 건너뛰고 파이프라인 지속, 리포트에 기록(US-E1/E2).

---

## 4. 서비스 ↔ 스토리 추적성

| 서비스 | 커버 스토리 |
|---|---|
| SyncService | US-E1, US-E2, US-E3, US-E4, US-E5, US-N7 |
| KnowledgeReadService | US-A1, US-H1, US-H2, US-H4, US-N1 |
| QueryService | US-A2 |
| SnippetService | US-A3, US-N2 |
| UpdateService | US-A4, FR-C1 |

> 서비스 간 의존/통신 패턴은 `component-dependency.md`, 서비스가 호출하는 컴포넌트 메서드는 `component-methods.md` 참조.

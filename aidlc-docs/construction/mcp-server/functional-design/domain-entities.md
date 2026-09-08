# Domain Entities — U2 MCP Server (Surface Model)

> U2는 자체 도메인 엔티티를 만들지 않는다. U1 도메인 모델을 **MCP 표면 표현**(URI, Tool I/O 페이로드, Prompt 템플릿)으로 매핑할 뿐이다. 아래는 그 표면 계약이다.

## 1. Resource URI 스킴 (Q1=A)

| Resource | URI 패턴 | U1 위임 | 반환(직렬화) |
|---|---|---|---|
| Structure | `agentic-kb://structure` | `KnowledgeReadService.get_structure()` | `StructureTree.to_dict()` (JSON) |
| Summary | `agentic-kb://summary/{target}` | `get_summary(target)` | `MergedSummary.to_dict()` (engine_first) |
| Relationships | `agentic-kb://relationships` 또는 `.../{target}` | `get_relationships(target?)` | `RelationshipGraph.to_dict()` |

- `{target}`: 프로젝트 상대 경로(예: `a.py`) 또는 심볼 id(예: `a.py::function::caller`). URL-decoding 후 그대로 서비스에 전달.
- 미존재/미인제스천 → **not-found** 신호(§business-rules BR-M4). 서버 미중단.

## 2. Tool 입출력 페이로드 (Q2=A)

### query (US-A2)
- **입력**: `{ query: str, mode?: "auto"|"keyword"|"graph" (기본 auto) }`
- **위임**: `QueryService.query(query, mode)`
- **출력**: `{ results: [SearchResult.to_dict(), ...] }` — 관련도 내림차순. 매칭 없음 → `{ results: [] }` (US-A2 AC-3).

### snippet (US-A3)
- **입력**: `{ target: str, token_budget: int }`
- **위임**: `SnippetService.snippet(target, token_budget)`
- **출력**: `Snippet.to_dict()` — `estimated_tokens`, `truncated` 포함(US-A3 AC-2).

### update_note (US-A4)
- **입력**: `{ target, body_md, author, created_at (ISO 8601) }` → `AgentNotePayload`
- **위임**: `UpdateService.apply_note(payload)`
- **출력**: `UpdateResult.to_dict()` — `ok`, `note_id?`, `errors[]`. 검증 실패 시 `ok=false`, KB 미변경(US-A4 AC-3).

### sync (US-E/US-N7 운영 표면)
- **입력**: `{ project_root: str, mode?: "full"|"resync" (기본 resync) }`
- **위임**: `SyncService.run(project_root, mode)`
- **출력**: `SyncReport.to_dict()` — `files_total`, `symbols_total`, `skipped[]`, `failures[]`, elapsed(US-N7).

## 3. Prompt 템플릿 (Q4=A)

| Prompt | 인자 | 내용(정적 텍스트, LLM 미호출) |
|---|---|---|
| `onboarding` | 없음 | 에이전트가 `structure`/`relationships` 리소스를 먼저 조회하고 `query`로 관련 심볼을 찾도록 안내하는 학습 템플릿 |
| `task` | `task_kind: str` (예: `write_unit_test`) | 해당 작업에 필요한 리소스/툴 사용 순서를 지시하는 작업 집중 템플릿 |

- 템플릿은 파라미터를 텍스트에 삽입해 조합하는 **순수 함수**. 외부/LLM 호출 없음.

## 4. 오류/신호 표현

| 상황 | 표현 |
|---|---|
| Resource 미존재 | MCP resource not-found (예외/신호), 서버 미중단 (US-A1 AC-4) |
| Tool 입력 검증 실패 | 결과 객체 `isError=true` + 메시지, 엔진 미변경 (US-A2/A4) |
| 정상 | 위 §2 직렬화 결과 |

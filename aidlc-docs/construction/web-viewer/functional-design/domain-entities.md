# Domain Entities — U3 Web Viewer (Surface Model)

> U3는 자체 도메인 엔티티를 만들지 않는다. U1 `KnowledgeReadService` 결과를 **SSR HTML 페이지**로 매핑한다. 아래는 라우트/뷰 표면 계약이다.

## 1. 라우트 → 뷰 → U1 위임 (Q2=A)

| 경로 | 뷰 | U1 위임 | 스토리 |
|---|---|---|---|
| `GET /` | Tree View | `get_structure()` → `StructureTree` | US-H1 |
| `GET /summary/{target}` | Wiki + Review | `get_summary(target)` → `MergedSummary` | US-H2, US-H4 |
| `GET /graph` | Dependency View (전체) | `get_relationships()` → `RelationshipGraph` | US-H3 |
| `GET /graph/{target}` | Dependency View (부분) | `get_relationships(target)` | US-H3 |
| `GET /static/style.css` | 정적 CSS | — (내장 상수) | 표현 |

- `{target}`: URL-decode한 프로젝트 상대 경로/심볼 id. 미존재 → 404 페이지(BR-W4).

## 2. 뷰 모델(서버가 조립하는 표현 구조)

### TreeView
- 입력: `StructureTree` (디렉토리/파일 노드 계층)
- 표현: 중첩 `<ul>` 트리. 파일 노드는 `/summary/{path}` 링크(US-H1 AC-2).

### WikiView
- 입력: `MergedSummary { target, engine: ModuleSummary?, agent_notes: [AgentNote], engine_first }`
- 표현:
  - **엔진 섹션**(배지: "엔진 자동 생성 · 재동기화 시 재생성") — signatures/docstrings/headings/comments를 Markdown 조합 후 HTML 렌더.
  - **에이전트 노트 섹션**(배지: "에이전트 작성 · 보존") — 각 note body_md를 HTML 렌더.
  - engine_first=True → 엔진 섹션 먼저(US-H4 AC-2, FR-C1 고지 배너).

### GraphView
- 입력: `RelationshipGraph { nodes: [TreeNode/Symbol], edges: [Edge{src,dst,kind}] }`
- 표현: 노드 목록(각 `/summary/{id}` 링크) + 엣지 인접 목록 + 경량 인라인 SVG. 노드 클릭→위키(US-H3 AC-2).

## 3. 오류/신호 표현
| 상황 | 표현 |
|---|---|
| 미인제스천/미존재 target | 404 HTML 페이지, 서버 미중단 |
| 인제스천 전 `/` | "지식 베이스 없음 — 먼저 sync 실행" 안내 페이지 |
| 정상 | 위 뷰 HTML |

## 4. HTML 안전 (Q6=A)
- 모든 동적 텍스트는 `html.escape` 후 삽입. Markdown 렌더러는 허용 요소(heading/para/list/code/inline-code)만 생성. 원문 HTML 미허용(XSS 방지).

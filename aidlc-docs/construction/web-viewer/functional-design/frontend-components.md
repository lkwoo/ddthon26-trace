# Frontend Components — U3 Web Viewer (SSR)

> SSR 다중 페이지. 클라이언트 JS 프레임워크 없음(FR-H5). 상호작용은 하이퍼링크 + 서버 렌더. 아래는 서버가 생성하는 HTML 컴포넌트 구조다.

## 1. 페이지 레이아웃 (공통 셸)
```
<html>
  <head> <link rel=stylesheet href="/static/style.css"> </head>
  <body>
    <nav>  [Tree /]  [Graph /graph]           # 전역 내비게이션
    <main> {페이지 콘텐츠}
    <footer> engine-first 정책 요약 링크
```
- 컴포넌트: `layout(title, body_html)` — 공통 셸 순수 함수.

## 2. 페이지별 컴포넌트

### Index/TreePage (`/`) — US-H1
- `tree_node(node)` (재귀): 디렉토리→`<details><summary>`, 파일→`<li><a href="/summary/{path}">`.
- 빈 KB → `empty_state("먼저 sync 실행")`.
- 상호작용: 파일 링크 클릭 → WikiPage(US-H1 AC-2). 펼침/접힘은 `<details>` 네이티브.

### WikiPage (`/summary/{target}`) — US-H2, US-H4
- `provenance_banner()` — engine-first 정책 고지(FR-C1, BR-W5).
- `engine_section(summary)` — 배지 "엔진 자동생성 · 재동기화 시 재생성" + `markdown_to_html`.
- `notes_section(notes)` — 배지 "에이전트 작성 · 보존" + note별 `markdown_to_html`.
- 순서: engine_first=True → 엔진 먼저.

### GraphPage (`/graph`, `/graph/{target}`) — US-H3
- `graph_svg(nodes, edges)` — 경량 인라인 SVG(노드 원 + 엣지 선). 결정적 좌표(노드 정렬 순 배치).
- `adjacency_list(edges)` — `src → dst (kind)` 목록, 각 노드 `/summary/{id}` 링크.
- 상호작용: 노드/링크 클릭 → WikiPage(US-H3 AC-2).

### NotFoundPage (404) — BR-W4
- `not_found(target)` — 안내 + 트리로 돌아가기 링크.

## 3. 상태 관리
- **서버사이드만**: 각 요청은 U1 읽기 결과로부터 stateless 렌더. 클라이언트 상태/스토어 없음.

## 4. 폼/입력
- 읽기 전용(BR-W2). 폼 없음. 검증 대상 입력 없음(경로 파라미터는 URL-decode 후 U1에 위임, confinement는 U1 보증).

## 5. API 통합 지점
- 모든 페이지는 **U1 `KnowledgeReadService`** 만 사용: `get_structure`, `get_summary`, `get_relationships`. (U2 MCP/외부 API 미사용.)

## 6. 스타일 (assets.py)
- 내장 최소 CSS 상수(트리 들여쓰기, 배지 색, 코드블록 모노스페이스). 외부 CDN/폰트 미사용(로컬·오프라인).

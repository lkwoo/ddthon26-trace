# Business Logic Model — U3 Web Viewer

> **핵심 원칙**: U3는 로직을 보유하지 않는다. 라우트를 파싱해 U1 `KnowledgeReadService`에 위임하고, 결과를 **결정적 SSR HTML**로 렌더한다. 렌더러는 서버와 분리된 순수 함수(테스트 가능).

## 1. 논리 컴포넌트 (Q1=A, stdlib 전용)

```
adapters/inbound/web/
├── rendering.py   # 순수 함수: markdown_to_html + render_tree/wiki/graph/not_found/index
├── routing.py     # Router: METHOD+path → (handler, target) 결정 (SDK/서버 독립)
├── app.py         # http.server 바인딩(BaseHTTPRequestHandler) — 얇은 껍데기
└── assets.py      # 내장 CSS 상수
tests/unit/web/    # rendering/routing 단위 테스트 (라이브 서버 불필요)
```

## 2. 위임/렌더 흐름

```
browser → app(HTTP GET path)
        → Router.match(path) → (view, target?)
        → switch view:
            index        → read.get_structure()          → rendering.render_index/tree
            summary       → read.get_summary(target)       → rendering.render_wiki
            graph         → read.get_relationships(target?) → rendering.render_graph
            static        → assets.CSS
          None from service → rendering.render_not_found (HTTP 404)  [BR-W4]
        → measure("web.<view>") 로 감싸 elapsed_ms 로깅  [US-N1 표면]
        ← HTTP 200 text/html (or 404)
```

## 3. Markdown 렌더링 (US-H2, FR-H5)
- `markdown_to_html(md)` — 내장 결정적 서브셋 렌더러:
  - `#`~`######` → `<h1>`..`<h6>`
  - 코드펜스```` ``` ```` → `<pre><code>`
  - `-`/`*` 목록 → `<ul><li>`
  - 빈 줄 구분 문단 → `<p>`
  - 인라인 `` `code` `` → `<code>`
  - 그 외 텍스트는 `html.escape` (원문 HTML 미허용, BR-W6)
- 순수 함수: 동일 입력 → 동일 출력(결정적). 외부/네트워크 호출 없음.

## 4. Wiki + Review 조립 (US-H2 + US-H4)
```
render_wiki(merged):
  banner = engine-first 정책 고지 (FR-C1)               [BR-W5]
  engine_section = badge("엔진 자동생성·재생성") + md→html(engine summary)
  notes_section  = badge("에이전트 작성·보존") + [md→html(note.body_md)]
  order = engine_section, notes_section  (engine_first=True)
```

## 5. 그래프 렌더 (US-H3)
```
render_graph(graph):
  nodes: 각 노드 이름/종류 + `/summary/{id}` 링크
  edges: src→dst (kind) 인접 목록 + 경량 인라인 SVG(노드/엣지)
  노드 링크 클릭 → 위키 이동(US-H3 AC-2)
```

## 6. 계측/오류
- 각 라우트 핸들러는 `measure("web.<view>")`로 계측(US-N1 표면).
- 서비스 None/미존재 → 404, 예외는 500 대신 안내 페이지로 격리(서버 미중단, BR-W8).

## 7. 스토리 커버리지
US-H1(tree + 탐색), US-H2(markdown SSR 렌더), US-H3(dependency graph + 연계), US-H4(review + engine-first 고지), US-N1(표면 계측).

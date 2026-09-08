# Code Generation Summary — U3 Web Viewer

> **단계**: CONSTRUCTION – Code Generation · **Unit: U3 Web Viewer** · 2026-09-08
> **결과**: `pytest` **46 passed** (U1 28 + U2 9 + U3 9). SSR, stdlib 전용, 읽기 전용.

## 생성 파일 (`src/agentic_kb/adapters/inbound/web/`)
- `rendering.py` — **순수 렌더 함수**: `markdown_to_html`(결정적 서브셋, HTML escape, 원문 HTML 미통과 BR-W6/W7), `layout`, `render_index`/`_tree_node`(US-H1), `render_wiki`+engine/notes 섹션+provenance 배너(US-H2/H4, FR-C1 BR-W5), `render_graph`+경량 인라인 SVG(US-H3), `render_not_found`(BR-W4), `render_css`. 그래프 노드 링크는 심볼 id의 path 부분→`/summary/{path}`(US-H3 AC-2).
- `routing.py` — **Router**(table-driven, 서버 독립): `/`, `/static/style.css`, `/summary/{target}`, `/graph`, `/graph/{target}`, 기타→not_found. 쿼리스트링 제거·URL-decode.
- `assets.py` — 내장 CSS 상수(외부 CDN/폰트 없음).
- `app.py` — **WebApp**(`handle(path)`→`Response`, U1 read 위임, `measure("web.<view>")` 계측, 예외→404/500 격리 BR-W8) + **WebServer**(ThreadingHTTPServer 바인딩, 127.0.0.1) + **Response**. 순수 dispatch는 라이브 서버 없이 테스트 가능(Humble Object).
- `__init__.py` — export.

## 테스트 (`tests/unit/web/test_web_viewer.py`, 9건)
- routing 테이블, markdown escape/렌더/코드펜스/결정성, wiki provenance(엔진→노트 순서·배너), WebApp dispatch(index/static/summary OK·404/graph/unknown) — 실제 U1 서비스 위에서 검증.

## 설계 준수
- **읽기 전용**(BR-W2), **stdlib 전용 SSR**(FR-H5, `[web]` extra 비움, NFR-U3-D1), **결정적 렌더**(BR-W7), **HTML 안전**(escape·allow-list, BR-W6), **서버 미중단**(BR-W8), **engine-first 고지**(BR-W5), **표면 계측**(US-N1), **무상태+ThreadingHTTPServer**(NFR-U3-A1).

## PBT 컴플라이언스 (U3)
- 렌더/라우팅 매핑 계층 → 신규 PBT 대상 얕음. round-trip/invariant는 U1 보증. U3는 **PBT-10 예제**(결정적 렌더·라우팅·dispatch)로 커버. Partial 차단 위반 없음.

## 스토리 커버리지
US-H1(tree+탐색), US-H2(markdown SSR), US-H3(dependency graph+연계), US-H4(review+engine-first 고지), US-N1(계측).

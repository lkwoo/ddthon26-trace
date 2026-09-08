# Tech Stack Decisions — U3 Web Viewer

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U3 Web Viewer** · 2026-09-08

## 1. 서버 / 전송
- **stdlib `http.server.ThreadingHTTPServer` + `BaseHTTPRequestHandler`** (Q2/Q3=A).
  - 근거: 최소 의존성(FR-H5), 로컬 오프라인, 결정적. 웹 프레임워크 불필요(MVP 단일 사용자).
  - 로컬 루프백(127.0.0.1) 바인드.

## 2. 렌더링
- **내장 Markdown-subset → HTML 렌더러**(순수 함수, `rendering.py`). 외부 markdown 라이브러리 미도입.
  - 지원: heading/문단/목록/코드펜스/인라인 코드. 모든 텍스트 `html.escape`(BR-W6).
  - 근거: 결정성·최소 의존·XSS 위생. 확장 필요 시 후속 `[web]` extra에 렌더러 추가 가능.

## 3. 스타일
- 내장 CSS 상수(`assets.py`). 외부 CDN/폰트 미사용.

## 4. 계측
- U1 `application.measurement.measure()` 재사용(US-N1). 추가 의존성 없음.

## 5. 테스트
- **pytest** — rendering(순수 함수)·routing 예제 테스트. 라이브 서버 불필요.

## 6. 의존성 (pyproject.toml)
| 의존성 | 범위 | 용도 |
|---|---|---|
| (stdlib) http.server, html | runtime | SSR 서버 + 이스케이프 |
| (U1 재사용) KnowledgeReadService | runtime | 읽기 위임 대상 |
| pytest | dev | rendering/routing 테스트 |

> `[web]` optional-extra는 **비어 있음**(stdlib 전용). 향후 그래프 라이브러리/템플릿 엔진 도입 시에만 채운다.

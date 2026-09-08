# Functional Design Plan — U3 Web Viewer

> **Unit**: U3 Web Viewer (inbound adapter) · **Depends on**: U1 `KnowledgeReadService`
> **Stories**: US-H1(Tree), US-H2(Wiki/SSR), US-H3(Dependency graph), US-H4(Content review + engine-first 고지)
> **Principle**: 얇은 인바운드 어댑터 — 로직 미보유, U1 읽기 서비스에 위임. **SSR·최소 의존성**(FR-H5, `[web]` extra 비어있음 = stdlib 전용).

## Steps
- [x] S1. Unit/스토리 분석 (US-H1~H4)
- [x] S2. 설계 질문 + 권장안 채택(자동)
- [x] S3. domain-entities.md — 라우트/뷰 모델(HTML 페이지 표면)
- [x] S4. business-logic-model.md — 라우트→U1 읽기 위임→렌더 흐름
- [x] S5. business-rules.md — 렌더/오류/engine-first 고지 규칙
- [x] S6. frontend-components.md — SSR 페이지/컴포넌트 구조
- [x] S7. 완료 메시지 + 승인(자동 채택)

## 설계 질문 및 채택 답변 (권장안 자동 채택)

### Q1. 서버/렌더 스택 (FR-H5 최소 의존성)
- A. stdlib `http.server` + 내장 Markdown-subset→HTML 렌더러(순수 함수, 결정적, 의존성 0) **(권장)**
- B. Flask/Jinja 등 프레임워크 도입
- **[Answer]: A** — `[web]` extra 비어있음. SSR·최소 의존·결정적 렌더. 렌더러는 서버 독립 순수 함수(테스트 가능).

### Q2. 라우트 구성
- A. `/`(트리), `/summary/{target}`(위키+검토), `/graph`(의존성), `/graph/{target}`(부분 그래프) **(권장)**
- B. 단일 페이지 SPA
- **[Answer]: A** — SSR 다중 페이지. 트리/그래프 노드에서 `/summary/{target}`로 연결(US-H1 AC-2, US-H3 AC-2).

### Q3. 위키 콘텐츠 소스 (US-H2)
- A. `KnowledgeReadService.get_summary(target)` → MergedSummary(엔진 요약 + 에이전트 노트)를 Markdown 조합 후 HTML 렌더 **(권장)**
- B. 저장된 .md 파일 직접 서빙
- **[Answer]: A** — 서비스 경유로 병합·engine-first 순서 일관. 저장 포맷 결합 회피.

### Q4. 의존성 시각화 방식 (US-H3)
- A. 서버가 그래프를 노드/엣지 목록 HTML(+경량 SVG/인접목록)로 SSR, 노드 클릭→`/summary` 링크 **(권장)**
- B. 클라이언트 JS 그래프 라이브러리
- **[Answer]: A** — 최소 의존성 우선. 노드/엣지를 SSR 목록 + 간단 SVG로 표현. 상호작용은 하이퍼링크.

### Q5. Content Review / engine-first 고지 (US-H4)
- A. summary 페이지에 "엔진 자동 생성(재동기화 시 소스 기준 재생성)"·"에이전트 노트(보존)" 출처 배지 및 고지 배너 표시 **(권장)**
- B. 별도 정책 문서 링크만
- **[Answer]: A** — FR-C1 정책을 UI에서 명시(US-H4 AC-2). 엔진 산출과 에이전트 노트를 시각적으로 구분.

### Q6. 안전한 HTML 출력
- A. 모든 텍스트는 HTML 이스케이프 후 렌더(간이 마크다운 요소만 허용) **(권장)**
- B. 원문 HTML 허용
- **[Answer]: A** — 최소 위생(XSS 방지). 렌더러는 허용 요소만 생성.

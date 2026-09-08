# NFR Requirements Plan — U3 Web Viewer

> **Unit**: U3 Web Viewer · Stories US-H1~H4, US-N1. 대부분 NFR을 U1에서 승계. 고유 관심사: SSR 성능·최소 의존성·HTML 안전.

## Steps
- [x] S1. Functional Design 분석
- [x] S2. NFR 질문 + 권장안 채택(자동)
- [x] S3. nfr-requirements.md
- [x] S4. tech-stack-decisions.md
- [x] S5. 완료 + 승인(자동)

## 질문 및 채택 답변 (권장안 자동 채택)

### Q1. 성능 (US-N1)
- A. SSR 페이지 렌더는 U1 읽기 시간 + 결정적 렌더(경량). MVP 규모에서 즉시 응답 목표, 계측으로 관찰 **(권장)**
- **[Answer]: A**

### Q2. 의존성 (FR-H5)
- A. stdlib 전용(`http.server`, `html`, 내장 렌더러). `[web]` extra 비어둠 **(권장)**
- B. Flask/Jinja/markdown 라이브러리
- **[Answer]: A** — 최소 의존·오프라인·결정적.

### Q3. 동시성/가용성
- A. 로컬 단일 사용자. `ThreadingHTTPServer`로 브라우저 병렬 리소스 요청 허용, 핸들러 무상태 **(권장)**
- **[Answer]: A** — 요청별 U1 읽기 위임, 공유 가변 상태 없음.

### Q4. 보안 (Baseline OFF)
- A. 최소 위생: HTML 이스케이프(XSS 방지, BR-W6), 읽기 전용, 로컬 바인드(127.0.0.1), 경로 confinement는 U1 **(권장)**
- **[Answer]: A**

### Q5. 테스트
- A. rendering(순수 함수)·routing 예제 테스트(라이브 서버 불필요). PBT는 U1 집중 **(권장)**
- **[Answer]: A**

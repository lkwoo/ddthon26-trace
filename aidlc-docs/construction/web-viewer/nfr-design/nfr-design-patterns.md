# NFR Design Patterns — U3 Web Viewer

> **단계**: CONSTRUCTION – NFR Design · **Unit: U3 Web Viewer** · 2026-09-08

## 1. Inbound Adapter (Hexagonal)
- U3는 인바운드 어댑터. 도메인/유즈케이스는 U1 소유. U3는 HTTP ↔ U1 읽기 서비스 번역(읽기 전용).

## 2. 렌더링 격리 (Pure Function + Humble Object)
- **패턴**: rendering.py = 순수 함수(결정적, 테스트 가능). `app.py` = 유일한 `http.server` 바인딩(Humble Object).
- 효과: 렌더 로직을 라이브 서버 없이 검증(NFR-U3-M1/T1), 서버/렌더 관심사 분리.

## 3. 라우팅 (Table-driven)
- **패턴**: Router가 METHOD+path를 (view, target)으로 매핑. app은 매핑 결과를 렌더 함수에 위임. 서버 독립.

## 4. 오류 격리 (Fault Isolation)
- **패턴**: Boundary translation. 서비스 None/미존재 → 404 페이지, 예외 포착 → 안내 페이지. 서버 프로세스 미중단(NFR-U3-A2, BR-W8).

## 5. HTML 안전 (Output Encoding)
- **패턴**: 모든 동적 텍스트 `html.escape`, 허용 요소만 생성. 원문 HTML 미통과(XSS 방지, NFR-U3-S1, BR-W6).

## 6. 표면 계측 (Observability)
- **패턴**: Decorator(measure). 각 라우트 핸들러를 `measure("web.<view>")`로 감쌈(US-N1).

## 7. 무상태 동시성
- **패턴**: Stateless handler + ThreadingHTTPServer. 요청별 U1 읽기 위임, 공유 가변 상태 없음(NFR-U3-A1).

## 8. Provenance 표시 (US-H4)
- summary 페이지는 엔진 자동생성(재생성) vs 에이전트 노트(보존)를 배지/배너로 구분(FR-C1, BR-W5).

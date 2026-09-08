# Logical Components — U3 Web Viewer

> **단계**: CONSTRUCTION – NFR Design · **Unit: U3 Web Viewer** · 2026-09-08

## 1. 논리 컴포넌트 맵

| 컴포넌트 | 계층 | 책임 | NFR 패턴 |
|---|---|---|---|
| adapters.inbound.web.rendering | inbound adapter | markdown_to_html + render_index/tree/wiki/graph/not_found (순수 함수) | Pure function, Output encoding |
| adapters.inbound.web.routing (Router) | inbound adapter | path → (view, target) 매핑 | Table-driven, 서버 독립 |
| adapters.inbound.web.assets | inbound adapter | 내장 CSS 상수 | 최소 의존 |
| adapters.inbound.web.app (WebApp/Handler) | inbound adapter (binding) | http.server 바인딩 + U1 read 위임 + measure | Humble Object, Fault isolation, Stateless |

## 2. 의존 방향
- `web.rendering/routing/assets` → 순수(U1 도메인 모델 타입만 참조).
- `web.app` → routing + rendering + U1 `KnowledgeReadService`. 조립 시 U4 `config.py`가 서비스 주입.
- 순환 없음: U3 → U1 (단방향).

## 3. 인프라성 논리 컴포넌트 판정
- **큐/브로커, 분산캐시, CDN, LB/오토스케일, 인증 게이트, 세션 스토어**: 전부 **N/A** — 로컬 단일 사용자 stdlib SSR, 읽기 전용, 외부 호출 없음.

## 4. 관측성
- Measurement 훅(U1 재사용)으로 라우트 지연 로깅. 별도 지표 저장소 없음.

## 5. 배치(파일)
```
src/agentic_kb/adapters/inbound/web/
├── __init__.py
├── rendering.py   # 순수 렌더 함수
├── routing.py     # Router
├── assets.py      # CSS 상수
└── app.py         # ThreadingHTTPServer 바인딩 (WebApp/Handler)
tests/unit/web/    # rendering/routing 예제 테스트
```

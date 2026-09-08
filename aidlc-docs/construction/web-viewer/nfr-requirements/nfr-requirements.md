# NFR Requirements — U3 Web Viewer

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U3 Web Viewer** · 2026-09-08
> 얇은 SSR 인바운드 어댑터. 대부분 NFR은 U1 승계. 고유 관심사: SSR 성능·최소 의존성·HTML 안전.

## 1. Performance (US-N1)
- **NFR-U3-P1**: 페이지 응답 = U1 읽기 시간 + 결정적 경량 렌더. MVP 규모에서 즉시 응답 목표.
- **NFR-U3-P2**: 각 라우트 핸들러는 `measure("web.<view>")`로 elapsed_ms 로깅(표면 계측).

## 2. Dependencies / Deployability (FR-H5)
- **NFR-U3-D1**: stdlib 전용(`http.server`, `html`, 내장 markdown-subset 렌더러). 웹 프레임워크/외부 CDN 미사용. `[web]` extra는 비어 있음.
- **NFR-U3-D2**: 오프라인·로컬 동작. 외부/LLM 호출 없음(NFR-C3, BR-W7/W10).

## 3. Availability / Concurrency
- **NFR-U3-A1**: `ThreadingHTTPServer`로 브라우저의 병렬 리소스 요청 처리. 핸들러는 무상태(요청별 U1 위임) → 경합 없음.
- **NFR-U3-A2**: 단일 요청 실패는 404/안내 페이지로 격리, 서버 미중단(BR-W8).

## 4. Security (Baseline OFF — 최소 위생)
- **NFR-U3-S1**: 모든 동적 텍스트 HTML 이스케이프, 허용 요소만 렌더(XSS 방지, BR-W6).
- **NFR-U3-S2**: 읽기 전용(BR-W2). 로컬 루프백(127.0.0.1) 바인드 권장, 외부 노출 없음.
- **NFR-U3-S3**: 경로 confinement는 U1 어댑터(BR-4)가 최종 보증. 인증/시크릿 없음. Security/Resiliency 확장 N/A.

## 5. Maintainability (NFR-C2)
- **NFR-U3-M1**: rendering(순수 함수)·routing은 서버 바인딩과 분리 → 단위 테스트 가능. `app.py`가 유일한 `http.server` 바인딩.

## 6. Testability (PBT Partial)
- **NFR-U3-T1**: rendering/routing 예제 테스트(라이브 서버 불필요, PBT-10). 결정적 렌더(BR-W7)는 동일 입력→동일 HTML로 검증.
- **NFR-U3-T2**: round-trip/invariant PBT는 U1 도메인이 보증. U3 신규 PBT 대상 얕음 → Partial 범위에서 예제로 충분.

## 7. 확장 컴플라이언스 요약
| Extension | 상태 | 판정 |
|---|---|---|
| Security Baseline | Disabled | N/A (최소 위생: HTML escape·읽기전용·로컬 바인드 유지) |
| Resiliency Baseline | Disabled | N/A |
| PBT (Partial) | Enabled | 적용 — U3는 렌더/라우팅 매핑, 신규 PBT 대상 얕음. PBT-10 예제로 커버. 차단 위반 없음. |

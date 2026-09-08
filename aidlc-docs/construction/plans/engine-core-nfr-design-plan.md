# NFR Design Plan — U1 Engine Core

> **단계**: CONSTRUCTION – NFR Design (per-unit) · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08 · **자동 진행**: 권장안 자동 채택.

## 1. 질문 (권장안 자동 채택)

### Q1 — 성능 패턴 (Performance)
1초 목표 달성 패턴은?
A) **사전 계산·직렬화 저장 + 조회 시 순수 로드(재계산 없음) + 지연 계측 데코레이터** (권장)
[Answer]: **A** — 인제스천 시 무거운 파싱/그래프 계산을 끝내고 저장. 조회는 JSON/Markdown 로드만.

### Q2 — 결정성 패턴 (Determinism)
결정성 보장 패턴은?
A) **불변 dataclass + 안정 정렬 직렬화 + 순수 함수(도메인) / I/O는 포트 뒤로 격리(헥사고날)** (권장)
[Answer]: **A** — NFR-C3. 부수효과 격리로 순수 로직 PBT 대상화.

### Q3 — 확장성 패턴 (Scalability/Extensibility)
파서 확장 패턴은?
A) **Registry + Strategy(Port 구현 플러그인 등록)** (권장, US-N4)
[Answer]: **A**

### Q4 — 신뢰성 패턴 (Reliability)
부분 실패 처리 패턴은?
A) **파일 단위 try/collect(예외 격리) + Result/Report 누적(SyncReport) + Null-object/Optional 조회** (권장)
[Answer]: **A** — BR-3/13.

### Q5 — 캐시/재처리 (Performance/Resource)
재처리 최소화 패턴은?
A) **콘텐츠 sha 기반 스킵 캐시(resync)** (권장, US-N7 AC-1)
[Answer]: **A**

### Q6 — 논리 컴포넌트(인프라성) (Logical Components)
큐/캐시/서킷브레이커 등 인프라 컴포넌트 필요?
A) **불필요(N/A) — 로컬 동기 처리. 유일한 "캐시"는 sha 스킵(파일 기반)** (권장)
[Answer]: **A** — 분산/네트워크 컴포넌트 없음.

## 2. 산출물
- [x] `construction/engine-core/nfr-design/nfr-design-patterns.md`
- [x] `construction/engine-core/nfr-design/logical-components.md`

## 3. 진행 절차
- [x] Step 1: NFR 요구 분석
- [x] Step 2-4: 계획+질문(자동 채택)
- [x] Step 5: 모호성 없음
- [x] Step 6: 산출물 2종
- [x] Step 7-9: 완료 → 승인(자동) → state 갱신

## 4. 컴플라이언스
- Security/Resiliency Baseline: N/A(opt-out). PBT: 설계 패턴이 순수 로직 격리로 PBT 대상 명확화(코드 생성에서 강제).

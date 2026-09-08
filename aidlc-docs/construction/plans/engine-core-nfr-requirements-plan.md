# NFR Requirements Plan — U1 Engine Core

> **단계**: CONSTRUCTION – NFR Requirements (per-unit) · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08
> **입력**: functional-design/*, requirements.md(NFR-P/C/D/E/R/T), stories.md(US-N1~N7)
> **자동 진행**: 사용자가 권장안 자동 채택 위임.

---

## 1. 질문 (권장안 자동 채택)

### Q1 — 성능 목표 구체화 (Performance, NFR-P1)
조회 응답 목표는?

A) **핵심 조회(Resource read/Query/Snippet) p95 < 1s @ MVP 규모(≤ ~2k 파일)** (권장)
B) 평균 < 1s만
[Answer]: **A** — US-N1/A2 AC-4의 1초 목표를 p95로 구체화, 사전직렬화 로드로 달성.

### Q2 — 규모 상정 (Scalability, NFR-R2)
MVP 대상 규모는?

A) **단일 개발자 로컬 프로젝트, ~수천 파일/수만 심볼** (권장)
B) 초대규모(제외 범위)
[Answer]: **A** — 초대규모는 명시적 out-of-scope. 규모/소요 계측(US-N7)으로 인지만.

### Q3 — 가용성/복구 (Availability)
가용성 요구는?

A) **N/A — 로컬 단일 사용자 CLI/stdio, 상시가동 SLA 없음** (권장)
B) HA/failover 필요
[Answer]: **A** — 로컬 실행 모델. Resiliency Baseline opt-out과 일관.

### Q4 — 보안 (Security)
보안 요구는?

A) **N/A(Security Baseline opt-out) — 로컬 파일 접근만, 네트워크/인증 없음. 단, 경로 탈출 방지(루트 밖 접근 금지)는 기본 위생으로 유지** (권장)
B) 전체 Security Baseline 적용
[Answer]: **A** — Q11 opt-out. 최소 위생(경로 정규화 BR-4)만 유지.

### Q5 — PBT 프레임워크 선정 (PBT-09, blocking)
Python PBT 프레임워크는?

A) **Hypothesis** (권장 — 성숙·shrinking·시드 재현·pytest 통합)
B) 기타
[Answer]: **A** — Hypothesis. dev 의존성 포함, pytest 러너 통합, PBT-07/08/09 충족 기반.

### Q6 — 테스트 러너 (Maintainability)
테스트 러너는?

A) **pytest + Hypothesis** (권장)
B) unittest
[Answer]: **A** — pytest 표준, Hypothesis 통합 용이.

### Q7 — 신뢰성/오류 처리 (Reliability)
부분 실패 정책은?

A) **부분 실패 격리 + SyncReport 기록(BR-3), 조회 미존재 안전응답(BR-13)** (권장, 이미 functional-design 반영)
B) fail-fast 전체 중단
[Answer]: **A** — 인제스천 견고성(US-E2 AC-3), 서버 무중단(US-A1 AC-4).

---

## 2. 산출물 (Artifacts)
- [x] `construction/engine-core/nfr-requirements/nfr-requirements.md`
- [x] `construction/engine-core/nfr-requirements/tech-stack-decisions.md` (PBT-09 프레임워크 포함)

## 3. 진행 절차
- [x] Step 1: functional design 분석
- [x] Step 2-4: 계획+질문 저장(권장안 자동 채택)
- [x] Step 5: 답변 분석 — 모호성 없음
- [x] Step 6: 산출물 2종 생성
- [x] Step 7-9: 완료 → 승인(자동) → state 갱신

## 4. PBT 컴플라이언스 (NFR Requirements 적용 규칙)
| Rule | 상태 | 근거 |
|---|---|---|
| PBT-09 Framework Selection | **Compliant** | Hypothesis 선정·tech-stack-decisions.md 문서화·pyproject dev 의존성 명시. shrinking/seed/custom strategy 지원 확인. |
| 그 외 PBT | N/A(본 단계) | PBT-02/03/07/08은 Code Generation/Build&Test 단계 적용. |

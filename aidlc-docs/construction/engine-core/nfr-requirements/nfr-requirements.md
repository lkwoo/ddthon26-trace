# NFR Requirements — U1 Engine Core

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08

---

## 1. 성능 (Performance)
- **NFR-U1-P1**: 핵심 조회(Resource read, Query, Snippet)는 MVP 규모(≤ 약 2,000 파일)에서 **p95 < 1초**. 저장소는 사전 직렬화된 JSON/Markdown을 로드하고 조회 시 재파싱/재계산하지 않는다. (US-N1, US-A2 AC-4)
- **NFR-U1-P2 (토큰 효율)**: 모든 에이전트 반환물은 요약/청크 형태. Snippet은 예산 준수 및 절단 표시(BR-17~19). (US-N2)
- **측정 수단**: `measure(name)` 계측 훅으로 조회·동기화 소요 로깅(US-N1 AC-2).

## 2. 확장성 / 자원 (Scalability & Resource)
- **NFR-U1-S1**: 대상은 단일 개발자 로컬 프로젝트(~수천 파일/수만 심볼). 초대규모 실시간 인덱싱은 out-of-scope.
- **NFR-U1-S2 (자원 인지)**: SyncReport에 files_total/symbols_total/duration_ms 노출. resync 시 sha 기반 재처리 스킵(BR-12). (US-N7)

## 3. 가용성 (Availability)
- **N/A**: 로컬 단일 사용자 CLI/stdio 실행 모델. 상시가동 SLA·failover·DR 요구 없음. (Resiliency Baseline opt-out과 일관)

## 4. 보안 (Security)
- **N/A(Baseline opt-out)**: 네트워크/인증/권한 부여 없음, 로컬 파일 접근만.
- **유지되는 최소 위생**: 경로 정규화·루트 밖 접근 금지(BR-4). 신뢰 경계 밖 입력 없음(로컬 소스 파일).

## 5. 신뢰성 (Reliability)
- **NFR-U1-R1 (부분 실패 격리)**: 파일 단위 수집/파싱 실패는 격리·기록 후 계속(BR-1~3). (US-E1 AC-2, US-E2 AC-3)
- **NFR-U1-R2 (안전 조회)**: 미존재 대상은 예외 대신 None/빈 결과(BR-13). 서버 무중단. (US-A1 AC-4)

## 6. 결정성 / 이식성 (Determinism & Portability)
- **NFR-U1-C1 (결정성)**: 동일 입력 → 동일 산출물. LLM/외부 호출 금지(BR-5~7). (US-N3, NFR-C3)
- **NFR-U1-C2 (파서 확장성)**: 언어 파서 플러그인 등록으로 코어 무수정 확장(US-N4, NFR-C2).
- **NFR-U1-D1 (Git 친화)**: 텍스트(Markdown+JSON) 저장, 결정적 직렬화로 diff 노이즈 최소(US-N5, US-E4).

## 7. 유지보수성 / 테스트 품질 (Maintainability & Testability)
- **NFR-U1-T1 (PBT Partial)**: 순수 함수/직렬화 round-trip에 PBT 적용. 차단 규칙 PBT-02/03/07/08/09. (US-N6)
- **NFR-U1-T2 (프레임워크)**: **Hypothesis** + **pytest**. (PBT-09, tech-stack-decisions 참조)
- **NFR-U1-T3 (재현성)**: 실패 시 shrinking + 시드 로깅(PBT-08). CI에서 시드 로깅/고정.

## 8. NFR → 스토리/요구 추적성
| NFR | 출처 |
|---|---|
| P1/P2 | NFR-P1/P2, US-N1/N2, US-A2/A3 |
| S1/S2 | NFR-R2, US-N7 |
| R1/R2 | US-E1/E2, US-A1 |
| C1/C2/D1 | NFR-C2/C3/D1, US-N3/N4/N5, US-E3/E4 |
| T1/T2/T3 | NFR-T1/T2/T3, US-N6 |

# Logical Components — U1 Engine Core

> **단계**: CONSTRUCTION – NFR Design · **Unit: U1 Engine Core** · 2026-09-08

---

## 1. 논리 컴포넌트 맵

| 컴포넌트 | 계층 | 책임 | NFR 패턴 |
|---|---|---|---|
| domain.models | domain | 불변 엔티티 + 직렬화 | Immutable/Stable ordering (C1,D1) |
| domain.graph_builder | domain | 심볼/엣지 결정적 그래프 | 순수함수 (C1), PBT-03 |
| domain.extractor | domain | 결정적 구조 추출 | 순수함수 (C1) |
| domain.chunking | domain | 예산 준수 스니펫/토큰 추정 | 순수함수 (P2), PBT-03 |
| domain.query | domain | 키워드/그래프 검색 | 순수함수, 결정적 정렬 |
| application.sync_service | application | 파이프라인 조율 + 실패 격리 + sha 스킵 | Error isolation, skip-cache (R1,S2) |
| application.read_service | application | 병합 요약/구조/관계 조회 + 계측 | Measure, Null-object (P1,R2) |
| application.query_service | application | 검색 위임 | Measure (P1) |
| application.snippet_service | application | 스니펫 위임 | 예산 준수 (P2) |
| application.update_service | application | 노트 검증·저장(별도 네임스페이스) | 원자적 실패 (BR-22) |
| ports.* | ports | 추상 계약 3종 | 헥사고날 격리 (C1,T1) |
| adapters.outbound.source | adapter | 파일 순회/읽기 + Path confinement | 보안 위생 |
| adapters.outbound.parsers | adapter | ParserRegistry + tree-sitter | Registry+Strategy (C2) |
| adapters.outbound.store | adapter | JSON/Markdown 저장 + sha 인덱스 | Precompute-persist, skip-cache |
| testing (공용) | test-support | Hypothesis strategy/제너레이터 | PBT-07 |

## 2. 인프라성 논리 컴포넌트 판정
- **큐 / 메시지 브로커**: N/A — 로컬 동기 처리.
- **분산 캐시**: N/A — 유일 캐시는 저장소 내 콘텐츠 sha 스킵 인덱스(파일 기반).
- **서킷 브레이커 / 리트라이**: N/A — 외부 호출 없음(NFR-C3). 부분 실패는 격리·기록으로 처리.
- **로드밸런서 / 오토스케일**: N/A — 단일 프로세스 로컬.
- **인증/인가 게이트**: N/A — 로컬 파일 접근(Security opt-out), Path confinement만 유지.

## 3. 관측성(경량)
- **Measurement 훅**: 조회/동기화 경로 소요를 로깅(표준 logging). 지표 저장소 없음(로컬 로그).
- **SyncReport**: files/symbols/skipped/failures/duration_ms — 실행 단위 자원·결과 가시성(US-N7).

## 4. 컴포넌트 의존 방향 (재확인)
- domain ← application ← (ports) ← adapters. 의존은 안쪽(domain)으로만. 순환 없음.

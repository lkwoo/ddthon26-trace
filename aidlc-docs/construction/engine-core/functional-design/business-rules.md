# Business Rules — U1 Engine Core

> **단계**: CONSTRUCTION – Functional Design · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08

각 규칙은 `BR-<n>` 식별자를 가지며 관련 스토리/요구사항을 추적한다.

---

## 1. 수집·파싱 규칙 (Ingestion & Parsing)

- **BR-1 (지원 포맷 한정)**: 소스 코드 + Markdown만 처리. 미지원 확장자(PDF/HTML/PPT 등)는 `discover` 단계에서 제외하고 `SyncReport.skipped`에 "unsupported format" 기록. (US-E1 AC-2, MVP 범위)
- **BR-2 (파서 부재)**: 확장자에 매핑된 파서가 없으면 해당 파일 skip("no parser") 후 파이프라인 계속. 코어 수정 없이 파서 추가 가능(플러그인). (US-N4, US-E2 AC-2)
- **BR-3 (파싱 실패 격리)**: 개별 파일 파싱 예외는 포착하여 `SyncReport.failures`에 "path: reason" 기록하고 계속. 전체 파이프라인 중단 금지. (US-E2 AC-3, Q7=A)
- **BR-4 (경로 정규화)**: 모든 파일 경로는 프로젝트 루트 기준 상대경로 + POSIX 구분자로 정규화. 절대경로·`..` 금지(저장 재현성).

---

## 2. 결정성 규칙 (Determinism — NFR-C3)

- **BR-5 (LLM/외부 호출 금지)**: 도메인·추출·그래프·저장 전 과정에서 LLM/외부 API 호출 금지. 모든 처리는 로컬. (US-E3 AC-2, US-N3 AC-1)
- **BR-6 (재현 가능 산출)**: 동일 입력(동일 sha 집합) → 동일 산출물. 컬렉션은 명시된 키로 안정 정렬, 시각/난수/해시순서 등 비결정 요소를 직렬화에 포함 금지. (US-E3 AC-3, US-E4 AC-2, US-N5 AC-2)
- **BR-7 (시간 필드 제한)**: `created_at`(AgentNote), `duration_ms`(SyncReport) 등 본질적 시변 필드만 시간 의존 허용. 엔진 산출물(구조/요약/그래프)에는 타임스탬프 미포함(diff 노이즈 방지).

---

## 3. 저장·충돌 정책 (Persistence & Conflict — 엔진 우선)

- **BR-8 (엔진 우선, Engine-first)**: 위키의 구조/요약/관계는 소스가 진실의 원천. 재동기화 시 소스 기준 재생성·덮어쓰기. (FR-C1, US-E5 AC-2)
- **BR-9 (에이전트 노트 보존)**: 에이전트 노트는 **별도 네임스페이스**에 저장되어 재동기화 시 삭제/덮어쓰기 되지 않음. (Q6, US-A4 AC-2)
- **BR-10 (Orphan 노트)**: 재동기화 후 대상 심볼/파일이 소스에서 사라지면 해당 노트는 삭제하지 않고 orphan으로 표시(읽기 시 구분 노출). 사용자 판단에 위임.
- **BR-11 (텍스트 전용 저장)**: 모든 산출물은 Markdown(문서형) + JSON(구조/그래프형) 텍스트로 저장. 바이너리 의존 금지. (US-E4 AC-1, US-N5 AC-1)
- **BR-12 (재처리 스킵)**: `mode='resync'`에서 저장된 sha와 동일한 파일은 재파싱/재추출 skip. (US-N7 AC-1)

---

## 4. 조회·검색 규칙 (Read & Query)

- **BR-13 (미존재 안전 응답)**: 존재하지 않는 target 조회 시 예외 대신 `None`/빈 결과 반환. 서버 중단 금지. (US-A1 AC-4)
- **BR-14 (병합 요약 출처 분리)**: `get_summary`는 엔진 요약과 에이전트 노트를 출처 구분하여 `MergedSummary`로 반환, `engine_first=True` 명시. (Q5, US-H4 AC-2)
- **BR-15 (검색 결정성·설명가능성)**: 검색 score는 결정적 가중 매칭(Q2). 결과는 score desc, 동점 target asc 정렬. 각 결과에 `matched_on` 근거 포함. (US-A2 AC-1, NFR-C3)
- **BR-16 (무매칭)**: 매칭 없으면 빈 리스트를 오류 없이 반환. (US-A2 AC-3)

---

## 5. 스니펫·토큰 규칙 (Snippet & Token — NFR-P2)

- **BR-17 (예산 준수)**: 반환 Snippet은 항상 `estimated_tokens <= token_budget`. (US-A3 AC-1, 불변식 PBT-03)
- **BR-18 (축약 우선순위)**: 예산 초과 시 대상 본문 우선 보존 → 시그니처/docstring → 주변 문맥 절단 순. (Q3, US-A3 AC-3)
- **BR-19 (절단 표시)**: 축약 발생 시 `truncated=True` 및 `estimated_tokens` 포함하여 에이전트가 예산 관리 가능. (US-A3 AC-2, US-N2 AC-2)
- **BR-20 (토큰 추정 로컬성)**: `estimate_tokens`는 외부 토크나이저 비의존 결정적 휴리스틱. (Q4, NFR-C3)

---

## 6. Update Tool 검증 규칙 (US-A4)

- **BR-21 (필수 필드)**: `target`(비어있지 않음), `body_md`(비어있지 않음), `author`(존재), `created_at`(ISO 8601) 필수. 하나라도 위반 시 검증 오류.
- **BR-22 (원자적 실패)**: 검증 실패 시 지식 베이스 **무변경** + 명확한 검증 오류 반환. (US-A4 AC-3)
- **BR-23 (엔진 산출물 불가침)**: Update Tool은 에이전트 노트 네임스페이스만 기록. 엔진 구조/요약/그래프 수정 금지.

---

## 7. 직렬화 검증 규칙

- **BR-24 (round-trip 보장)**: 모든 엔티티 `from_dict(to_dict(x)) == x`. (PBT-02, US-N6 AC-1)
- **BR-25 (미지원 열거값)**: `from_dict` 시 Literal 필드에 미정의 값이면 `ValueError`. 부분 손상 데이터의 조용한 통과 금지.
- **BR-26 (그래프 무결성)**: `RelationshipGraph`의 모든 `Edge.src/dst`는 노드 집합에 존재해야 함. 위반 데이터 역직렬화 시 오류. (PBT-03)

---

## 8. 규칙 → 스토리 추적성 요약

| 규칙 | 스토리/요구 |
|---|---|
| BR-1~4 | US-E1, US-E2, US-N4 |
| BR-5~7 | US-E3, US-N3, US-N5 |
| BR-8~12 | US-E4, US-E5, US-A4, US-N7, FR-C1 |
| BR-13~16 | US-A1, US-A2, US-H4 |
| BR-17~20 | US-A3, US-N2 |
| BR-21~23 | US-A4 |
| BR-24~26 | US-N6 (PBT-02/03) |

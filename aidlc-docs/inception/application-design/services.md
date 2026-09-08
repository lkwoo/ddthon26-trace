# TRACE — 서비스 & 오케스트레이션 (Services)

**단계**: INCEPTION / Application Design
**작성일**: 2026-09-08
**결정**: Q3=A (명시적 순차 파이프라인)

> "서비스"는 여러 컴포넌트를 조율하는 오케스트레이션 단위다. TRACE의 코어 서비스는 로컬 엔진(C2)에 있으며, MCP 서버(C1)와 CLI(C9)는 이를 호출하는 얇은 어댑터다(NFR-CORE-002).

---

## S1. AnalysisService — 프로젝트 분석 오케스트레이션
`analyze_project(path)` 구현. 순차 파이프라인(각 단계 구조화 출력·부분 실패 허용):

```text
scan_project(path)                      [C2]  → assets (+제외규칙, 경로검증)
   ↓
parse assets (source/MD/PDF/OpenAPI/SQL/config/test)  [C2]  → parsed docs (실패는 warning)
   ↓
identify_features(assets)               [C3]  → feature candidates (자동)
   ↓  (feature별)
extract_claims → group_evidence → assign_confidence   [C3]
   ↓
detect_conflicts(feature)               [C5]  → value_mismatch 등
   ↓
generate_feature_knowledge(...)         [C3]
   ↓
save_feature(fk)                        [C4]  → .trace/knowledge/features/<id>.md
   ↓
Result(summary, features, conflicts_count, warnings)
```
- **캐시**: 입력 해시 기준 캐시 히트 시 LLM 재호출 생략(NFR-PERF-003). 캐시는 시연 폴백에도 사용(NFR-AI-004, Q5 캐시).
- **진행 전달**(P1): 단계별 로그/진행 이벤트(FR-ANALYSIS-002).

## S2. KnowledgeQueryService — 지식/충돌 조회
`list_features()`, `get_feature_knowledge(id)`, `get_conflicts(id?)` 구현. C4 로드 + C5 요약. LLM 호출 없음(순수 조회, NFR-PERF-003).

## S3. ImpactService — 작업 영향 분석 오케스트레이션
`analyze_task_impact(task, feature_id?)` 구현:

```text
load relevant knowledge/evidence        [C4]  (feature_id 또는 관련 탐색)
   ↓
gather related conflicts                [C5]  → 충돌 인지 경고(P1)
   ↓
analyze_task(task, context)             [C3/C6]  → Must/Likely/Review + reasons+evidence
   ↓
build ordered change_plan               [C6]
   ↓
Result(summary, impact, related_conflicts, change_plan)
```
- **그라운딩**: 반드시 기존 지식/근거를 컨텍스트로(FR-IMPACT-002). 근거 부족 항목은 Review/LOW(NFR-AI-003).

## S4. LLMService — LLM 접근 캡슐화 (C3 내부)
Claude 호출, 구조화 출력 요청·검증, 재시도(제약 교정), 실패 시 사용자 친화 오류+진단 로깅(§17.3, NFR-REL-002). 결정성 파라미터 고정(NFR-AI-004).

---

## 어댑터 (서비스 소비자)

| 어댑터 | 소비 서비스 | 비고 |
|---|---|---|
| **C1 MCP 서버** | S1·S2·S3 | 도구=서비스 1:1, result envelope 직렬화, 리소스 노출 |
| **C9 CLI (P1)** | S1·S2·S3 | 동일 서비스 재사용, 예제 실행기/폴백 |

## 오케스트레이션 원칙
- 모든 AI 로직은 S1/S3 파이프라인 내부 step(C3)에 위치; 어댑터에는 없음(NFR-CORE-001).
- 각 파이프라인 단계는 독립적으로 실패 처리 가능(FR-ANALYSIS-003, §17).
- 결과는 항상 공통 봉투로 반환, 핵심(요약→충돌→영향→근거) 우선(NFR-MCP-UX-002).

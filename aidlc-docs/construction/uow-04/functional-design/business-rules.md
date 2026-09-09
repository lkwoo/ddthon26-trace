# UOW-04 (Task Impact Analysis) — 비즈니스 규칙 (business-rules)

**단계**: CONSTRUCTION / Functional Design (UOW-04)
**작성일**: 2026-09-09
**출처**: FR-IMPACT-001~006, NFR-AI-003, US-04.1~04.4

---

## BR-CTX — 지식 컨텍스트 그라운딩 (FR-IMPACT-002, Q1/Q2=A)
- **BR-CTX-001**: 영향 분석은 **저장된 지식(FeatureKnowledge·Evidence)**을 컨텍스트로 사용한다.
  일반 LLM 프롬프트 단독 금지 — 컨텍스트가 비면 근거 부족으로 처리(BR-IMP-005).
- **BR-CTX-002 (focus 선정)**: `feature_id` 지정 시 그 Feature만 focus. 미지정 시 전체 FeatureSummary를
  요약으로 주되, 작업 텍스트와 관련도(제목/소스 토큰 겹침) 상위 N개의 상세 지식을 focus에 포함(Q2=A).
- **BR-CTX-003 (화이트리스트)**: `known_sources` = focus Feature들의 `related_sources` ∪ evidence `source` 집합.
  영향 후보 path 판정의 기준(Q1=A).

## BR-IMP — 영향 분류 (FR-IMPACT-003/005, NFR-AI-003)
- **BR-IMP-001 (3범주)**: 각 후보는 `must_change / likely_change / review` 중 하나로 분류되고, **이유(reason) 필수**.
- **BR-IMP-002 (근거 참조)**: 각 후보는 `evidence: list[EvidenceRef]`로 근거(소스·위치·관계)를 참조한다(FR-IMPACT-005).
- **BR-IMP-003 (정렬)**: 카테고리 내 항목은 `path` 순 안정 정렬(결정성·재현성).
- **BR-IMP-004 (허구 path 방지)**: `path ∉ known_sources` 인 후보는 신뢰할 수 없으므로 **review로 강등**하고
  reason에 "근거 밖 추정" 표기(+warning). 근거 없는 must/likely 승격 금지.
- **BR-IMP-005 (근거 부족)**: 근거(evidence)가 없거나 컨텍스트가 빈약한 항목은 `review` + reason "Insufficient evidence" +
  Result.meta confidence LOW로 표기한다(NFR-AI-003). 확신 표현 금지.

## BR-CONFWARN — 충돌 인지 경고 (FR-IMPACT-004, P1, Q3=A)
- **BR-CONFWARN-001**: focus Feature(들)의 **기존 conflicts**(UOW-03 산출·저장)를 `related_conflicts`로 노출한다.
- **BR-CONFWARN-002 (우선 노출)**: related_conflicts가 있으면 `build_result`가 요약 상단에 경고를 얹는다
  (구현 권고 전 강조 — 잘못된 명세 위 구현 방지, US-04.3-AC1).

## BR-PLAN — Change Plan (FR-IMPACT-006, Q4=A)
- **BR-PLAN-001 (순서형)**: 근거 기반 순서 단계 목록을 생성한다. **관련 충돌 해소를 앞 순서**로 둔다
  (예: 검증 정책 해소 → API 정의 → 흐름 수정 → 설정 → 테스트 → 문서).
- **BR-PLAN-002 (자문용)**: Change Plan·영향 분석은 **소스 코드를 자동 수정하지 않는다**. 파일 쓰기 없음(US-04.4-AC2).

## BR-PIPE — 조립·실패 처리 (Q5=A)
- **BR-PIPE-001**: `analyze_task_impact` = build_context → analyze_task(1회 LLM) → to_impact_out → build_result.
- **BR-PIPE-002 (강등)**: analyze_task LLM 실패(검증 소진)는 warning으로 강등하고 **빈 ImpactOut + 안내 메시지**를
  반환한다(예외 전파 금지). related_conflicts는 LLM과 무관하게 저장 지식에서 채워 여전히 노출.
- **BR-PIPE-003 (지식 부재)**: 저장된 지식이 없으면(analyze_project 미실행) 안내 warning("먼저 analyze_project 실행")과
  빈 impact 반환.

## BR-SEC / BR-DET
- **BR-SEC-001**: 로그/warning·reason에 원문·시크릿·절대경로 비노출. path는 rel_path만.
- **BR-DET-001**: 매핑·정렬은 결정적(카테고리별 path 정렬). LLM 문구 변동 외 구조는 재현 가능.

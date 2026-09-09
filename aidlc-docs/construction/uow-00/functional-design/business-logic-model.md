# UOW-00 데모 데이터셋 — 데이터 흐름 & 페르소나 시나리오 (business-logic-model)

**단계**: CONSTRUCTION / Functional Design (UOW-00)
**작성일**: 2026-09-09
**목적**: 데모 자산이 파이프라인을 통해 어떻게 Feature→Conflict→Impact로 흐르는지, 그리고
**세 페르소나 각각의 대표 시나리오**가 어떤 데이터·도구 호출로 뒷받침되는지 정의한다(Units Generation 결정).

> UOW-00에는 실행 로직이 없다(데이터 단위). 여기서 "business logic model"은
> **데이터가 다운스트림에서 소비되는 경로**와 **페르소나 시나리오 매핑**을 뜻한다.

---

## 1. 데이터 흐름 (파이프라인 관점)

```text
demo/ (고정 자산)
  │  requirements(pdf/md) · openapi(yaml) · db(sql) · src(java) · config · tests
  ▼
UOW-01 scan_project ─▶ assets[] + parse_status   (PDF/YAML/SQL/Java 파싱, 부분실패=warning)
  ▼
UOW-02 identify_features ─▶ Feature "Owner Management"(+ 인접 Pet)
        generate_feature_knowledge ─▶ .trace/knowledge/features/owner-management.md
  ▼
UOW-03 extract_claims ─▶ 원자 Claim(subject·predicate·value) + Evidence(source·type)
        assign_confidence ─▶ HIGH/MEDIUM
        detect_conflicts ─▶ C-1 value_mismatch(P0) · C-2 stale_knowledge · C-3 policy_conflict
  ▼
UOW-04 analyze_task_impact ─▶ Must/Likely/Review + 충돌경고 + Change Plan
  ▼
UOW-05 (MCP 노출) / UOW-06 (E2E·walkthrough·스크린샷)
```

- 데이터셋은 이 경로의 **입력 계약**만 제공한다. 위 함수 구현은 각 UOW 소관.
- Hero Feature = **Owner Management**(Q3=A). 전화번호 충돌(C-1)과 정확히 맞물린다.

---

## 2. 페르소나별 대표 시나리오 ↔ 데이터/도구 매핑 (S4)

### P1. 데브 — "어디를 바꿔야 하지?" (변경 착수)
- **트리거/빈도**: 변경 티켓 수령 시(상시). 예: "전화번호를 국제 형식(최대 20자)으로 지원하라".
- **자연어 요청**: "이 프로젝트에서 Owner 전화번호 관련해서 어디를 바꿔야 해?"
- **도구 경로**: `analyze_project` → `list_features` → `analyze_task_impact("전화번호 20자 지원")`
- **데이터 근거**: C-1(telephone 20 vs 10) — Must=Owner.java/schema.sql/openapi, Review=OwnerControllerTests.
- **이점(TRACE 부재 대비)**: 흩어진 5개 파일을 수작업 대조하지 않고, 근거와 함께 영향 파일을 즉시 확보. 문서-구현 드리프트(20 vs 10)를 착수 전에 인지.

### P2. 마이라 — "왜 문제가 났고 또 뭘 고쳐야 하지?" (충돌/장애 조사)
- **트리거/빈도**: 운영 이슈 조사 시. 예: "미래 생년월일을 가진 Pet 데이터가 유입됨".
- **자연어 요청**: "Pet 생년월일 관련해서 뭐가 어긋나 있는지 보여줘."
- **도구 경로**: `get_conflicts` 중심 + 지식 뷰 조회(낡은 지식 확인).
- **데이터 근거**: C-2(maintenance-notes: 검증함 vs Pet.java: 검증없음) — stale_knowledge 드리프트.
- **이점**: 근본 원인 후보(검증 누락)를 빠르게 좁히고, 함께 고쳐야 할 코드·문서(노트)까지 포함해 재발 방지.

### P3. 피엠 — "이 요구사항이 바뀌면 영향은 어디까지?" (요구사항 변경 파급)
- **트리거/빈도**: 정책/요구 변경 평가 시. 예: "모든 Owner에게 이메일을 필수로 도입".
- **자연어 요청**: "Owner에 이메일 필수 정책을 넣으면 개발 범위가 어디까지 번지지?"
- **도구 경로**: 자연어 task → `analyze_task_impact` → Change Plan.
- **데이터 근거**: C-3(요구:email 필수 vs 스펙/코드/DB: 부재) — 엔티티·DTO·schema.sql·OpenAPI·테스트 전반 파급.
- **이점**: 코드를 직접 읽지 않고 구현 복잡도·리스크·결정 지점을 조기 파악. 상충 정책을 착수 전에 발견.

### A1. 클로드 코드 (에이전트, 1급 액터)
- 위 세 사람을 대신해 도구를 자동 호출하고, 구조화된 Result(Feature→Conflict→Impact→Evidence 순)로
  "왜"를 사람에게 설명. 데이터셋은 이 구조화 결과가 실제로 채워지도록 3충돌·다자산을 보장.

---

## 3. Hero 시나리오(E2E 앵커, US-06.1)
가장 강한 단일 경로 = **P1 전화번호 시나리오(C-1)**:
`analyze_project(demo/)` → Feature "Owner Management" → C-1 value_mismatch 검출 →
`analyze_task_impact("전화번호 국제형식 20자 지원")` → Must(Owner.java·schema.sql·openapi)+충돌경고+Change Plan.

이 경로가 무편집으로 통과하는 것이 UOW-06 DoD의 핵심 앵커이며, P2·P3는 같은 데이터셋 위에서
각자 C-2·C-3를 통해 보조 시나리오로 시연된다.

---

## 4. 완료조건 (이 데이터셋이 만족해야 할 것)
- [ ] `analyze_project`가 소비 가능한 고정 데이터셋(결정적).
- [ ] Hero Feature "Owner Management" 1개 이상 식별 가능.
- [ ] 의도적 충돌 3건(C-1 value_mismatch P0 필수, C-2 stale_knowledge, C-3 policy_conflict) 검출 가능.
- [ ] 자산 유형 6종(requirement/api_spec/db_schema/source_code/config/test) 각 1개 이상.
- [ ] 세 페르소나 시나리오 각각 최소 1개 대표 경로 지원.
- [ ] 시크릿·개인정보 없음, 라이선스 출처 표기.

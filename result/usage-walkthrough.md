# TRACE — 페르소나별 사용 여정 (Usage Walkthrough)

세 사람 페르소나(P1 데브 · P2 마이라 · P3 피엠)는 **Claude Code** 안에서 자연어로 요청하고,
에이전트가 TRACE MCP 도구를 호출합니다. 각 여정은 [언제·빈도 → 자연어 요청 → 호출 도구 →
실행 증거 → 이점(TRACE 부재 대비)] 형식입니다.

> **실행 증거**: 아래 흐름은 `python demo/run_demo.py`로 **API 키 없이 결정적으로 재현**됩니다
> (콘솔 출력 원문: [`hero-demo-output.txt`](hero-demo-output.txt)). GUI 스크린샷 캡처 절차는 [`README.md`](README.md) 참고.

---

## P1. 데브 — 낯선 코드베이스 이해 (Understand)

- **언제·빈도**: 새 프로젝트/팀에 투입된 **첫 며칠**, 기능을 건드리기 전마다.
- **자연어 요청**: "이 프로젝트를 분석하고, Owner 등록 기능이 어떻게 동작하는지 근거와 함께 보여줘."
- **호출 도구**: `trace_analyze_project` → `trace_list_features` → `trace_get_feature_knowledge("owner-registration")`
- **실행 증거** (hero-demo-output.txt ①②):
  ```
  6개 Feature 분석 완료 (자산 48개, 충돌 9건)
    - billing-invoicing: Billing & Invoicing (충돌 1건)
    - clinic-configuration: Clinic Configuration (충돌 1건)
    - owner-registration: Owner Registration (충돌 3건)
    - pet-management: Pet Management (충돌 1건)
    - vet-directory: Veterinarian Directory (충돌 1건)
    - visit-scheduling: Visit Scheduling (충돌 2건)
  ```
  48개 자산이 5개 도메인의 6개 Feature로 재구성되고, 각 지식은 `trace://feature/<id>` 리소스
  (Markdown 본문)와 구조화 claims/confidence로 제공.
- **이점**: TRACE 없이는 48개 파일(소스·스펙·스키마·설정·테스트)을 직접 읽어 머릿속에서 조립해야 함.
  TRACE는 **자산을 기능 단위로 재구성 + 근거 참조**를 즉시 제공 → 온보딩 시간 단축, 추측 대신 근거.

---

## P2. 마이라 — 정책 불일치 조사 (Maintain)

- **언제·빈도**: 운영 이슈·정책 불일치 리포트가 올라올 때마다(수시).
- **자연어 요청**: "문서와 구현이 어긋난 부분이 있으면 근거와 함께 보여줘."
- **호출 도구**: `trace_get_conflicts`
- **실행 증거** (hero-demo-output.txt ③) — 5개 도메인에 걸친 **9건**:
  ```
  - [value_mismatch]  owner.telephone.max_length   : 20(owner-spec.pdf) vs 10(openapi/code/db)
  - [value_mismatch]  visit.description.max_length : 255(visit-spec.pdf) vs 8192(openapi/code/db)
  - [value_mismatch]  invoice.amount.precision     : DECIMAL(10,2)(billing-spec.pdf) vs (8,2)(code/db)
  - [policy_conflict] owner.email.required         : required(spec) vs absent(openapi/code/db)
  - [policy_conflict] owner.address.required       : required(spec) vs absent(code)
  - [policy_conflict] vet.specialties.min_one      : required(vet-spec) vs absent(code)
  - [stale_knowledge] pet.birthDate.future_date_validation : rejected(notes) vs accepted(code)
  - [stale_knowledge] visit.date.past_date_validation      : rejected(notes) vs accepted(code)
  - [stale_knowledge] billing.tax.enforcement_default      : enforced(notes) vs disabled(config)
  ```
  세 유형(값 불일치·정책 충돌·오래된 지식)이 각 3건씩, **결정적 구조 비교**로 검출되고 각 값의 출처
  파일이 붙음.
- **이점**: TRACE 없이는 48개 파일 5개 도메인에 흩어진 이 9건을 사람이 일일이 대조해야 하고 대부분 놓친다
  (telephone 20/10 같은 한 건도 스펙 PDF·OpenAPI·Java·SQL 4곳을 열어봐야 확인됨). TRACE는 **어긋난
  지점과 양쪽 근거**를 한눈에 → 조사 시간 단축, 놓친 불일치 방지.

---

## P3. 피엠 — 변경 파급 가늠 (Plan Change)

- **언제·빈도**: 새 요구사항/정책 변경을 검토할 때(스프린트 계획·착수 직전).
- **자연어 요청**: "Owner 등록에 SMS 인증을 추가하려는데, 영향 범위와 먼저 볼 리스크를 알려줘."
- **호출 도구**: `trace_analyze_task_impact("Add SMS verification to Owner registration", "owner-registration")`
- **실행 증거** (hero-demo-output.txt ④):
  ```
  ⚠ 구현 착수 전 확인해야 할 기존 충돌 (owner-registration 관련 3건):
    - [value_mismatch]  owner.telephone.max_length (20 vs 10)
    - [policy_conflict] owner.email.required
    - [policy_conflict] owner.address.required

  Must Change:   src/.../owner/Owner.java  — 전화번호 검증·SMS 인증 연동 지점
  Likely Change: openapi/petclinic-rest.yaml — telephone 스키마 갱신 가능
  Review:        db/schema.sql — telephone 컬럼 길이 확인

  Change Plan (충돌 해소 우선):
    1. telephone 길이 충돌(문서 20 vs 구현 10) 먼저 해소
    2. OpenAPI telephone 스키마·검증 규칙 정의
    3. Owner 검증 로직에 SMS 인증 흐름 추가
    4. 통합/컨트롤러 테스트 갱신
    5. 문서(spec) 동기화
  ```
- **이점**: TRACE 없이는 영향 범위를 감으로 추정 → 낡은 명세 위에 구현. TRACE는 **기존 충돌을 착수 전
  경고**하고 근거 기반 3범주 분류 + 순서형 Change Plan을 제시 → 잘못된 전제 위 구현 방지.

---

## 공통 흐름 요약 (Hero)

```
analyze_project → list_features → get_feature_knowledge → get_conflicts → analyze_task_impact
     (지식화)         (탐색)            (이해)              (불일치)          (영향·계획)
```
세 페르소나 모두 **같은 코어**를 각자의 진입점에서 소비합니다(MCP 도구 또는 폴백 CLI). 실행 증거는
`hero-demo-output.txt`에서 전 구간을 확인할 수 있습니다.

# 마이라(Maintain) — "왜 이 문제가 생겼고, 무엇을 고쳐야 하지?"

> 이 문서는 **마이라** 페르소나가 TRACE를 사용해 운영 이슈의 근본 원인을 근거와 함께 찾아내는
> 과정을 순차적으로 기록한 시나리오다. 각 단계의 **자연어 요청 → 호출된 MCP tool → 실제 작업 화면
> (콘솔 출력 원문) → 마이라가 읽어낸 것 / 다음 행동** 순으로 이어진다.
>
> **이 판의 작업 화면은 실제 Claude(Amazon Bedrock, `global.anthropic.claude-opus-4-8`)로
> 라이브 추출한 지식을 조회한 결과다.** 충돌 검출은 실제 코어 코드의 결정적 구조 비교로 이뤄지며,
> 이 조회 단계들은 저장된 지식만 읽으므로 **LLM 재호출 없이** 동작한다.
>
> - **라이브 지식 생성**: `python demo/tools/extract_features_live.py` (Bedrock 자격증명 필요, `.env` 참고)
> - **API 키 없이 결정적 재현**: `python demo/run_demo.py` (FakeLLM, 큐레이션된 9충돌)

---

## 👤 업무 명세 (Task Spec)

| 항목 | 내용 |
|---|---|
| **누가** | 마이라 — petclinic 운영/유지보수 담당. 운영 리포트를 받아 원인을 파고든다. |
| **들어온 이슈** | *"청구서에 부가세(VAT)가 안 붙는다는 문의가 늘고 있다. 스펙엔 기본 적용이라는데 왜 안 되지?"* |
| **핵심 질문** | *"왜 이 문제가 생겼고(근본 원인), 무엇을·어디를 고쳐야 하지?"* |
| **언제·빈도** | 운영 이슈·정책 불일치 리포트가 올라올 때마다(수시). |
| **성공 기준** | 추측이나 로그 grep이 아니라, **문서·구현·설정의 어느 값이 어긋났는지 양쪽 근거로** 짚어내고, 함께 갱신할 지점(코드·설정·문서·테스트)을 특정한다. |

**TRACE 없이는**: 세금이 왜 안 붙는지 알려면 `application.properties`, `BillingService.java`,
`billing-spec.pdf`, `maintenance-notes.md`를 각각 열어 값을 눈으로 대조해야 한다. 대부분 "코드는
맞는 것 같은데…"에서 막히고, 설정 한 줄(`billing.tax.enforcement=disabled`)이 원인이라는 걸
놓치기 쉽다.

**마이라의 도구 흐름**: `trace_get_conflicts` → `trace_get_conflicts(feature=…)` →
`trace_get_feature_knowledge("clinic-configuration")`.

---

## STEP 1 — 어긋난 지점을 전부 펼쳐 훑는다

**자연어 요청 (Claude Code)**
```
문서와 구현이 어긋난 부분이 있으면 전부 근거와 함께 보여줘.
```

**호출된 tool**: `trace_get_conflicts` (저장된 지식만 읽음, LLM 미호출)

**실제 작업 화면** (Bedrock opus 라이브 지식 기준)
```text
⚠ 충돌 39건이 감지되었습니다 (아래 우선 확인).
전체 충돌 39건

유형 분포: value_mismatch 20 · policy_conflict 15 · stale_knowledge 4
```

<details>
<summary>전체 39건 펼치기 (도메인별 발췌·클릭)</summary>

```text
[billing]
  - [policy_conflict] invoice.tax.vat_enforced_by_default : absent@BillingService.java, enforced@billing-spec.pdf
  - [stale_knowledge] billing.tax.enforcement.default_policy : disabled@application.properties, enforced@billing-spec.pdf
  - [value_mismatch] invoices.amount.decimal_precision : 10@billing-spec.pdf, 8@schema.sql
  - [value_mismatch] invoice_items.amount.nullable : NOT NULL@schema.sql, nullable(no constraint)@InvoiceItem.java
  - [value_mismatch] BillingService.computeTotal.* (empty/null→0, sums_item_amounts) : 테스트 vs 구현 표현차 3건
[owner]
  - [value_mismatch] owner.telephone.max_length : 10@schema.sql, 20@owner-management-spec.pdf
  - [policy_conflict] owner.email.required / owner.email.format_validation : required@spec vs absent@code/db
  - [policy_conflict] owner.address.required : required@spec vs absent/nullable@openapi/Owner.java/schema.sql
  - [value_mismatch] owner.firstName.required / owner.lastName.required : NOT NULL@schema.sql vs required@openapi
[pet]
  - [policy_conflict] pet.birthDate.future_date_validation : 미래일자 거부@notes vs absent@openapi
  - [stale_knowledge] pet.name.required · [policy_conflict] pet.name.unique_within_owner
  - [value_mismatch] pet.type.* / pet.owner_id.required / pet.*.endpoint (controller vs test vs openapi)
[vet]
  - [policy_conflict] vet.specialties.min_count : 1@vet-directory-spec.pdf vs absent@schema.sql
  - [policy_conflict] vet.specialties.required_before_publish / represented_in_openapi_schema
  - [value_mismatch] GET /vets.base_path : /api/vets@VetRestController.java vs /vets@openapi
[visit]
  - [policy_conflict] visit.date.no_past_date_allowed : true@notes vs absent@schema.sql
  - [value_mismatch] visit.description.max_length : 255 vs 8192
  - [policy_conflict] visit.* (date.required / description.required / pet_id.required / unique_date_per_pet)
```
</details>

**마이라가 읽어낸 것**
- 이슈는 세금인데, 목록 상단에서 **세금 관련 충돌 두 건**이 바로 눈에 띈다:
  `invoice.tax.vat_enforced_by_default`(코드), `billing.tax.enforcement.default_policy`(설정).
- 각 값에 **출처 파일이 붙어** 있어, 다음에 어느 Feature를 좁혀 볼지 즉시 정해진다 → billing / clinic.

---

## STEP 2 — 세금 이슈로 범위를 좁힌다

**자연어 요청**
```
세금(tax) 관련 충돌만 근거 위치까지 자세히 보여줘. (clinic-configuration, billing-invoicing)
```

**호출된 tool**: `trace_get_conflicts(feature="clinic-configuration")` · `trace_get_conflicts(feature="billing-invoicing")`

**실제 작업 화면**
```text
=== clinic-configuration (충돌 1건) ===
  - [stale_knowledge] billing.tax.enforcement.default_policy
      해석: [문서/지식이 구현과 어긋남] disabled(config/application.properties) vs enforced(requirements/billing-spec.pdf)
        · disabled  @ config/application.properties  (billing.tax.enforcement)
        · enforced   @ requirements/billing-spec.pdf   (REQ-2)

=== billing-invoicing (충돌 6건 중 세금 관련) ===
  - [policy_conflict] invoice.tax.vat_enforced_by_default : absent@BillingService.java, enforced@billing-spec.pdf
  - [value_mismatch]  invoices.amount.decimal_precision   : 10@billing-spec.pdf, 8@schema.sql
```

**마이라가 읽어낸 것**
- 원인이 **두 겹**으로 드러난다:
  1. **설정** `config/application.properties`의 `billing.tax.enforcement = disabled` — 스펙(REQ-2)은
     `enforced`인데 운영 설정이 꺼져 있다 (stale_knowledge, C-9).
  2. **코드** `BillingService.java`에 VAT 기본 적용 로직이 **absent** — 스펙은 기본 적용을 요구
     (policy_conflict).
- 즉 "세금이 안 붙는" 현상은 버그 한 줄이 아니라 **설정이 꺼져 있고 + 코드도 강제하지 않는** 이중
  드리프트다. 근거 위치(`billing.tax.enforcement`, `REQ-2`)까지 붙어 바로 확인 가능하다.

---

## STEP 3 — 근본 원인 Feature의 지식으로 확정한다

**자연어 요청**
```
clinic-configuration 기능의 지식을 근거와 함께 보여줘.
```

**호출된 tool**: `trace_get_feature_knowledge("clinic-configuration")`

**실제 작업 화면** (Bedrock opus 라이브)
```text
Feature: 클리닉 설정 및 세금 정책
설명: 애플리케이션 전역 설정과 청구 세금 적용 기본 정책을 관리하는 기능.
      세금 기본 적용(enforced) 문서 지식과 설정값(disabled) 사이의 드리프트(C-9)가 존재한다.
관련 자산: requirements/billing-spec.pdf, requirements/maintenance-notes.md, config/application.properties

Claims 8건:
  - billing.tax.enforcement.default_policy = enforced      ← 문서/지식이 말하는 정책
  - billing.currency.value = KRW
  - server.port.value = 9966
  - spring.datasource.url.value = jdbc:h2:mem:petclinic
  - spring.datasource.username.value = demo_user
  - spring.datasource.password.value = CHANGE_ME_PLACEHOLDER
  - spring.h2.console.enabled.value = true
  - spring.jpa.hibernate.ddl-auto.value = none
```

**마이라가 읽어낸 것 — 무엇을 고칠지 확정**
- 이 Feature가 세금 기본 정책을 **enforced**로 지식화하고 있는데, 실제 설정이 이를 배신한다.
  고칠 지점이 근거와 함께 명확해진다:
  1. **설정**: `application.properties`의 `billing.tax.enforcement`를 `enabled`로 전환(또는 코드가
     강제하도록 수정).
  2. **코드**: `BillingService.java`에 VAT 기본 적용 로직 추가(policy_conflict 해소).
  3. **문서/지식 동기화**: `maintenance-notes.md`·`billing-spec.pdf`와 실제 동작을 일치시킴.
  4. **회귀 방지**: 세금이 기본 적용됨을 검증하는 테스트 추가.
- 덤으로 `invoices.amount.decimal_precision`(스펙 10 vs DB 8)도 청구 금액에 영향을 줄 수 있어 함께
  검토 대상으로 메모한다.

> ℹ️ (보안 관측) Claim 목록에서 `spring.datasource.password.value = CHANGE_ME_PLACEHOLDER`가 그대로
> 노출된다 — TRACE는 설정 자산도 지식화하므로, 운영 전 실제 시크릿이 평문으로 들어가 있지 않은지
> 마이라가 점검하는 계기도 된다(데모 데이터셋은 더미 플레이스홀더만 사용).

---

## ✅ 마이라 여정 결과

**성공적으로 수행된 것**
1. 어긋난 지점 전체(39건)를 유형 분포와 함께 훑고, 이슈 키워드로 후보를 좁혔다 (STEP 1).
2. "세금 미적용"의 원인을 **설정(disabled) + 코드(absent)** 이중 드리프트로, **양쪽 근거·위치와
   함께** 특정했다 (STEP 2).
3. 근본 원인 Feature 지식으로 **무엇을·어디를 고칠지**(설정·코드·문서·테스트) 확정했다 (STEP 3).

**TRACE 부재 대비 이점**
- 조사: "4개 파일을 열어 값 대조 + 로그 추적" → "충돌 목록에서 근거와 함께 원인 지목".
- 재발 방지: 문서/지식이 구현과 어긋난 지점(stale_knowledge)을 **명시적으로** 드러내, 같은 드리프트가
  다시 쌓이는 것을 막는다.

> 마이라가 짚은 충돌들은 **데브**가 온보딩에서 본 그 지식과, **피엠**이 변경 영향에서 경고받는
> 그 충돌과 동일한 코어에서 나온다.

---

## 🔁 재현 방법

```bash
# (A) 라이브 지식 생성 후 조회 (실제 opus) — 위 화면의 근거
python demo/tools/extract_features_live.py             # demo/.trace/knowledge/features/*.md 생성(비결정적)
#  이후 조회는 저장 지식을 읽음(LLM 미호출):
#    trace conflicts --path demo
#    trace conflicts --path demo --feature clinic-configuration
#    trace knowledge clinic-configuration --path demo

# (B) API 키 없이 결정적 재현 — 큐레이션된 9충돌(세금 C-9 포함), 매 실행 동일
python demo/run_demo.py
```

- 결정적 모드의 세금 충돌은 `billing.tax.enforcement_default : enforced(notes) vs disabled(config)`로,
  전체 출력은 [`result/hero-demo-output.txt`](../../../result/hero-demo-output.txt) 참고.
- 페르소나 세 명 요약 여정은 [`result/usage-walkthrough.md`](../../../result/usage-walkthrough.md) 참고.

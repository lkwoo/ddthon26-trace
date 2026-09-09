# 데브(Understand) — 낯선 코드베이스, 하루 만에 근거로 이해하기

> 이 문서는 **데브** 페르소나가 TRACE를 사용해 실제 업무를 성공적으로 수행하는 과정을
> 순차적으로 기록한 시나리오다. 각 단계의 **자연어 요청 → 호출된 MCP tool → 실제 작업 화면
> (콘솔 출력 원문) → 데브가 읽어낸 것 / 다음 행동** 순으로 이어진다.
>
> 아래 모든 작업 화면은 `demo/scenario/dev/capture_dev_scenario.py`로 **API 키 없이 결정적으로
> 재현**된다(FakeLLM). 스캔·파싱·지식 저장·충돌 검출은 모두 실제 코어 코드가 수행한다.

---

## 👤 업무 명세 (Task Spec)

| 항목 | 내용 |
|---|---|
| **누가** | 데브 — 이번 주에 petclinic 팀에 합류한 개발자. 코드베이스가 낯설다. |
| **핵심 질문** | *"이 프로젝트에 뭐가 있고, 내가 곧 손댈 Owner 등록 기능은 어떻게 동작하지? 어디를 바꿔야 하지?"* |
| **언제·빈도** | 새 프로젝트/팀에 투입된 **첫 며칠**, 그리고 기능을 건드리기 전마다. |
| **주어진 것** | 5개 도메인(Owner/Pet/Vet/Visit/Billing)에 걸친 **48개 자산** — 요구사항 PDF·OpenAPI·DB 스키마·Java 소스·설정·테스트가 폴더별로 흩어져 있음. |
| **성공 기준** | 파일을 일일이 열어 머릿속으로 조립하지 않고, **Feature 단위로 재구성된 지식 + 각 사실의 근거(Evidence)**를 확보한다. 곧 손댈 기능에 이미 어긋난 지점이 있으면 착수 전에 안다. |

**TRACE 없이는**: 48개 파일을 직접 열어(`requirements/*.pdf`, `openapi/*.yaml`, `db/schema.sql`,
`src/**/*.java`, `config/*`, `tests/*`) Feature 경계를 스스로 그리고, 문서와 코드가 맞는지 눈으로
대조해야 한다. 온보딩이 며칠씩 걸리고, telephone 길이가 스펙엔 20인데 코드엔 10이라는 사실 같은 건
대부분 놓친 채 개발에 들어간다.

**데브의 도구 흐름**: `trace_analyze_project` → `trace_list_features` →
`trace_get_feature_knowledge("owner-registration")` → 지식 본문 리소스 조회.

---

## STEP 1 — 프로젝트를 통째로 지식화한다

**자연어 요청 (Claude Code)**
```
이 프로젝트를 분석해줘.
```

**호출된 tool**: `trace_analyze_project`
(스캔 → Feature 식별 → Claim/Evidence 추출 → 결정적 충돌 검출 → 지식 저장)

**실제 작업 화면**
```text
======================================================================
STEP 1 · trace_analyze_project — "이 프로젝트를 분석해줘"
======================================================================
⚠ 충돌 9건이 감지되었습니다 (아래 우선 확인).
6개 Feature 분석 완료 (자산 48개, 충돌 9건)
자산 48개 / Feature 6개 / 충돌 9건
```

**데브가 읽어낸 것**
- 흩어져 있던 **48개 자산**이 한 번의 호출로 **6개 Feature**로 재구성됐다.
- 시작부터 **9건의 문서-구현 충돌**이 경고로 떠서, "일단 코드부터 읽자"가 아니라 "무엇이 어긋나
  있는지부터 보자"로 방향이 잡힌다.
- 이후 조회는 저장된 지식을 읽으므로 **API 키 없이도** 동작한다(cache fallback).

---

## STEP 2 — 무슨 기능들이 있는지 지도를 본다

**자연어 요청**
```
어떤 기능들이 있는지 목록으로 보여줘.
```

**호출된 tool**: `trace_list_features` (저장된 지식만 읽음, LLM 미호출)

**실제 작업 화면**
```text
======================================================================
STEP 2 · trace_list_features — "어떤 기능들이 있어?"
======================================================================
  - billing-invoicing: Billing & Invoicing (충돌 1건)
  - clinic-configuration: Clinic Configuration (충돌 1건)
  - owner-registration: Owner Registration (충돌 3건)
  - pet-management: Pet Management (충돌 1건)
  - vet-directory: Veterinarian Directory (충돌 1건)
  - visit-scheduling: Visit Scheduling (충돌 2건)
```

**데브가 읽어낸 것**
- 코드베이스의 **기능 지도**가 한눈에 들어온다. 폴더 구조가 아니라 **의미 단위(Feature)**다.
- 곧 손댈 **`owner-registration`에 충돌이 3건**으로 가장 많다 — 여기를 먼저 깊게 봐야 한다는
  신호. 다음 단계의 대상이 자연스럽게 정해진다.

---

## STEP 3 — 손댈 기능을 근거와 함께 파고든다

**자연어 요청**
```
Owner 등록 기능이 어떻게 동작하는지 근거와 함께 설명해줘.
```

**호출된 tool**: `trace_get_feature_knowledge("owner-registration")`

**실제 작업 화면**
```text
======================================================================
STEP 3 · trace_get_feature_knowledge("owner-registration") — "Owner 등록 기능을 근거와 함께 설명해줘"
======================================================================
Feature: Owner Registration (owner-registration)
설명: 반려동물 주인 등록·연락처·이메일·주소 정책
관련 자산 4개:
  - requirements/owner-management-spec.pdf
  - openapi/petclinic-rest.yaml
  - db/schema.sql
  - src/main/java/org/springframework/samples/petclinic/owner/Owner.java

Claims 3건 (subject · predicate = value):
  - owner.address.required = required
  - owner.email.required = required
  - owner.telephone.max_length = 10

Confidence 3건:
  - owner.address.required: Confidence.LOW — 근거 2건, 상이값 2개, supports 1건, contradicts 1건
  - owner.email.required: Confidence.LOW — 근거 4건, 상이값 2개, supports 1건, contradicts 3건
  - owner.telephone.max_length: Confidence.LOW — 근거 4건, 상이값 2개, supports 4건, contradicts 0건

이 Feature의 충돌 3건:
  - [policy_conflict] owner.address.required
      [요구와 구현 부재의 충돌] owner.address.required: absent(src/main/java/org/springframework/samples/petclinic/owner/Owner.java), required(requirements/owner-management-spec.pdf)
      값: absent@src/main/java/org/springframework/samples/petclinic/owner/Owner.java, required@requirements/owner-management-spec.pdf
  - [policy_conflict] owner.email.required
      [요구와 구현 부재의 충돌] owner.email.required: absent(db/schema.sql), required(requirements/owner-management-spec.pdf)
      값: absent@db/schema.sql, required@requirements/owner-management-spec.pdf
  - [value_mismatch] owner.telephone.max_length
      [값 불일치] owner.telephone.max_length: 10(db/schema.sql), 20(requirements/owner-management-spec.pdf)
      값: 10@db/schema.sql, 20@requirements/owner-management-spec.pdf

지식 본문 리소스: trace://feature/owner-registration
```

**데브가 읽어낸 것**
- 이 기능을 이루는 **4개 자산**(스펙 PDF · OpenAPI · DB 스키마 · Java 소스)이 무엇인지 즉시 안다 —
  더 이상 어느 파일을 열어야 할지 헤매지 않는다.
- 각 규칙이 **Claim(subject·predicate=value)**으로 정규화돼 있고, 그 값이 **어느 파일에서 왔는지**가
  Evidence로 붙어 있다. "코드가 그렇다"가 아니라 "`Owner.java`가 그렇다"까지 짚힌다.
- **Confidence가 세 건 모두 LOW**인 이유가 근거 통계로 설명된다. `owner.telephone.max_length`는
  supports 4 / contradicts 0인데도 LOW인 것은 **상이값이 2개(10 vs 20)** 존재하기 때문 —
  근거끼리 값이 갈리면 신뢰도를 낮춘다는 뜻이다. 데브는 "이 값은 그대로 믿으면 안 된다"를 근거로 안다.
- **충돌 3건**의 정체가 드러난다:
  - `owner.telephone.max_length` — 요구사항 PDF는 **20**, DB 스키마는 **10** (값 불일치).
  - `owner.email.required` — 스펙은 **필수**인데 DB엔 컬럼이 **없음** (정책 충돌).
  - `owner.address.required` — 스펙은 **필수**인데 `Owner.java`엔 강제가 **없음** (정책 충돌).

> 이 시점에서 데브는 아직 코드 한 줄 고치지 않았지만, "Owner 등록을 건드리려면 최소한 telephone
> 길이(20 vs 10)와 email/address 필수 정책부터 정리해야 한다"를 **근거와 함께** 파악했다.

---

## STEP 4 — 지식 본문(리소스)까지 열어본다

**자연어 요청**
```
그 지식 본문을 그대로 보여줘. (trace://feature/owner-registration)
```

**호출**: MCP resource read — `trace://feature/owner-registration`

**실제 작업 화면**
```text
======================================================================
STEP 4 · resource read — "trace://feature/owner-registration" 본문
======================================================================
# 지식 개요

(데모 본문)
```

> ℹ️ 결정적 데모(FakeLLM) 모드에서는 본문 Markdown이 고정 플레이스홀더(`(데모 본문)`)로
> 대체된다. 실제 Claude를 붙이는 `--live` 모드에서는 이 리소스에 LLM이 생성한 서술형 지식 요약이
> 담긴다. **구조화된 substance(Claims·Confidence·Conflicts)는 두 모드 모두 실제 코어가 생성**하며,
> 데브의 판단은 STEP 3의 구조화 지식만으로 이미 성립한다.

---

## ✅ 데브 여정 결과

```text
======================================================================
데브 여정 완료 — 낯선 코드베이스를 Feature 단위 + 근거로 이해
======================================================================
```

**성공적으로 수행된 것**
1. 48개 자산 → **6개 Feature**로 재구성 (STEP 1).
2. 손댈 지점을 **충돌 개수**로 우선순위화 (STEP 2, `owner-registration` 3건).
3. 대상 기능을 **Claim + Evidence + Confidence + Conflict**로 근거와 함께 이해 (STEP 3).

**TRACE 부재 대비 이점**
- 온보딩: "48개 파일을 열어 머릿속에서 조립" → "Feature 단위 지식 조회 한 번".
- 판단 근거: "코드가 이런 것 같다(추측)" → "이 값은 이 파일에서 왔고, 스펙과 이렇게 갈린다(근거)".
- 착수 전 리스크 인지: telephone 20/10 같은 불일치를 **코드를 짜기 전에** 안다 — stale spec 위에서
  자신 있게 잘못 구현하는 것을 방지.

> 데브가 파악한 `owner-registration`의 충돌 3건은, **피엠**이 "Owner 등록에 SMS 인증 추가"의 영향을
> 분석할 때(`trace_analyze_task_impact`) *착수 전 확인해야 할 기존 충돌*로 다시 등장한다. 세 페르소나가
> **같은 코어 지식**을 각자의 진입점에서 소비한다.

---

## 🔁 재현 방법

```bash
# 리포 루트에서 (API 키 불필요, 매 실행 동일)
python demo/scenario/dev/capture_dev_scenario.py
```

- 이 하니스는 `demo/run_demo.py`의 결정적 FakeLLM 스크립트를 재사용하며, 위 STEP 1~4의 콘솔
  출력을 그대로 생성한다.
- Hero 흐름(피엠의 impact 분석 포함) 전체 출력은 `python demo/run_demo.py` 및
  [`result/hero-demo-output.txt`](../../../result/hero-demo-output.txt) 참고.
- 페르소나 세 명 요약 여정은 [`result/usage-walkthrough.md`](../../../result/usage-walkthrough.md) 참고.

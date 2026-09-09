# 피엠(Plan Change) — "이 요구사항이 바뀌면 영향은 어디까지 번지지?"

> 이 문서는 **피엠** 페르소나가 TRACE를 사용해 새 요구사항의 변경 영향과 착수 전 리스크를 근거와
> 함께 가늠하는 과정을 기록한 시나리오다. **자연어 요청 → 호출된 MCP tool → 실제 작업 화면(콘솔
> 출력 원문) → 피엠이 읽어낸 것 / 다음 행동** 순으로 이어진다.
>
> **이 판의 작업 화면은 실제 Claude(Amazon Bedrock, `global.anthropic.claude-opus-4-8`)로
> 라이브 실행한 결과다.** 저장된 지식에 그라운딩해 영향을 분류하며, `analyze_task_impact`는 영향
> 매핑을 위해 실제 opus를 1회 호출한다(비결정적). **소스 코드를 자동 수정하지는 않는다 — 자문용이다.**
>
> - **라이브 재현**: `.env`(Bedrock 자격증명) 설정 후 아래 "재현 방법" 참고
> - **API 키 없이 결정적 재현**: `python demo/run_demo.py` (FakeLLM, 매번 동일)

---

## 👤 업무 명세 (Task Spec)

| 항목 | 내용 |
|---|---|
| **누가** | 피엠 — 스프린트 계획을 세우고 새 요구사항의 착수 여부·순서를 판단한다. |
| **검토 중인 요구사항** | *"Owner 등록에 SMS 인증을 추가하자."* |
| **핵심 질문** | *"이걸 건드리면 영향이 어디까지 번지고, 착수 전에 먼저 봐야 할 리스크는 뭐지?"* |
| **언제·빈도** | 새 요구사항·정책 변경을 검토할 때(스프린트 계획·착수 직전). |
| **성공 기준** | 감이 아니라 **근거 기반 영향 범위(Must/Likely/Review)**와 **착수 전 기존 충돌 경고**, 그리고 **충돌 해소를 앞세운 실행 순서(Change Plan)**를 확보한다. |

**TRACE 없이는**: 영향 범위를 경험과 감으로 추정하고, telephone이 스펙 20/코드 10으로 어긋나 있다는
사실을 모른 채 "SMS 인증만 붙이면 되겠지" 하고 착수한다. 낡은 전제 위에 구현이 쌓여 재작업으로 이어진다.

**피엠의 도구 흐름**: `trace_analyze_task_impact("Add SMS verification to Owner registration", "owner-registration")`.

---

## STEP 1 — 변경 영향과 착수 전 리스크를 한 번에 가늠한다

**자연어 요청 (Claude Code)**
```
Owner 등록에 SMS 인증을 추가하려는데, 영향 범위와 먼저 봐야 할 리스크를 알려줘.
```

**호출된 tool**: `trace_analyze_task_impact("Add SMS verification to Owner registration", "owner-registration")`

**실제 작업 화면** (Bedrock opus 라이브)
```text
영향 후보 11건 (must 5 / likely 4 / review 2), 관련 충돌 6건

⚠ 착수 전 확인할 기존 충돌:
  - [value_mismatch]  owner.telephone.max_length   : 10(db/schema.sql) vs 20(owner-management-spec.pdf)
  - [policy_conflict] owner.email.required          : required(spec) vs absent(db/schema.sql)
  - [policy_conflict] owner.email.format_validation : required(spec) vs absent(OwnerDto.java)
  - [policy_conflict] owner.address.required        : required(spec) vs absent/nullable(openapi/Owner.java/schema.sql)
  - [value_mismatch]  owner.firstName.required      : NOT NULL(schema.sql) vs required(openapi)
  - [value_mismatch]  owner.lastName.required       : NOT NULL(schema.sql) vs required(openapi)

Must Change:
  - openapi/petclinic-rest.yaml               : SMS 코드 발송/검증 엔드포인트·인증 필드를 API 계약에 정의. telephone maxLength=10(C-1) 충돌도 이 시점에 정리.
  - requirements/owner-management-spec.pdf    : SMS 인증 절차·전화번호 검증·인증 흐름을 명세에 등록. REQ-1(20자·국제형식)과 정합.
  - .../owner/OwnerRestController.java         : 등록(POST /owners) 흐름에 SMS 인증 단계(코드 발송·검증 게이트) 통합.
  - .../owner/OwnerService.java                : 등록 트랜잭션 경계에서 인증 상태 확인·검증 로직 배치.
  - tests/OwnerControllerTests.java            : 인증 흐름(발송·검증·미인증 등록 거부) 테스트 추가. 기존 telephoneMaxLengthIsTen(C-1) 가정 수정.

Likely Change:
  - db/schema.sql                              : phone_verified 컬럼/인증코드 저장 구조, telephone VARCHAR(10)(C-1) 확장 검토.
  - .../owner/Owner.java                        : 인증 상태 저장 또는 국제형식 telephone 제약 조정. C-1 선결 필요.
  - .../owner/OwnerDto.java                     : 인증 코드/검증 상태 필드 추가 또는 telephone 제약 정합화(C-1).
  - .../owner/OwnerMapper.java                  : 인증 필드 추가 시 매핑 갱신.

Review:
  - .../model/Person.java                       : 이름 공통 상위 클래스. 전화번호가 상위로 이동돼 있지 않은지 확인.
  - .../owner/OwnerRepository.java              : 인증 상태 조회/저장이 별도로 필요하면 영향 가능(근거는 간접적).

Change Plan:
  1. 충돌 선결: C-1(telephone 10 vs 요구 20, 국제형식) 정책 확정 — SMS 인증은 국제형식 전화번호를 전제.
  2. SMS 인증 요구사항 명세화(발송·검증·미인증 등록 거부·만료/재발송)를 owner-management-spec.pdf에 추가.
  3. openapi에 인증 발송/검증 엔드포인트·인증상태 필드 정의, telephone maxLength 정합화.
  4. db/schema.sql에 telephone 길이 확장 및 phone_verified(또는 코드 저장) 스키마 반영.
  5. Owner/OwnerDto 검증 제약 정합화 및 인증 상태 필드 추가, OwnerMapper 매핑 갱신.
  6. OwnerService/OwnerRestController에 SMS 인증 흐름 통합(등록 전 검증 게이트).
  7. OwnerControllerTests에 인증 흐름 테스트 추가 및 telephoneMaxLengthIsTen 등 기존 가정 수정.
  8. 문서/명세 최종 정합성 확인.
```

**피엠이 읽어낸 것**
- **착수 전 경고가 먼저 온다.** SMS 인증을 붙이기도 전에, Owner 등록에 이미 쌓여 있던 **충돌 6건**을
  근거와 함께 알려준다. 특히 `owner.telephone.max_length`(스펙 20 vs DB 10, C-1)는 **SMS 인증의
  전제(국제형식 전화번호)**와 직결돼 — 이걸 방치하면 인증 코드를 엉뚱한 길이 필드에 붙이게 된다.
- **영향이 3범주로 근거와 함께 분류**된다. "어디를 반드시 바꿔야 하고(Must 5), 아마 바꿀 것이고
  (Likely 4), 확인만 하면 되는지(Review 2)"가 파일 단위로 짚힌다. Controller·Service·OpenAPI·스펙·
  테스트가 Must, 스키마·엔티티·DTO·Mapper가 Likely, 상위 클래스·Repository가 Review.
- **Change Plan이 충돌 해소를 1번으로 앞세운다.** "SMS부터 짜자"가 아니라 "① C-1 정책 확정 → …"으로
  시작해, 낡은 전제 위에 구현이 쌓이지 않도록 순서를 제시한다.
- 이 결과는 **자문(advice)**일 뿐 코드를 건드리지 않는다 — 피엠은 이 계획을 스프린트 티켓으로 쪼개면 된다.

---

## ✅ 피엠 여정 결과

**성공적으로 수행된 것**
1. 새 요구사항의 영향을 **11개 후보 · 3범주(Must/Likely/Review)**로 근거와 함께 파악.
2. 착수 전 **기존 충돌 6건을 경고**받아, 잘못된 전제(telephone 10) 위 구현을 예방.
3. **충돌 해소를 앞세운 8단계 Change Plan**으로 실행 순서를 확보.

**TRACE 부재 대비 이점**
- 계획: "감으로 영향 추정 → 낡은 명세 위 착수" → "근거 기반 영향 범위 + 착수 전 리스크 + 순서형 계획".
- 리스크: 숨어 있던 충돌(telephone 20/10, email·address 필수 부재)을 **착수 전에** 인지 → 재작업 방지.

> 피엠이 경고받은 `owner-registration` 충돌들은, **데브**가 온보딩에서 근거와 함께 이해한 그 지식,
> **마이라**가 조사에서 짚는 그 불일치와 **동일한 코어**에서 나온다. 세 페르소나가 같은 지식을 각자의
> 진입점에서 소비한다.

---

## 🔁 재현 방법

```bash
# (A) 실제 Claude(Amazon Bedrock) 라이브 — 위 화면을 생성한 방법
#     먼저 라이브 지식 생성:
python demo/tools/extract_features_live.py
#     이후 영향 분석(opus 1회 호출):
TRACE_PROJECT_ROOT=demo trace impact "Add SMS verification to Owner registration" --feature owner-registration

# (B) API 키 없이 결정적 재현 — 큐레이션된 3충돌·5단계 계획, 매 실행 동일
python demo/run_demo.py     # ④ analyze_task_impact 구간
```

- 결정적 모드의 동일 태스크 출력(착수 전 충돌 3건 + Must/Likely/Review + 5단계 Change Plan)은
  [`result/hero-demo-output.txt`](../../../result/hero-demo-output.txt) ④ 구간 참고.
- 페르소나 세 명 요약 여정은 [`result/usage-walkthrough.md`](../../../result/usage-walkthrough.md) 참고.

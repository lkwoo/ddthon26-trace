# UOW-00 데모 데이터셋 — 의도적 충돌 불변식 (business-rules)

**단계**: CONSTRUCTION / Functional Design (UOW-00)
**작성일**: 2026-09-09
**목적**: 데모 데이터셋이 **반드시 유지해야 하는 불변식**(어떤 값이 어디서 어긋나는지, 검출 기대치)을
동결한다. 이 규칙은 UOW-03(충돌 검출)의 골든 기대치이자, 데이터셋 변경 시 회귀 방지 기준이다.

> 이 데이터셋은 "일부러 어긋난" 픽스처다. 아래 불변식은 **버그가 아니라 의도**이며,
> 픽스처를 수정할 때 실수로 정합화(충돌 제거)되지 않도록 지킨다.

---

## 충돌 C-1 — Owner.telephone max_length (value_mismatch, P0) 〔P1 데브〕
**불변식 INV-C1**: 아래 4개 근거가 서로 다른 max_length를 주장하며, 그 값 집합은 고정이다.

| source | 파일 | 표현 | 값 |
|---|---|---|---|
| requirement | `requirements/owner-management-spec.pdf` | "전화번호는 국제 형식 지원을 위해 최대 20자" | **20** |
| api_spec | `openapi/petclinic-rest.yaml` | `telephone: {maxLength: 10}` | **10** |
| source_code | `src/.../owner/Owner.java` | `@Size(max = 10)` | **10** |
| db_schema | `db/schema.sql` | `telephone VARCHAR(10)` | **10** |

- **검출 기대**: `detect_conflicts`가 subject=`Owner.telephone`, predicate=`max_length`,
  type=`value_mismatch`, values=`{20,10,10,10}` 충돌 1건을 반환해야 한다.
- **해석 기대**: "요구(20)와 구현/스펙(10)이 불일치. 국제 전화번호 저장 시 데이터 잘림 위험."
- **금지**: 네 파일의 숫자를 서로 같게 만들지 말 것(충돌 소멸).

## 충돌 C-2 — Pet.birthDate 미래일자 검증 드리프트 (stale_knowledge) 〔P2 마이라〕
**불변식 INV-C2**: 지식/설계 노트는 검증을 "있다"고 기술하나, 코드에는 검증이 없다(드리프트).

| source | 파일 | 표현 | 값 |
|---|---|---|---|
| design_note | `requirements/maintenance-notes.md` | "Pet.birthDate 는 미래 일자를 거부하도록 검증된다" | **rejected(검증함)** |
| source_code | `src/.../pet/Pet.java` | birthDate 필드에 미래일자 제약 애너테이션 **없음** | **none(검증 없음)** |

- **검출 기대**: subject=`Pet.birthDate`, predicate=`future_date_validation`,
  type=`stale_knowledge`(문서-구현 드리프트) 충돌 1건.
- **해석 기대**: "문서는 검증을 전제하나 코드에 없음 → 미래 생일 데이터 유입 가능(재발 원인)."
- **P2 연결**: 마이라가 '왜 잘못된 데이터가 들어왔나'를 조사할 때 근본 원인 후보로 제시.
- **금지**: 코드에 검증을 추가하거나 노트에서 규칙을 삭제하지 말 것.

## 충돌 C-3 — Owner.email 신규 필수 정책 vs 부재 (policy_conflict) 〔P3 피엠〕
**불변식 INV-C3**: 신규 요구는 email을 필수로 규정하나, 스펙/구현/DB에는 email이 아예 없다.

| source | 파일 | 표현 | 값 |
|---|---|---|---|
| requirement | `requirements/owner-management-spec.pdf` | "모든 Owner 는 이메일 주소를 필수로 가진다(신규 정책)" | **required** |
| api_spec | `openapi/petclinic-rest.yaml` | Owner 스키마에 email 속성 **없음** | **absent** |
| source_code | `src/.../owner/Owner.java`, `OwnerDto.java` | email 필드 **없음** | **absent** |
| db_schema | `db/schema.sql` | owners 테이블 email 컬럼 **없음** | **absent** |

- **검출 기대**: subject=`Owner.email`, predicate=`required`(요구) ↔ `presence`(구현),
  type=`policy_conflict` 충돌 1건.
- **해석 기대**: "요구는 필수이나 어디에도 구현이 없음 → 신규 필드 추가가 엔티티·DTO·스키마·API·테스트로 파급."
- **P3 연결**: 피엠이 '이 정책을 도입하면 영향 범위?'를 물을 때 광범위 파급의 근거.
- **금지**: 스펙/코드/DB 어느 하나에도 email을 미리 추가하지 말 것(파급 시연 소멸).

---

## 데이터셋 무결성 규칙 (전역)
- **R1 결정성(Q5=A)**: 모든 파일은 정적. 타임스탬프/난수/절대경로/환경변수 값 금지.
- **R2 시크릿 금지**: `application.properties` 등에 실제 키·비밀번호 금지(플레이스홀더만).
- **R3 최소성(Q4=B)**: Owner(Hero)+Pet 인접까지만. 무관한 도메인(Vet/Visit 확장) 추가 금지.
- **R4 다양성**: requirement(pdf/md)·api_spec(yaml)·db_schema(sql)·source_code(java)·config·test
  자산 유형이 각 1개 이상 존재(파서 커버리지 시연).
- **R5 매니페스트 동기화**: `demo/README.md`의 충돌 3건 표는 위 INV-C1~C3과 항상 일치.

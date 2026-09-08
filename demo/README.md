# TRACE 데모 데이터셋 (UOW-00)

TRACE의 Hero 시나리오를 결정적으로 재현하기 위한 하이브리드 픽스처다 (Q6).

## 구성

| 경로 | 유형 | 역할 |
|---|---|---|
| `petclinic/src/main/java/.../owner/Owner.java` | source | Owner 엔티티 — `telephone @Size(max=10)` (구현 기준 **10**) |
| `petclinic/src/main/java/.../owner/OwnerRestController.java` | source | Owner 등록 REST 엔드포인트, **SMS 인증 없음** |
| `petclinic/src/main/resources/db/schema.sql` | sql | `telephone VARCHAR(10)` (**10**) |
| `petclinic/src/main/resources/openapi.yaml` | openapi | `telephone.maxLength: 10` (**10**) |
| `petclinic/src/test/.../OwnerRegistrationTests.java` | test | 전화번호 10자리 상한 검증 |
| `requirements/owner-registration-spec.pdf` | requirement(PDF) | 전화번호 **최대 20자리** 요구 + **SMS 인증 필수** 요구 |
| `replay/*.json` | (replay 픽스처) | API 키 없이 AI 단계 결정적 재현 (4종: identify_features·generate_knowledge·extract_claims·analyze_task) |

## 의도적 충돌 (value_mismatch, P0)

정규화 Claim **`Owner.telephone.max_length`** 에 서로 다른 값이 붙는다:

- `20` ← `requirements/owner-registration-spec.pdf` (요구사항)
- `10` ← `openapi.yaml`, `schema.sql`, `Owner.java` (명세·구현)

→ TRACE는 이를 **value_mismatch 충돌**로 검출하고, 각 값의 근거 소스를 인용한다. 이것이
"코드를 짜기 전에 충돌을 경고" 하는 Hero 시나리오의 핵심이다.

## Hero Task

> "Add SMS verification to Owner registration"

요구사항 PDF는 SMS 인증을 요구하지만 구현(Controller/테스트)에는 없다 → Task Impact 분석이
Must/Likely/Review 파일을 근거와 함께 제시하고, 전화번호 길이 충돌을 함께 경고한다.

## PDF 재생성 (선택)

`python demo/tools/gen_requirements_pdf.py` (dev 전용, `fpdf2` 필요). 생성된 `.pdf`는 커밋된다.

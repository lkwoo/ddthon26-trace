# Owner/Pet — Maintenance & Design Notes

> TRACE 데모 픽스처 — 합성 유지보수 지식 노트(실제 운영 문서 아님).
> 이 노트는 "문서에는 규칙이 있으나 코드에는 없는" **문서-구현 드리프트(stale knowledge)**를
> 의도적으로 담는다. (참조: 충돌 C-2)

## Pet 도메인 규칙 (as-designed)

- **PET-RULE-1 (birthDate 검증)**: `Pet.birthDate`는 **미래 일자를 거부하도록 검증된다.**
  등록/수정 시 오늘보다 이후의 생년월일은 허용되지 않는다. 과거 장애(미래 생일 유입으로 인한
  나이 계산 오류)의 재발 방지책으로 도입되었다.
- **PET-RULE-2**: `Pet.name`은 필수이며 소유자(Owner) 내에서 중복될 수 없다.
- **PET-RULE-3**: `Pet.type`은 사전 정의된 `PetType` 목록 중 하나여야 한다.

## Owner 도메인 규칙 (as-designed)

- **OWNER-RULE-1**: `Owner.firstName`, `Owner.lastName`은 필수.
- **OWNER-RULE-2**: `Owner.telephone`은 연락 가능한 번호여야 한다.

> ⚠️ 주의(데모 의도): 위 PET-RULE-1(미래일자 검증)은 이 노트에는 "검증된다"고 기술되어 있으나,
> 현재 `pet/Pet.java` 구현에는 해당 검증 애너테이션/로직이 존재하지 않는다(드리프트).
> TRACE는 이 노트(지식)와 코드(구현) 사이의 불일치를 충돌로 드러낸다.

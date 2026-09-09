# PetClinic — Maintenance & Design Notes

> TRACE 데모 픽스처 — 합성 유지보수 지식 노트(실제 운영 문서 아님).
> 이 노트는 "문서에는 규칙이 있으나 코드에는 없는" **문서-구현 드리프트(stale knowledge)**를
> 의도적으로 담는다. (참조: 충돌 C-2, C-6, C-9)

## Pet 도메인 규칙 (as-designed)

- **PET-RULE-1 (birthDate 검증)**: `Pet.birthDate`는 **미래 일자를 거부하도록 검증된다.**
  등록/수정 시 오늘보다 이후의 생년월일은 허용되지 않는다. 과거 장애(미래 생일 유입으로 인한
  나이 계산 오류)의 재발 방지책으로 도입되었다.
- **PET-RULE-2**: `Pet.name`은 필수이며 소유자(Owner) 내에서 중복될 수 없다.
- **PET-RULE-3**: `Pet.type`은 사전 정의된 `PetType` 목록 중 하나여야 한다.

## Owner 도메인 규칙 (as-designed)

- **OWNER-RULE-1**: `Owner.firstName`, `Owner.lastName`은 필수.
- **OWNER-RULE-2**: `Owner.telephone`은 연락 가능한 번호여야 한다.

## Visit(진료 방문) 도메인 규칙 (as-designed)

- **VISIT-RULE-1 (date 검증)**: `Visit.date`는 **과거 일자로의 예약을 거부하도록 검증된다.**
  이미 지난 날짜로 진료를 예약할 수 없으며, 등록 시 오늘 이전 일자는 반려된다.
  (지난 날짜로 오등록되어 통계가 왜곡된 사고 이후 도입된 규칙)
- **VISIT-RULE-2**: 하나의 `Pet`에 대해 같은 날짜의 방문은 하나만 허용된다.

## Billing(청구) 도메인 규칙 (as-designed)

- **BILLING-RULE-1 (세금 적용)**: 청구서 금액에는 **부가세가 기본으로 적용(enforced)된다.**
  별도 면세 처리를 하지 않는 한, 모든 청구서는 세금이 포함되어 계산되는 것이 기본 동작이다.

> ⚠️ 주의(데모 의도) — 아래는 버그가 아니라 시연을 위한 의도적 드리프트다.
> - PET-RULE-1(미래일자 검증)은 이 노트엔 "검증된다"고 적혀 있으나 `pet/Pet.java`에는 검증이 없다 (C-2).
> - VISIT-RULE-1(과거일자 예약 금지)은 이 노트엔 있으나 `visit/Visit.java`에는 검증이 없다 (C-6).
> - BILLING-RULE-1(세금 기본 적용)은 이 노트엔 "enforced"이나 `config/application.properties`의
>   `billing.tax.enforcement=disabled`로 기본 비활성이다 (C-9).
> TRACE는 이 노트(지식)와 코드/설정(구현) 사이의 불일치를 충돌로 드러낸다.

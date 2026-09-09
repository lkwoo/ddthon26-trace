# UOW-00 (데모 데이터셋) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (per-unit: UOW-00)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(3 충돌 C-1~C-3·자산↔모델 매핑·무결성 규칙) + NFR Requirements
(결정성/시크릿/라이선스 + PBT→데이터 무결성 테스트 이관, NFR Design SKIP)를 **실제 파일**로 전개한다.

> UOW-00은 픽스처 데이터 단위다. "Code Generation"의 산출물은 애플리케이션 로직이 아니라
> `demo/` 데이터 자산 + 이를 검증하는 무결성 테스트다. 각 파일은 domain-entities.md의 레이아웃과
> business-rules.md의 불변식(INV-C1~C3, R1~R5)을 정확히 구현해야 한다.

---

## 생성 대상 파일 (체크박스)

### A. 데모 자산 — `demo/`
- [ ] A1. `demo/README.md` — 매니페스트: 각 파일 용도, 출처/라이선스(Apache-2.0 발췌·개변), **의도적 충돌 3건 표**(INV-C1~C3와 동기화, R5)
- [ ] A2. `demo/requirements/owner-management-spec.pdf` — 합성 PDF 요구사항(P0 파서 대상). 내용: Owner telephone **최대 20자(국제형식)**, **email 필수(신규 정책)**. Q2=A 완성 바이너리 커밋
- [ ] A3. `demo/requirements/maintenance-notes.md` — 유지보수 지식 노트: "Pet.birthDate는 미래 일자를 거부하도록 검증된다"(코드와 드리프트 → C-2)
- [ ] A4. `demo/openapi/petclinic-rest.yaml` — Owner/Pet 경로. `telephone: maxLength 10`, **email 필드 없음**
- [ ] A5. `demo/db/schema.sql` — `owners(telephone VARCHAR(10), email 컬럼 없음)`, `pets`, `types`
- [ ] A6. `demo/src/main/java/org/springframework/samples/petclinic/owner/Owner.java` — `@Size(max=10) telephone`, email 필드 없음
- [ ] A7. `.../owner/OwnerRestController.java` + `.../owner/OwnerDto.java` — Owner CRUD, DTO(email 없음)
- [ ] A8. `.../pet/Pet.java` + `.../pet/PetType.java` — `birthDate` 필드, **미래일자 검증 애너테이션 없음**(C-2)
- [ ] A9. `demo/config/application.properties` — 로컬 설정, **시크릿 없음/더미값만**(R2)
- [ ] A10. `demo/tests/OwnerControllerTests.java` — telephone 최대 10자 가정 인코딩(드리프트 고착, C-1 근거 보강)

### B. 데이터셋 무결성 테스트 — `tests/` (PBT 대체, NFR §3)
- [ ] B1. `tests/test_demo_dataset_integrity.py`:
  - INV-C1: telephone max_length가 pdf=20, yaml/java/sql=10 로 어긋나 있음을 assert
  - INV-C2: maintenance-notes는 검증 언급, Pet.java에는 미래일자 검증 없음을 assert
  - INV-C3: pdf는 email 필수 언급, yaml/java/sql에는 email 부재를 assert
  - R1: 금지 패턴(타임스탬프/난수 흔적) 부재, R2: 시크릿 패턴 부재, R4: 자산 유형 6종 존재, R5: README 충돌표 존재

### C. 마무리
- [ ] C1. 로컬에서 `pytest tests/test_demo_dataset_integrity.py` 실행 → 전부 pass 확인, PDF 텍스트 추출 가능 확인
- [ ] C2. `aidlc-docs/construction/uow-00/code/code-summary.md` 작성(생성 파일 목록·불변식 매핑·실행 결과)
- [ ] C3. 계획 체크박스 전부 [x], 커밋

---

## 준수 사항
- **결정성(Q5=A/R1)**: 모든 파일 정적. PDF는 한 번 생성해 바이너리로 커밋(생성 스크립트는 리포에 두지 않음 — Q2=A).
- **시크릿(R2)**: application.properties는 `spring.datasource.password=CHANGuse-me` 같은 더미/플레이스홀더만.
- **라이선스(S6)**: README 상단에 spring-petclinic-rest(Apache-2.0) 출처·개변 고지.
- **범위(Q4=B/R3)**: Owner(Hero)+Pet만. Vet/Visit 등 무관 도메인 추가 금지.
- **PDF 파서 검증**: 생성한 .pdf가 UOW-01/UOW-0F 파서로 텍스트 추출 가능해야 함(C1에서 확인).

## 실행 순서 (Part 2)
A2(PDF) → A1,A3~A10 자산 → B1 무결성 테스트 → C1 실행/검증 → C2 요약 → C3 커밋

# UOW-00 (데모 데이터셋) — Code Generation 요약

**단계**: CONSTRUCTION / Code Generation (UOW-00) Part 2
**작성일**: 2026-09-09
**결과**: `pytest` 43 passed (기존 31 + UOW-00 무결성 12), Python 3.11.9(.venv)

## 생성 파일

### demo/ 데모 자산 (11개)
| 파일 | 자산 유형 | 담긴 충돌/의도 |
|---|---|---|
| `demo/README.md` | 매니페스트 | 출처·라이선스 고지 + 충돌 3건 Ground Truth 표 (R5) |
| `demo/requirements/owner-management-spec.pdf` | requirement(PDF, P0) | telephone ≤ 20자(C-1 요구측), email 필수 신규정책(C-3 요구측) |
| `demo/requirements/maintenance-notes.md` | design_note | Pet.birthDate 미래일자 검증 규칙(C-2 지식측) |
| `demo/openapi/petclinic-rest.yaml` | api_spec | telephone maxLength 10(C-1), email 없음(C-3) |
| `demo/db/schema.sql` | db_schema | telephone VARCHAR(10)(C-1), email 컬럼 없음(C-3) |
| `demo/src/.../owner/Owner.java` | source_code | @Size(max=10) telephone(C-1), email 없음(C-3) |
| `demo/src/.../owner/OwnerDto.java` | source_code | 동일(C-1/C-3) |
| `demo/src/.../owner/OwnerRestController.java` | source_code | Owner CRUD REST |
| `demo/src/.../owner/OwnerRepository.java` | source_code | 레포지토리 인터페이스 |
| `demo/src/.../pet/Pet.java` | source_code | birthDate 미래일자 검증 없음(C-2 코드측) |
| `demo/src/.../pet/PetType.java` | source_code | Pet 타입 |
| `demo/config/application.properties` | config | 더미 자격증명만(R2) |
| `demo/tests/OwnerControllerTests.java` | test | telephone 10자 가정 인코딩(C-1 드리프트 고착) |

### tests/ (PBT 대체 무결성 테스트)
- `tests/test_demo_dataset_integrity.py` — 12 테스트:
  - 존재/자산다양성(R4), C-1(telephone 20 vs 10, 4소스), C-2(노트 검증함 vs 코드 없음),
    C-3(요구 email 필수 vs 스펙/코드/DB 부재), R2(시크릿 플레이스홀더), R5(README 충돌표 동기화).

## 불변식 매핑 (business-rules INV-C1~C3)
- **INV-C1** ✅ pdf=20 / openapi=10 / java=10 / sql=10 (value_mismatch, P0)
- **INV-C2** ✅ maintenance-notes: 검증함 / Pet.java: 검증 애너테이션 없음 (stale_knowledge)
- **INV-C3** ✅ pdf: email 필수 / openapi·java·sql: email 선언 부재 (policy_conflict)

## 결정성/보안
- **PDF 결정성**: reportlab `invariant=1`로 생성 → 2회 생성 바이트 동일 확인(R1). 생성 스크립트는
  리포에 두지 않음(Q2=A, 완성 바이너리만 커밋).
- **시크릿**: application.properties 비밀번호=`CHANGE_ME_PLACEHOLDER`(R2).
- **라이선스**: README에 spring-petclinic-rest(Apache-2.0) 출처·개변 고지(S6).

## 의존성 변경
- `pyproject.toml [dev]` 에 `pypdf>=4.0` 추가 — 무결성 테스트의 PDF 텍스트 추출용(런타임 아님).
  PDF 파싱 라이브러리의 최종 선택은 UOW-01(스캐너/파서)에서 확정.

## 다음 단계로 넘기는 컨텍스트
- 이 데이터셋은 UOW-01(scan_project 대상), UOW-02(Feature="Owner Management"), UOW-03(충돌 3건),
  UOW-04(Task Impact), UOW-06(3 페르소나 walkthrough)의 고정 입력이다.
- Hero E2E 앵커 = C-1 telephone 경로.

# TRACE 데모 데이터셋 (UOW-00)

이 디렉터리는 TRACE가 분석하는 **합성 데모 프로젝트**다. "Owner 관리(Owner Management)" 기능을
중심으로, 요구사항·API 명세·DB 스키마·소스코드·테스트가 **의도적으로 서로 어긋나** 있어
TRACE의 충돌 검출과 영향 분석을 시연할 수 있다.

## 출처 및 라이선스
- 소스코드/스키마/OpenAPI 조각은 **spring-petclinic-rest**(Apache License 2.0)에서 발췌하여
  데모 목적에 맞게 **축약·개변**했다. 실제 배포용 산출물이 아니다.
- 요구사항 PDF·유지보수 노트는 데모용 **합성 문서**다.
- 실제 시크릿·개인정보는 포함하지 않는다(설정 파일의 자격증명은 더미 플레이스홀더).

## 구성

| 경로 | 자산 유형 | 용도 |
|---|---|---|
| `requirements/owner-management-spec.pdf` | requirement (PDF, P0 파서) | 기능 요구사항 — telephone ≤ 20자, email 필수(신규 정책) |
| `requirements/maintenance-notes.md` | design_note | 유지보수 지식 노트 — Pet.birthDate 미래일자 검증 규칙 |
| `openapi/petclinic-rest.yaml` | api_spec | Owner/Pet REST 명세 (telephone maxLength 10, email 없음) |
| `db/schema.sql` | db_schema | 테이블 정의 (telephone VARCHAR(10), email 컬럼 없음) |
| `src/main/java/.../owner/*.java` | source_code | Owner 엔티티/DTO/컨트롤러/레포지토리 |
| `src/main/java/.../pet/*.java` | source_code | Pet/PetType 엔티티 |
| `config/application.properties` | config | 로컬 설정 (더미 자격증명) |
| `tests/OwnerControllerTests.java` | test | telephone 10자 가정을 인코딩(드리프트 고착) |

## 의도적 충돌 3건 (Ground Truth)

> ⚠️ 아래는 **버그가 아니라 데모를 위한 의도**다. 픽스처를 수정할 때 실수로 정합화하지 말 것.
> (설계 근거: `aidlc-docs/construction/uow-00/functional-design/business-rules.md` INV-C1~C3)

| # | 유형 | 대상 · 술어 | 어긋난 값 | 대표 페르소나 |
|---|---|---|---|---|
| **C-1** | value_mismatch (P0) | `Owner.telephone` · max_length | 요구 **20** / OpenAPI **10** / 코드 **10** / DB **10** | P1 데브 |
| **C-2** | stale_knowledge | `Pet.birthDate` · future_date_validation | 노트 **검증함** / 코드 **검증 없음** | P2 마이라 |
| **C-3** | policy_conflict | `Owner.email` · required vs presence | 요구 **필수** / 스펙·코드·DB **부재** | P3 피엠 |

## 사용
TRACE MCP 서버(또는 폴백 CLI)에서 이 디렉터리를 대상으로 `analyze_project`를 호출하면,
"Owner Management" 기능이 식별되고 위 충돌 3건이 근거와 함께 드러난다.
데이터셋 무결성은 `tests/test_demo_dataset_integrity.py`가 검증한다.

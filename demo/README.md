# TRACE 데모 데이터셋 (UOW-00)

이 디렉터리는 TRACE가 분석하는 **합성 데모 프로젝트**다. spring-petclinic-rest 스타일의
5개 도메인(Owner/Pet/Vet/Visit/Billing, 약 48개 자산)에 걸쳐 요구사항·API 명세·DB 스키마·
소스코드·설정·테스트가 **의도적으로 서로 어긋나** 있어, 사람이 눈으로는 놓치기 쉬운
**문서-구현 불일치 9건**을 TRACE가 근거와 함께 드러내는 것을 시연한다.

## 출처 및 라이선스
- 소스코드/스키마/OpenAPI는 **spring-petclinic-rest**(Apache License 2.0) 스타일을 따라
  데모 목적으로 축약·개변·합성했다. 실제 배포용 산출물이 아니다.
- 요구사항 PDF(4종)·유지보수 노트는 데모용 **합성 문서**다.
  PDF는 `tools/generate_specs.py`로 결정적으로 재생성할 수 있다(reportlab 필요, 개발용).
- 실제 시크릿·개인정보는 포함하지 않는다(설정 파일의 자격증명은 더미 플레이스홀더).

## 구성 (요약)

| 경로 | 자산 유형 | 도메인 |
|---|---|---|
| `requirements/owner-management-spec.pdf` | pdf (P0 파서) | Owner (telephone ≤ 20, email 필수, address 필수) |
| `requirements/vet-directory-spec.pdf` | pdf | Vet (수의사당 최소 1개 specialty 필수) |
| `requirements/visit-scheduling-spec.pdf` | pdf | Visit (description ≤ 255자, 과거일자 금지) |
| `requirements/billing-spec.pdf` | pdf | Billing (금액 DECIMAL(10,2), 세금 기본 적용) |
| `requirements/maintenance-notes.md` | markdown | 드리프트 지식 노트 (PET/VISIT/BILLING 규칙) |
| `openapi/petclinic-rest.yaml` | openapi | Owner/Pet/Vet/Visit REST 명세 |
| `db/schema.sql` | sql | 전 도메인 테이블 정의 |
| `config/application.properties` | config | 로컬 설정 + `billing.tax.enforcement=disabled` |
| `src/main/java/.../{owner,pet,vet,visit,billing,model}/*.java` | source | 엔티티/DTO/레포/컨트롤러/서비스/매퍼 |
| `tests/*Tests.java` | test | 컨트롤러/서비스 테스트 |

## 의도적 충돌 9건 (Ground Truth)

> ⚠️ 아래는 **버그가 아니라 데모를 위한 의도**다. 픽스처를 수정할 때 실수로 정합화하지 말 것.
> (설계 근거: `aidlc-docs/construction/uow-00/functional-design/business-rules.md` INV-C1~C3,
>  회귀 방지: `tests/test_demo_dataset_integrity.py`)

| # | 유형 | 대상 · 술어 | 어긋난 값 | Feature |
|---|---|---|---|---|
| **C-1** | value_mismatch | `owner.telephone` · max_length | 요구 **20** / OpenAPI·코드·DB **10** | owner-registration |
| **C-2** | stale_knowledge | `pet.birthDate` · future_date_validation | 노트 **검증함(rejected)** / 코드 **검증 없음(accepted)** | pet-management |
| **C-3** | policy_conflict | `owner.email` · required | 요구 **필수** / 스펙·코드·DB **부재** | owner-registration |
| **C-4** | value_mismatch | `visit.description` · max_length | 명세 **255** / OpenAPI·코드·DB **8192** | visit-scheduling |
| **C-5** | policy_conflict | `vet.specialties` · min_one_required | 명세 **필수(≥1)** / 코드 **미강제(부재)** | vet-directory |
| **C-6** | stale_knowledge | `visit.date` · past_date_validation | 노트 **거부(rejected)** / 코드 **허용(accepted)** | visit-scheduling |
| **C-7** | value_mismatch | `invoice.amount` · precision | 명세 **DECIMAL(10,2)** / 코드·DB **DECIMAL(8,2)** | billing-invoicing |
| **C-8** | policy_conflict | `owner.address` · required | 요구 **필수** / 코드 **선택(부재)** | owner-registration |
| **C-9** | stale_knowledge | `billing.tax` · enforcement_default | 노트 **적용(enforced)** / 설정 **비활성(disabled)** | clinic-configuration |

유형 분포: value_mismatch 3 · policy_conflict 3 · stale_knowledge 3.

## 사용

### 결정적 데모 (API 키 불필요)
```bash
python demo/run_demo.py
```
스캔 → 6 Feature 식별 → 9충돌 검출(근거 포함) → "Add SMS verification to Owner registration"
영향 분석까지 매번 동일하게 재현한다.

### 실제 Claude 자동 검출 (선택)
```bash
python demo/run_demo.py --live   # anthropic 설치 + ANTHROPIC_API_KEY 필요, 결과는 비결정적
```

### 스펙 PDF 재생성 (선택, 개발용)
```bash
.venv/Scripts/python.exe demo/tools/generate_specs.py
```

데이터셋 무결성은 `tests/test_demo_dataset_integrity.py`가 검증한다(9충돌이 실수로 소멸되지 않도록).

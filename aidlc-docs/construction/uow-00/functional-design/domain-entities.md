# UOW-00 데모 데이터셋 — 자산 ↔ 도메인 모델 매핑 (domain-entities)

**단계**: CONSTRUCTION / Functional Design (UOW-00)
**작성일**: 2026-09-09
**결정 반영**: Q1=C(충돌 3건), Q2=A(.pdf 커밋), Q3=A(Hero=Owner 관리), Q4=B(Owner+Pet 발췌), Q5=A(완전 고정)

> UOW-00은 코드가 아니라 **픽스처 데이터**다. 도메인 엔티티(Feature/Claim/Evidence/Confidence/
> Conflict/FeatureKnowledge)는 UOW-0F에서 이미 동결됐다. 이 문서는 **데모 자산 파일들이
> 그 동결 모델의 어느 필드를 채우는지**를 매핑한다. (모델 정의 자체는 UOW-0F 산출물 참조)

---

## 1. 데이터셋 디렉터리 레이아웃 (S1)

```text
demo/
├── README.md                          # 매니페스트: 각 파일이 무엇을 위한 픽스처인지 + 의도적 충돌 3건 명시
├── requirements/
│   ├── owner-management-spec.pdf       # 합성 PDF 요구사항 (P0 파서 검증) — telephone≤20, email 필수(신규 정책)
│   └── maintenance-notes.md            # 유지보수 지식 노트 — Pet birthDate 검증 규칙(코드와 드리프트)
├── openapi/
│   └── petclinic-rest.yaml             # Owner/Pet 경로. telephone maxLength:10, email 필드 없음
├── db/
│   └── schema.sql                      # owners(telephone VARCHAR(10), email 컬럼 없음), pets, types
├── src/main/java/org/springframework/samples/petclinic/
│   ├── owner/
│   │   ├── Owner.java                   # @Size(max=10) telephone, email 필드 없음
│   │   ├── OwnerRestController.java     # Owner CRUD REST
│   │   └── OwnerDto.java                # DTO (email 없음)
│   └── pet/
│       ├── Pet.java                     # birthDate 필드, 미래일자 검증 없음(드리프트)
│       └── PetType.java
├── config/
│   └── application.properties           # 로컬 설정(시크릿 없음)
└── tests/
    └── OwnerControllerTests.java        # telephone 최대 10자 가정을 인코딩(드리프트 고착)
```

- **라이선스(S6)**: Petclinic 발췌 조각은 원 프로젝트(spring-petclinic-rest, Apache-2.0) 파생.
  `demo/README.md` 상단에 출처·라이선스·"발췌·개변됨"을 명시한다. 시크릿·개인정보 없음.
- **결정성(Q5=A)**: 모든 파일은 정적 텍스트/바이너리. 타임스탬프·난수·환경의존 값 없음.
  → 동일 입력 재실행 시 스캔·파싱 결과가 동일(캐시/재현성 검증 기반).

---

## 2. 자산 → 동결 모델 필드 매핑

### 2.1 Feature (Hero)
| 자산 근거 | Feature 필드 |
|---|---|
| owner-management-spec.pdf, Owner*.java, OpenAPI Owner 경로, schema.sql owners | `Feature.name` = "Owner Management" |
| 위 자산 집합 | `Feature.evidence_sources` = [pdf, java, yaml, sql, tests] (다중 자산 유형 → 파서 커버리지 시연) |

### 2.2 Claim ↔ Evidence (subject / predicate / value)
동일 predicate에 대해 **서로 다른 source가 다른 value**를 주장 → Conflict의 재료.

| Claim (subject·predicate) | Evidence.source | Evidence.type | extracted_value |
|---|---|---|---|
| Owner.telephone · max_length | requirements/owner-management-spec.pdf | requirement | **20** |
| Owner.telephone · max_length | openapi/petclinic-rest.yaml | api_spec | **10** |
| Owner.telephone · max_length | src/.../owner/Owner.java (`@Size(max=10)`) | source_code | **10** |
| Owner.telephone · max_length | db/schema.sql (`VARCHAR(10)`) | db_schema | **10** |
| Owner.email · required | requirements/owner-management-spec.pdf | requirement | **true(필수)** |
| Owner.email · presence | openapi/petclinic-rest.yaml | api_spec | **absent(필드 없음)** |
| Owner.email · presence | src/.../owner/Owner.java | source_code | **absent** |
| Pet.birthDate · future_date_validation | requirements/maintenance-notes.md | design_note | **rejected(검증함)** |
| Pet.birthDate · future_date_validation | src/.../pet/Pet.java | source_code | **none(검증 없음)** |

### 2.3 Confidence 기대치
- telephone: 4개 source 중 3개가 `10`으로 수렴, PDF 요구만 `20` → 다수 근거 존재, **Confidence=HIGH**(충돌 자체는 명확).
- email: 요구는 명시적, 구현/스펙은 부재 → 근거 비대칭, **Confidence=MEDIUM**.
- Pet.birthDate: 지식 노트 vs 코드 1:1 → **Confidence=MEDIUM**(드리프트 후보).

### 2.4 Conflict (3건 — Q1=C, 상세 불변식은 business-rules.md)
| # | type | subject·predicate | values | 대표 페르소나 |
|---|---|---|---|---|
| C-1 | `value_mismatch` (P0) | Owner.telephone · max_length | {20, 10, 10, 10} | **P1 데브** |
| C-2 | `stale_knowledge` (드리프트) | Pet.birthDate · future_date_validation | {지식노트:검증함, 코드:없음} | **P2 마이라** |
| C-3 | `policy_conflict` (신규 정책 부재) | Owner.email · required vs presence | {요구:필수, 구현/스펙:부재} | **P3 피엠** |

### 2.5 FeatureKnowledge (저장 뷰)
- `.trace/knowledge/features/owner-management.md` 로 저장될 지식 뷰의 **입력 근거**가 위 Claim/Evidence.
- UOW-02가 이 데이터를 소비해 지식 뷰를 생성, UOW-03이 Conflict를 검출, UOW-04가 Impact를 산출.

---

## 3. 다운스트림 소비 계약(요약)
- **UOW-01 스캔/파서**: `demo/` 전체를 자산으로 분류·파싱. PDF·YAML·SQL·Java·properties 모두 커버.
- **UOW-02**: Feature="Owner Management"(Hero) + 인접 Pet Feature 식별, 지식 뷰 저장.
- **UOW-03**: 위 3개 Conflict 검출(P0 value_mismatch C-1 필수).
- **UOW-04**: Hero Task(예: "전화번호 국제형식 20자 지원")에서 3범주 영향 + 충돌 경고.
- **UOW-06**: 세 페르소나 walkthrough의 실제 입력.

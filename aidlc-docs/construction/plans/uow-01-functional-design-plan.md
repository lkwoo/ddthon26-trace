# UOW-01 (스캐너 & 파서) — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (per-unit: UOW-01)
**작성일**: 2026-09-09
**앞 단계 반영**:
- UOW-0F에서 동결한 `Result` envelope·`config.get_exclusions()`·공통 오류/로깅을 소비한다.
- UOW-00 `demo/`가 실제 스캔 대상. 이 단위의 출력(assets)이 UOW-02(Feature 식별)의 입력.
- 요구사항: FR-PROJECT-001/002/003, FR-ANALYSIS-003, NFR-SEC-004. component-methods `scan_project(path)->Result`.

> UOW-01의 책임: 로컬 경로를 안전하게 스캔하여 자산을 분류하고(소스/MD/텍스트/PDF/OpenAPI/SQL/설정/테스트),
> 각 자산의 텍스트 내용을 추출하며, 제외 규칙·경로 검증·부분 실패 허용을 구현한다. **구조적 의미 해석은
> 하지 않는다**(그것은 UOW-02/03 AI 단계의 몫). 즉 "스캔 + 텍스트화 + 분류"까지가 경계.

---

## 계획 스텝 (체크박스)
- [x] S1. `Asset` 도메인 모델 정의(path, rel_path, filename, asset_type, parse_status, content, size, truncated, error)
- [x] S2. `AssetType` 분류 taxonomy(EvidenceType 정렬) 및 분류 규칙(확장자 + 내용 판별) 정의
- [x] S3. 파서 전략 — 유형별 텍스트 추출 방식(PDF=pypdf/YAML=PyYAML/나머지 텍스트) 정의
- [x] S4. 경로 검증 규칙(NFR-SEC-004: 존재·디렉터리·심볼릭/트래버설 안전) 정의 — BR-PATH
- [x] S5. 제외 규칙 적용(FR-PROJECT-003, C7 `get_exclusions()` 소비) 및 바이너리·대용량 처리 — BR-EXCLUDE/BR-SIZE
- [x] S6. 부분 실패 허용 흐름(FR-ANALYSIS-003) — BR-FAIL
- [x] S7. `scan_project(path)->Result` 데이터 계약 확정(Q5=A: 메타만, 내부 scan_project_assets는 content 포함)
- [x] S8. business-logic-model / business-rules / domain-entities 산출물 작성

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. 파서 라이브러리 — PDF/YAML 등 어떤 라이브러리로 텍스트를 추출할까?
- **A. PDF=pypdf(이미 dev 의존성), YAML/JSON=PyYAML(이미 런타임 의존성)+표준 json, SQL/소스/설정/MD/텍스트=순수 텍스트 읽기** (권장) — 신규 의존성 최소, 결정적, 순수 파이썬
- **B. PDF=pdfplumber(레이아웃 정밀)**, 나머지 A와 동일 — 추출 품질↑, 무거운 의존성 추가
- **C. 기타(직접 지정)**

[Answer]: A

### Q2. 자산의 "파싱" 깊이 — UOW-01은 어디까지 구조화하나?
- **A. 텍스트 추출까지만**(각 Asset에 정규화된 text 보관). SQL/소스/OpenAPI의 구조 해석은 UOW-02/03 LLM에 위임 (권장) — 단위 경계 명확, 결정적, 파서 부담 최소
- **B. OpenAPI/SQL은 경량 구조 파싱까지**(예: OpenAPI 경로·스키마 dict, SQL 테이블/컬럼 추출) — 후속 AI 그라운딩 정밀↑, 파서 복잡도·유지보수 부담↑
- **C. 혼합(직접 지정)**

[Answer]: A

### Q3. 자산 유형 분류 기준 — 특히 OpenAPI vs 일반 설정 YAML 구분
- **A. 확장자 1차 분류 + 내용 판별 보정**(YAML/JSON 안에 `openapi:`/`swagger:` 키 있으면 api_spec, 아니면 config; `*Test*`·`test_*`·`/test/` 경로면 test) (권장) — 실용적·결정적
- **B. 확장자만으로 분류** — 단순하나 OpenAPI/테스트 오분류 가능
- **C. 기타(직접 지정)**

[Answer]: A

### Q4. 자산 내용을 언제 메모리에 적재하나(성능/메모리)?
- **A. 스캔 시 즉시 텍스트 적재(eager) + 파일당 최대 크기 상한**(초과 시 truncate + warning) (권장) — 데모/로컬 규모에 단순·충분, 결정적
- **B. 지연 로딩(lazy) — 경로만 들고 있다가 필요 시 읽기** — 대규모 대응, 상태관리 복잡

[Answer]: A

### Q5. `scan_project`가 반환하는 Asset 필드에 전체 text를 포함할까, 요약만 포함할까?
- **A. Result.data.assets에는 메타(path/type/status/size)만, 전체 text는 엔진 내부 오케스트레이션이 보유**(MCP 응답 비대화 방지, NFR-MCP-UX) (권장)
- **B. data.assets에 text까지 포함** — 단순하나 MCP 응답이 커짐

[Answer]: A

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-01/functional-design/business-logic-model.md` — 스캔→분류→파싱→부분실패 알고리즘·데이터 흐름
- `aidlc-docs/construction/uow-01/functional-design/business-rules.md` — 경로검증·제외·분류·크기상한·실패허용 규칙
- `aidlc-docs/construction/uow-01/functional-design/domain-entities.md` — Asset/AssetType/ParseStatus 모델 + scan_project 데이터 계약

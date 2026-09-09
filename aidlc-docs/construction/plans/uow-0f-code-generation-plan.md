# UOW-0F Foundation — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (Part 1 — Planning)
**단위**: UOW-0F (Foundation, enabler)
**작성일**: 2026-09-09
**프로젝트 유형**: Greenfield, 단일 패키지(monolith) → 코드는 **워크스페이스 루트**의 `trace/`·`tests/`.
**전제 설계**: functional-design(domain-entities/business-logic-model/business-rules) · nfr-requirements · nfr-design(P1~P8, logical-components).

> 이 계획이 Code Generation의 **단일 진실원**이다. Part 2는 아래 단계를 순서대로만 실행한다.
> UOW-0F는 이후 전 단위가 임포트하는 계약을 **동작하는 코드**로 고정한다.

---

## 단위 컨텍스트

- **구현 스토리**: 직접 대응 없음(enabler). 뒷받침: US-02.3/03.1/03.2(모델·직렬화), US-06.4(시크릿).
- **의존**: 없음(leaf). 이후 UOW-01~06이 이 단위를 임포트.
- **제공 계약(공개 인터페이스)**: `trace.models`(도메인·Result), `trace.models.serialize`, `trace.common`(errors·warnings·logging), `trace.config`, `trace.prompts`, `trace.llm`.
- **활성 확장**: Resiliency Baseline·PBT(Blocking) → 오류 계층·부분실패·Hypothesis 속성 테스트 포함.

## 코드 위치 (워크스페이스 루트, aidlc-docs 아님)

```text
ddthon26-trace/
├── pyproject.toml                 # 신규(0F가 최초 선언): 의존성·진입점·빌드
├── trace/
│   ├── __init__.py
│   ├── models/{__init__,domain,result,serialize}.py
│   ├── common/{__init__,errors,warnings,logging}.py
│   ├── config/{__init__,settings}.py
│   ├── prompts/{__init__,loader}.py
│   │   └── templates/            # (빈 디렉터리+.gitkeep; 내용은 02/03/04)
│   └── llm/{__init__,client,service}.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py               # FakeLLMClient 등 픽스처
│   ├── test_models_serialize.py  # PBT round-trip·결정성
│   ├── test_domain_rules.py      # slug·정규화·검증·충돌 성립
│   ├── test_result_warnings.py   # Result 조립·WarningCollector
│   ├── test_config_settings.py   # env-only·미설정 ConfigError
│   ├── test_prompts_loader.py    # 렌더·미존재 ConfigError
│   └── test_llm_service.py       # 제약교정 재시도·검증실패(Fake client)
├── .env.example                  # ANTHROPIC_API_KEY 등(값 없음)
└── .gitignore                    # .env, .trace/, __pycache__ 등
```

---

## 생성 단계 (순차)

### Step 1 — 프로젝트 구조·빌드 셋업 (Greenfield)
- [x] `pyproject.toml`: PEP 621 메타·의존성(`mcp, anthropic, pydantic>=2, PyYAML`)·dev(`pytest, hypothesis`)·진입점(`trace-mcp`, `trace`; 대상 모듈은 후속 단위, 0F는 선언만 or 주석 placeholder)·Python 3.11+.
- [x] `.gitignore`, `.env.example`(키 이름만), 패키지 `__init__.py`들, `prompts/templates/.gitkeep`.
- *NFR*: 빌드 재현성(락파일은 Build&Test에서 생성), SEC-1(.env.example 값 없음).

### Step 2 — 공통: 오류·로깅·Warning (common/)  [Business Logic]
- [x] `common/errors.py`: `TraceError` + `ConfigError/PathValidationError/ParseError/LLMValidationError/StorageError` + `error_to_result(e)->Result` 헬퍼(P3).
- [x] `common/warnings.py`: `WarningCollector`(P4).
- [x] `common/logging.py`: 로거 설정 + `log_stage` 컨텍스트매니저(P5), 값/원문 마스킹.
- *스토리/규칙*: BR-ERR-*, BR-WARN-*, NFR-0F-REL-1/2·OBS-1·SEC-3.

### Step 3 — 도메인 모델 (models/domain.py)  [Business Logic]
- [x] Pydantic 모델: enums(Confidence/EvidenceRelation/EvidenceType/ConflictType/ImpactCategory), `Feature/Claim/Evidence/ConfidenceAssessment/ClaimConfidence/Conflict/ConflictValue/FeatureKnowledge`.
- [x] 필드 검증(BR-VAL-*), `make_feature_id(title)` slug 생성(BR-ID-*), 값 정규화 헬퍼(BR-NORM-*).
- *스토리*: US-02.3/03.1/03.2. *NFR*: MNT-1.

### Step 4 — Result & 출력 DTO (models/result.py)  [Business Logic]
- [x] `Result, Warning, ConflictOut, EvidenceRef, ImpactItem, ImpactOut, FeatureSummary`.
- [x] `build_result(...)` 조립 규칙(충돌 상위 노출·warnings 합본, business-logic-model §1).
- *NFR*: REL-2·OBS-2·MCP-UX(핵심 우선).

### Step 5 — 직렬화 (models/serialize.py)  [Business Logic]
- [x] `serialize(fk)->str`(YAML Front Matter sort_keys + 리스트 정렬 + Markdown 본문 렌더), `deserialize(text)->FeatureKnowledge`(safe_load, Front Matter만; P6/P8).
- *NFR*: DET-1·SEC-4·TST-2. *규칙*: BR-DET-002, BR-VAL-005.

### Step 6 — 설정 (config/settings.py)  [Business Logic]
- [x] `Config, LLMSettings`, `load_config(path)`, `get_exclusions()`, `get_llm_settings()`(키 이름만, late lookup P7). 기본값(temperature=0, max_retries=2, knowledge_dir=.trace/knowledge).
- *NFR*: SEC-1·DET-2. *규칙*: BR-SEC-*, BR-DET-001.

### Step 7 — 프롬프트 로더 (prompts/loader.py)  [Business Logic]
- [x] `get_prompt(name, **vars)->str`(templates/ 로드+렌더, 미존재/미해결변수 → ConfigError). 템플릿 내용은 후속 단위.
- *NFR*: MNT-2.

### Step 8 — LLM 클라이언트·서비스 (llm/)  [Business Logic / 주입 경계]
- [x] `llm/client.py`: `LLMClient` Protocol + `AnthropicClient`(생성자 주입, 호출 직전 env 키 조회; 실제 SDK 호출은 최소 구현/명시적 경계 — Build&Test 전 네트워크 불필요, P1/P7).
- [x] `llm/service.py`: `LLMService.complete_structured(prompt, schema)` — 결정성 파라미터·Pydantic 검증·제약교정 재시도 max_retries·실패 시 LLMValidationError(P1/P2).
- *NFR*: REL-3·TST-1·SEC-1.

### Step 9 — 테스트 (tests/) — 단위 + PBT  [Unit Testing]
- [x] `conftest.py`: `FakeLLMClient`(스크립트 응답), 샘플 FeatureKnowledge 팩토리.
- [x] `test_models_serialize.py`: Hypothesis `deserialize(serialize(x))==x`, serialize 결정성.
- [x] `test_domain_rules.py`: slug 멱등·정규화 멱등·필수필드 검증·Conflict(값≥2) 성립.
- [x] `test_result_warnings.py`: build_result 충돌 상위·WarningCollector 취합.
- [x] `test_config_settings.py`: 키 미설정 ConfigError·값 비저장.
- [x] `test_prompts_loader.py`: 렌더·미존재 ConfigError.
- [x] `test_llm_service.py`: 첫 응답 스키마 위반→교정 재시도 성공, 소진→LLMValidationError (FakeLLMClient).
- *NFR*: TST-1/2(PBT), REL-3.

### Step 10 — 코드 요약 문서 (문서 only)
- [x] `aidlc-docs/construction/uow-0f/code/code-summary.md`: 생성 파일 목록·공개 계약·테스트 커버리지 매핑·하위 단위 임포트 가이드. (markdown 요약만, 코드는 루트)

---

## 실행/검증 메모
- 테스트 실제 실행·락파일 생성은 **Build & Test** 단계(전 단위 완료 후). 여기선 코드·테스트 파일 생성까지.
- 시크릿 커밋 금지: `.env`는 .gitignore, `.env.example`만 커밋.

## 승인
[Answer]: (예: "승인" 또는 변경요청)

---
**총 10 스텝.** 승인 시 Part 2에서 Step 1→10 순차 실행하며 각 스텝 완료 즉시 체크박스 갱신.

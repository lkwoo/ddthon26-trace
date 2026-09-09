# UOW-03 (Claims/Evidence/Conflict) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (UOW-03)
**작성일**: 2026-09-09
**입력**: functional-design(BR-CLAIM/EVID/CONF/CONFLICT/OUT/PIPE/DET/SEC), nfr-design(P1~P10), logical-components
**앞 단계 반영**: 비-LLM 결정적 코어(구조적 충돌비교) + Feature별 격리 강등 + 캐시-완본 스테이지 + PBT-03-A~D.
**기존 계약 소비**: `Conflict/Claim/Evidence/ClaimConfidence/claim_key/normalize_value`(domain), `build_result/ConflictOut/FeatureSummary`(result),
`build_knowledge/generate_feature_knowledge`(workflow/features), `LLMService.complete_structured`, `KnowledgeStore`, `scan_project_assets`(engine).

---

## 생성/수정 파일 (logical-components 청사진)

### 코드
- [x] C1. `trace/models/domain.py` **[수정]** — `ConflictType`에 `STALE_KNOWLEDGE`, `POLICY_CONFLICT` 추가(하위 호환).
- [x] C2. `trace/models/extraction.py` **[신설]** — `ExtractedClaim{subject,predicate,evidence}`, `ClaimExtractionResult{claims}`.
- [x] C3. `trace/conflict/__init__.py` **[신설]** — 패키지 초기화.
- [x] C4. `trace/conflict/detect.py` **[신설]** — `ABSENCE_TOKENS`(상수), `detect_conflicts(claims, feature_id)`(결정적 순수),
      `classify_conflict_type(ec, vals)`(전결정성, 순서규칙+value_mismatch 폴백), `_looks_behavioral`/`_has_doc_vs_code`/`_render_interpretation` 내부.
- [x] C5. `trace/conflict/summarize.py` **[신설]** — `summarize_conflicts(conflicts) -> list[ConflictOut]`.
- [x] C6. `trace/workflow/claims.py` **[신설]** — `extract_claims(feature, assets, llm)`(Feature당 1회, 허구근거 드롭+warning),
      `assign_confidence(ec)`(비-LLM 규칙), `enrich_feature_knowledge(fk_shell, assets, llm)`(대표값 Claim/평탄 Evidence/meta.stage="complete").
- [x] C7. `trace/engine/analyze.py` **[신설]** — `analyze_project(path)`(스캔→build_knowledge→셸 완본화→충돌 집계→cache.put→build_result),
      `get_conflicts(feature_id=None)`(로드→summarize→meta.conflicts_count), `_build_llm_service()`(AnthropicClient 조립).
- [x] C8. `trace/engine/__init__.py` **[수정]** — `analyze_project`, `get_conflicts` export 추가.
- [x] C9. `trace/prompts/templates/extract_claims.md` **[신설]** — `${feature_title}/${feature_description}/${sources}`, "원자 Claim 분해·유효 JSON만" 명시.

### 테스트 (PBT/단위/통합)
- [x] T1. `tests/test_conflict_detect.py` — demo 3충돌 손수 픽스처(C-1 value_mismatch/C-2 stale_knowledge/C-3 policy_conflict) 유형 정확, distinct<2 → 0건.
- [x] T2. `tests/test_confidence.py` — assign_confidence 경계(LOW: contradicts/≥2값, HIGH: supports≥2·일치, MEDIUM: 그 외), reason 존재.
- [x] T3. `tests/test_conflict_properties.py` — PBT-03-A(건전성)·B(결정성/멱등·evidence 셔플)·C(전결정성·예외없음)·D(Confidence 정합). hypothesis derandomize.
- [x] T4. `tests/test_analyze_project.py` — FakeLLM 주입: 스캔→지식→완본화→충돌 반환, 부분실패 격리, 2회차 캐시-완본 스테이지 재사용(LLM 미호출 카운트).
- [x] T5. `tests/test_llm_integration.py` **[수정]** — `@pytest.mark.llm_integration` analyze_project 실 API 통합 1건 추가(env+키 없으면 skip).

### DoD 검증
- [x] V1. `pytest -q` 전체 green(기존 90 pass 유지 + 신규), `llm_integration`는 skip.
- [x] V2. 신규 모듈 mypy-clean(기존 방침 유지).
- [x] V3. `analyze_project("demo")` FakeLLM 시나리오에서 3충돌·유형 정확 재현(수기 픽스처 기반 결정성).
- [x] V4. code-summary.md 작성.

---

## 핵심 알고리즘 (functional-design 반영 요약)

**detect_conflicts** (C4, 결정적): 각 `ExtractedClaim`의 evidence에서 `normalize_value(extracted_value)` distinct 수집.
`< 2` → 스킵. `≥ 2` → `classify_conflict_type` 후 `Conflict(type, claim=claim_key, values[≥2], interpretation)` 1건. `claim` 순 정렬.

**classify_conflict_type** (C4, 순서 규칙): ①부재토큰 ∩ 요구값 → `POLICY_CONFLICT` ②행위서술 ∧ 문서vs코드 → `STALE_KNOWLEDGE` ③그 외 → `VALUE_MISMATCH`(폴백). 예외 없이 유효값 하나.

**assign_confidence** (C6, 비-LLM): `has_contradiction`(contradicts>0 or distinct≥2)→LOW; `supports≥2 ∧ distinct≤1`→HIGH; else MEDIUM. reason 한 줄.

**analyze_project** (C7): `validate→scan_project_assets→build_knowledge(cache-first)` → 각 Feature `stage!="complete"`면 `enrich`(try/except 격리) → `store.save` → 전체 conflicts 집계 → `cache.put` → `build_result(data={features,assets_count,conflicts_count}, conflicts=all)`.

---

## 결정/제약
- 신규 런타임 의존성 없음. `conflict/detect`는 표준 라이브러리·모델만(순수 → PBT).
- 로그/warning은 rel_path·claim_key·feature_id·code만(원문·시크릿·절대경로 금지).
- 대표 Claim.value = evidence 중 최다 supports 값; 동률/부재 시 정규화 사전순 첫 값(domain-entities §3).

## Part 2 (승인 후 실행)
위 C1~C9 + T1~T5 생성 → V1~V4 검증 → `aidlc-docs/construction/uow-03/code/code-summary.md` 작성.

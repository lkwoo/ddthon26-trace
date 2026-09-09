# UOW-02 (Feature & Knowledge) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (per-unit: UOW-02)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-IDF/KN/STORE/CACHE/FAIL/DET/SEC) + NFR Requirements(발췌 4000·무제한·
PBT 4속성·llm_integration 옵트인) + NFR Design(P1~P9, logical-components)를 실제 코드로 구현.
소비: UOW-01 `scan_project_assets`, UOW-0F `LLMService`/`get_prompt`/`serialize`/도메인 모델/`config`.

---

## 생성/수정 대상 (체크박스)

### A. 모델
- [x] A1. `trace/models/feature_candidate.py` — `FeatureCandidate`·`FeatureCandidateList`·`KnowledgeBody`

### B. 지식 계층 (knowledge/, C4)
- [x] B1. `trace/knowledge/__init__.py`
- [x] B2. `trace/knowledge/ids.py` — `safe_feature_id()`·`dedupe_ids` (P3)
- [x] B3. `trace/knowledge/store.py` — `KnowledgeStore` (P4)
- [x] B4. `trace/knowledge/cache.py` — `compute_assets_hash`·`CacheEntry`·`AnalysisCache`(손상=미스, P5)

### C. 워크플로 (workflow/, C3)
- [x] C1. `trace/workflow/__init__.py`
- [x] C2. `trace/workflow/catalog.py` — `build_catalog`(발췌 4000)·`render_catalog` (P1)
- [x] C3. `trace/workflow/features.py` — `identify_features`·`generate_feature_knowledge`·`build_knowledge` (P2/P6)

### D. 프롬프트 (prompts/templates/, C8)
- [x] D1. `identify_features.md`
- [x] D2. `feature_knowledge.md`

### E. 테스트
- [x] E1. `tests/test_knowledge_store.py`
- [x] E2. `tests/test_analysis_cache.py`
- [x] E3. `tests/test_features_workflow.py` (캐시 히트 LLM 미호출·부분실패 격리·폴백)
- [x] E4. `tests/test_features_properties.py` — PBT-02-A/B/C/D
- [x] E5. `tests/test_llm_integration.py` — 옵트인(기본 skip)

### F. 의존성 & 마무리
- [x] F1. `pyproject.toml` — `llm_integration` 마커 등록
- [x] F2. `pytest` 90 passed, 1 skipped(70+20+옵트인1), 신규 모듈 mypy-clean
- [x] F3. `code-summary.md` 작성
- [x] F4. 계획 체크박스 전부 [x], 커밋

---

## 준수 사항
- **경계(Q2=A)**: 식별+지식 셸+캐시까지. claims/evidence/conflicts는 빈 채로 저장(UOW-03 보강).
- **부분실패(BR-FAIL)**: identify/지식 LLM 실패는 warning 강등, 예외 상위 전파 금지.
- **결정성**: 정렬된 카탈로그·콘텐츠 해시(순서 무관)·저장 멱등.
- **보안**: 발췌 상한·로그/warning 위생·저장 루트 하위·키 late-lookup.
- **오프라인 테스트 기본**: FakeLLMClient(UOW-0F conftest) 재사용. 실 API는 옵트인 마커만.
- **타입**: mypy(disallow_untyped_defs) 통과.

## 실행 순서 (Part 2)
A1→B2(ids)→B4(cache)→B3(store)→C2(catalog)→D1·D2(프롬프트)→C3(features)→E1~E5→F1→F2(pytest)→F3→F4

# UOW-02 (Feature & Knowledge) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (per-unit: UOW-02)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-IDF/KN/STORE/CACHE/FAIL/DET/SEC) + NFR Requirements(발췌 4000·무제한·
PBT 4속성·llm_integration 옵트인) + NFR Design(P1~P9, logical-components)를 실제 코드로 구현.
소비: UOW-01 `scan_project_assets`, UOW-0F `LLMService`/`get_prompt`/`serialize`/도메인 모델/`config`.

---

## 생성/수정 대상 (체크박스)

### A. 모델
- [ ] A1. `trace/models/feature_candidate.py` — `FeatureCandidate`·`FeatureCandidateList`·`KnowledgeBody`

### B. 지식 계층 (knowledge/, C4)
- [ ] B1. `trace/knowledge/__init__.py`
- [ ] B2. `trace/knowledge/ids.py` — `safe_feature_id()` (P3, 항상 안전)
- [ ] B3. `trace/knowledge/store.py` — `KnowledgeStore`(save/load/list_feature_summaries/read_resource, P4)
- [ ] B4. `trace/knowledge/cache.py` — `compute_assets_hash`·`CacheEntry`·`AnalysisCache`(손상=미스, P5)

### C. 워크플로 (workflow/, C3)
- [ ] C1. `trace/workflow/__init__.py`
- [ ] C2. `trace/workflow/catalog.py` — `build_catalog`(발췌 4000)·`render_catalog` (P1)
- [ ] C3. `trace/workflow/features.py` — `identify_features`·`generate_feature_knowledge`·`build_knowledge` (P2/P6, 부분실패 강등)

### D. 프롬프트 (prompts/templates/, C8)
- [ ] D1. `identify_features.md` — 카탈로그→FeatureCandidateList JSON 지시(유효 JSON만)
- [ ] D2. `feature_knowledge.md` — Feature 개요 본문→KnowledgeBody JSON

### E. 테스트
- [ ] E1. `tests/test_knowledge_store.py` — save/load round-trip·list(손상 skip)·read_resource·경로 루트 하위
- [ ] E2. `tests/test_analysis_cache.py` — 히트 시 LLM 미호출(호출 카운트)·내용 변경 미스·손상=미스
- [ ] E3. `tests/test_features_workflow.py` — FakeLLM 주입: 식별→지식셸→저장, 부분실패 강등, 본문 폴백
- [ ] E4. `tests/test_features_properties.py` — PBT-02-A/B/C/D (hypothesis, derandomize)
- [ ] E5. `tests/test_llm_integration.py` — 옵트인: `@pytest.mark.llm_integration`, env+키 없으면 skip

### F. 의존성 & 마무리
- [ ] F1. `pyproject.toml` — `[tool.pytest.ini_options].markers` 에 `llm_integration` 추가
- [ ] F2. 로컬 `pytest` 전체 실행 → 전부 pass(기존 70 + UOW-02 신규), 신규 모듈 mypy-clean
- [ ] F3. `aidlc-docs/construction/uow-02/code/code-summary.md` 작성
- [ ] F4. 계획 체크박스 전부 [x], 커밋

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

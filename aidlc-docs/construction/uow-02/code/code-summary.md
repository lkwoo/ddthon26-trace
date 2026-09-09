# UOW-02 (Feature & Knowledge) — Code Generation 요약

**단계**: CONSTRUCTION / Code Generation (UOW-02) Part 2
**작성일**: 2026-09-09
**결과**: `pytest` **90 passed, 1 skipped**(옵트인 llm_integration), 기존 70 + UOW-02 20+1. 신규 모듈 mypy-clean.

## 생성/수정 파일
### 애플리케이션 코드
| 파일 | 내용 |
|---|---|
| `trace/models/feature_candidate.py` | FeatureCandidate·FeatureCandidateList·KnowledgeBody(LLM 구조화 출력) |
| `trace/knowledge/ids.py` | safe_feature_id(항상 안전, PBT-02-A)·dedupe_ids |
| `trace/knowledge/cache.py` | compute_assets_hash(순서무관·내용민감)·CacheEntry·AnalysisCache(손상=미스) |
| `trace/knowledge/store.py` | KnowledgeStore(save/load/list_feature_summaries/read_resource, serialize/deserialize, 루트 하위 강제) |
| `trace/workflow/catalog.py` | build_catalog(발췌 4000·content 있는 자산만)·render_catalog |
| `trace/workflow/features.py` | identify_features·generate_feature_knowledge(셸·폴백)·build_knowledge(cache-first·격리) |
| `trace/prompts/templates/identify_features.md` | 카탈로그→FeatureCandidateList JSON |
| `trace/prompts/templates/feature_knowledge.md` | 개요 본문→KnowledgeBody JSON |
| `pyproject.toml` | pytest marker `llm_integration` 등록 |

### 테스트 (20 + 옵트인 1)
| 파일 | 내용 |
|---|---|
| `tests/test_knowledge_store.py` | save/load round-trip·list 손상 skip·read_resource·경로 루트 하위·오류 |
| `tests/test_analysis_cache.py` | 해시 순서무관·내용민감·put/get·손상=미스 |
| `tests/test_features_workflow.py` | FakeLLM: 식별·정렬·부분실패 강등·본문 폴백·캐시 히트(LLM 미호출)·Feature별 격리 |
| `tests/test_features_properties.py` | PBT-02-A(id 안전)·B(해시)·C(발췌 상한)·D(저장 round-trip) |
| `tests/test_llm_integration.py` | 옵트인: env+키일 때만 실 API(기본 skip) |

## FakeLLM 실증 (스모크)
- demo/ 스캔 자산 → identify(1콜)→지식 셸 저장(1콜) = 2콜, `owner-management` 저장.
- 2회차 동일 자산 → **캐시 히트, LLM 0콜**, 동일 요약 반환(NFR-PERF-003).
- read_resource("trace://feature/owner-management") 본문 반환.

## NFR/규칙 이행
- **Q2=A 경계**: 지식 셸만(claims/evidence/conflicts=[]) — UOW-03 보강. generate_feature_knowledge는
  claims/evidence/confidence/conflicts 인자를 받아 UOW-03이 동일 함수로 완본화 가능.
- **BR-FAIL**: identify 실패→빈 목록+warning; Feature별 지식 실패 격리; 본문 실패→템플릿 폴백.
- **BR-CACHE(Q4=A)**: 콘텐츠 해시 키, 손상=미스 재분석.
- **BR-SEC**: 발췌 상한·로그 위생·저장 루트 하위·키 late-lookup.
- **PBT 확장(전면)**: 4속성 구현. **재현성/테스트(Q3=B)**: 기본 오프라인 FakeLLM + 옵트인 실 API 마커.

## 다음 단계 컨텍스트
- UOW-03(Claims/Evidence/Conflict)은 build_knowledge/generate_feature_knowledge를 확장:
  extract_claims·group_evidence·assign_confidence·detect_conflicts를 채워 FeatureKnowledge 완본화 후 재저장.
- analyze_project(전체 파이프라인) 완성은 UOW-03/04 이후(현재 build_knowledge가 前반부 재사용 단위).

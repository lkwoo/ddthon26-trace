# UOW-02 (Feature & Knowledge) — NFR Design Patterns

**단계**: CONSTRUCTION / NFR Design (UOW-02)
**작성일**: 2026-09-09
**입력**: nfr-requirements(COST/PERF/REL/SEC/TST/PBT), functional-design(BR-IDF/KN/STORE/CACHE/FAIL/DET/SEC)
**참고**: 추가 질문 없음 — 패턴이 앞 단계 결정에서 일의적으로 도출됨.

---

## P1. 자산 카탈로그 빌더 (NFR-02-COST-1, BR-IDF-002)
- **패턴**: *Projection + Truncation*. `build_catalog(assets)` → content 있는 자산만(parsed/partial),
  각 항목 `{rel_path, asset_type, excerpt=content[:4000] 정규화}`. rel_path 정렬(결정성).
- 렌더: 사람이 읽는 구획 텍스트(경로/유형/발췌 구분자)로 프롬프트에 삽입.

## P2. 구조화 LLM step + 단계 강등 (NFR-02-REL-1/2/3, BR-FAIL)
- **패턴**: *Structured call with graceful degradation*. `llm.complete_structured(prompt, Schema)`(UOW-0F)로
  검증·재시도. `LLMValidationError`는 **해당 step에서 포착**해 빈 결과/폴백 + `Warning`으로 강등(상위 미전파).
- 스키마: `FeatureCandidateList`(식별), `KnowledgeBody{markdown}`(지식 본문).

## P3. id 안전화 (PBT-02-A, BR-IDF-004)
- **패턴**: *Sanitize/slugify*. `safe_feature_id(candidate_id | title)`:
  소문자화 → 공백/구분자→`-` → `[a-z0-9-]` 외 제거 → 연속/양끝 `-` 정리 → 빈 값이면 `feature-<n>`.
  결과는 항상 `/\..` 없는 비어있지 않은 문자열(Feature.id 검증 통과 보장).

## P4. 지식 저장소 (NFR-02-SEC-3, BR-STORE)
- **패턴**: *Repository over serialize/deserialize*. `KnowledgeStore(project_root)`:
  경로 `<root>/.trace/knowledge/features/<id>.md`, 저장 전 `id` 안전성 + 루트 하위 보장(트래버설 금지).
  `save`=serialize+write, `load`=read+deserialize(손상→StorageError),
  `list_feature_summaries`=glob+load(손상 파일 skip+warning, 목록은 계속 — BR-STORE-003), 정렬 반환.
- `read_resource("trace://feature/<id>")` → body_markdown.

## P5. 콘텐츠 해시 캐시 (NFR-02-PERF, BR-CACHE, Q4=A)
- **패턴**: *Content-addressed cache*. `compute_assets_hash(assets)` =
  sha256("\n".join(sorted(f"{rel_path}:{size}:{sha256(content or '')}")))  → 순서 무관·내용 민감(PBT-02-B).
- `AnalysisCache(project_root)`: `<root>/.trace/cache/<hash>.json`. `get`은 파싱/스키마 실패 시 **None(미스)**
  반환(조용한 폴백, Q4=A) + debug 로그. `put`은 CacheEntry(model_dump→json).

## P6. 오케스트레이션 build_knowledge (NFR-02-PERF-1, BR-FAIL/CACHE)
- **패턴**: *Cache-first + per-item isolation*.
  1) hash 계산 → cache.get 히트면 store.list_feature_summaries()만 반환(LLM 미호출).
  2) 미스면 identify → 각 Feature try/except 격리 저장 → cache.put.
- warnings 누적, 예외는 밖으로 던지지 않음(어댑터가 Result로).

## P7. 프롬프트 템플릿 (NFR-02-MAINT-1, C8)
- `prompts/templates/identify_features.md`, `feature_knowledge.md`. `${catalog}`,`${max_features}`,
  `${title}`,`${description}`,`${sources}` 변수. `get_prompt`의 StrictTemplate(미해결 변수→ConfigError).
- 프롬프트는 "유효 JSON만 출력"을 명시(complete_structured의 _extract_json과 정합).

## P8. 테스트 배치 (NFR-02-TST, PBT)
| 파일 | 내용 |
|---|---|
| `tests/test_features_workflow.py` | FakeLLM 주입 — 식별→지식셸→저장, 부분실패 강등, 폴백 |
| `tests/test_knowledge_store.py` | save/load round-trip, list(손상 skip), read_resource, id 안전 경로 |
| `tests/test_analysis_cache.py` | 히트 시 LLM 미호출(호출 카운트), 콘텐츠 변경 시 미스, 손상=미스 |
| `tests/test_features_properties.py` | PBT-02-A/B/C/D (hypothesis, derandomize) |
| `tests/test_llm_integration.py` | Q3=B 옵트인: `@pytest.mark.llm_integration`, env+키 없으면 skip |
- pyproject `[tool.pytest.ini_options] markers = ["llm_integration: 실제 Anthropic API 호출(옵트인)"]`.

## P9. 결정성/보안
- LLM 결정성은 settings(temp=0)만. 프롬프트는 정렬된 카탈로그로 동일 입력→동일 프롬프트.
- 로그/warning은 rel_path·feature_id·code만(원문·시크릿 금지). API 키 late-lookup(UOW-0F).

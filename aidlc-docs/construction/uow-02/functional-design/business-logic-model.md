# UOW-02 (Feature & Knowledge) — 비즈니스 로직 모델 (business-logic-model)

**단계**: CONSTRUCTION / Functional Design (UOW-02)
**작성일**: 2026-09-09

> AI 파이프라인 前반부: 스캔된 자산에서 Feature를 자동 식별하고, 각 Feature의 지식 뷰 셸을 생성해
> `.trace`에 저장하며, 콘텐츠 해시 캐시로 재실행을 가속한다. Claim/Evidence/Conflict는 UOW-03이 보강.

---

## 1. 컴포넌트 배치
```text
trace/
├── models/
│   └── feature_candidate.py    # [신설] FeatureCandidate, FeatureCandidateList
├── workflow/                   # [신설 패키지] C3 AI step
│   ├── __init__.py
│   ├── catalog.py              # 자산 카탈로그 빌드(Q3=A) + 발췌 상한
│   └── features.py             # identify_features, generate_feature_knowledge
├── knowledge/                  # [신설 패키지] C4 저장소·캐시
│   ├── __init__.py
│   ├── store.py                # KnowledgeStore (save/load/list/read_resource)
│   └── cache.py                # compute_assets_hash, AnalysisCache
└── prompts/templates/
    ├── identify_features.md    # [신설] C8 프롬프트(내용)
    └── feature_knowledge.md    # [신설] C8 프롬프트(내용)
```
- 소비: UOW-01 `scan_project_assets`, UOW-0F `LLMService`/`get_prompt`/`serialize`/도메인 모델/`config`.

## 2. 식별 흐름 — identify_features(assets, llm, max_features)
```text
1. catalog = build_catalog(assets)             # content 있는 자산만, 발췌 상한(BR-IDF-002)
      각 항목: {rel_path, asset_type, excerpt}
2. prompt = get_prompt("identify_features", catalog=render(catalog), max_features=N)
3. try:
       out = llm.complete_structured(prompt, FeatureCandidateList)   # 구조화·검증·재시도(UOW-0F)
   except LLMValidationError:
       return [], [Warning("identify_failed", ...)]                  # BR-FAIL-002
4. candidates = normalize(out.features)         # id 안전화·중복제거·정렬·상한 (BR-IDF-003/004/005)
5. return candidates, warnings
```

## 3. 지식 셸 생성 — generate_feature_knowledge(candidate, assets, llm)
```text
1. feature = Feature(id, title, description, related_sources=candidate.related_sources)
2. related = [a for a in assets if a.rel_path in candidate.related_sources]
3. prompt = get_prompt("feature_knowledge", title=..., description=..., sources=render(related catalog))
4. try:  body = llm.complete_structured(prompt, KnowledgeBody).markdown
   except LLMValidationError:  body = fallback_body(feature); warn("knowledge_fallback", feature.id)
5. return FeatureKnowledge(feature=feature, claims=[], evidence=[], confidence=[], conflicts=[],
                           body_markdown=body, meta={model, sources, stage:"knowledge-shell"})
```
- (KnowledgeBody = {markdown: str} 구조화 봉투. 실패 시 템플릿 폴백으로 저장 계속 — BR-KN-002.)

## 4. 오케스트레이션(부분) — analyze 파이프라인의 UOW-02 구간
```text
def build_knowledge(assets, llm, store, cache) -> (list[FeatureSummary], warnings):
    h = compute_assets_hash(assets)
    hit = cache.get(h)
    if hit:                                   # BR-CACHE-002
        return store.list_feature_summaries(), []      # 저장된 지식 재사용(LLM 호출 없음)
    candidates, w1 = identify_features(assets, llm, max_features=N)
    warnings = list(w1)
    saved_ids = []
    for c in candidates:                      # 각 Feature 독립 — 실패 격리(BR-FAIL-001)
        try:
            fk = generate_feature_knowledge(c, assets, llm)
            store.save_feature(fk)
            saved_ids.append(fk.feature.id)
        except Exception as e:
            warnings.append(Warning("knowledge_failed", sanitize(e), source=c.id))
    cache.put(CacheEntry(assets_hash=h, feature_ids=saved_ids))
    return store.list_feature_summaries(), warnings
```
- 이 `build_knowledge`는 UOW-02가 제공하는 재사용 단위. `analyze_project`(전체) 완성은 UOW-03/04 이후.
- 공개 코어 `list_features()`는 `store.list_feature_summaries()`를 Result로 감싼다(UOW-05가 노출).

## 5. 데모(UOW-00) 기준 기대 동작
- `demo/` 자산에서 **Owner Management**(Hero) Feature가 식별되고(관련: pdf/openapi/sql/Owner*.java/tests),
  인접 **Pet** Feature가 나올 수 있음. 각 Feature 지식 셸이 `.trace/knowledge/features/<id>.md`로 저장.
- 재실행 시 자산 불변이면 캐시 히트 → LLM 재호출 없이 동일 목록 반환(NFR-PERF-003).

## 6. 완료조건 (DoD)
- [ ] identify_features가 demo에서 ≥1 Hero Feature(자동) 식별.
- [ ] generate_feature_knowledge가 지식 셸(body_markdown) 생성, save_feature로 저장.
- [ ] list_feature_summaries/read_resource로 조회 가능.
- [ ] 콘텐츠 해시 캐시: 2회차 실행 시 히트(LLM 미호출) — 테스트로 검증(FakeLLM 호출 카운트).
- [ ] LLM 단계 실패가 전체를 막지 않음(부분 warning) — 테스트로 검증.
- [ ] 결정적: 동일 자산·동일 FakeLLM 응답 → 동일 저장 결과.

## 7. 테스트 전략(코드 단계 예고)
- FakeLLMClient(UOW-0F conftest)로 결정적 응답 주입 → 네트워크 없이 검증.
- 캐시 히트/미스, 부분 실패 격리, 저장·로드 round-trip, read_resource, id 안전화.
- PBT(전면): id 안전화 함수(임의 title→항상 안전 id), 캐시 해시 안정성(순서 무관 동일) 등 후속 NFR에서 확정.

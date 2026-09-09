# UOW-03 (Claims/Evidence/Conflict) — 비즈니스 로직 모델 (business-logic-model)

**단계**: CONSTRUCTION / Functional Design (UOW-03)
**작성일**: 2026-09-09

> AI 파이프라인 後반부 + 전체 파이프라인 완성(Q5=A). UOW-02 지식 셸을 원자 Claim·Evidence·근거일치
> Confidence·충돌(3유형)로 완본화한다. **충돌 존재는 결정적 구조 비교**(RAG 차별점의 코드적 입증).

---

## 1. 컴포넌트 배치
```text
trace/
├── models/
│   ├── domain.py          # [수정] ConflictType += STALE_KNOWLEDGE, POLICY_CONFLICT
│   └── extraction.py      # [신설] ExtractedClaim, ClaimExtractionResult
├── workflow/
│   └── claims.py          # [신설] extract_claims, assign_confidence, enrich_feature_knowledge
├── conflict/              # [신설] C5
│   ├── __init__.py
│   ├── detect.py          # detect_conflicts(결정적), classify_conflict_type
│   └── summarize.py       # summarize_conflicts
├── engine/
│   └── analyze.py         # [신설] analyze_project, get_conflicts (코어 공개)
└── prompts/templates/
    └── extract_claims.md  # [신설] C8
```

## 2. 추출 흐름 — extract_claims(feature, assets, llm)
```text
1. related = [a for a in assets if a.rel_path in feature.related_sources]
2. prompt = get_prompt("extract_claims", feature=..., sources=render_catalog(build_catalog(related)))
3. try: result = llm.complete_structured(prompt, ClaimExtractionResult)
   except TraceError: return [], [Warning("extract_failed", source=feature.id)]   # BR-PIPE-002
4. drop evidence whose source ∉ related rel_paths (BR-EVID-004, +warning)
5. return result.claims, warnings
```

## 3. Confidence — assign_confidence(ec)  (비-LLM, BR-CONF)
```text
values = { normalize_value(e.extracted_value) for e in ec.evidence if e.extracted_value }
supports = count(relation==supports); contradicts = count(relation==contradicts)
has_contradiction = contradicts>0 or len(values)>=2
level = LOW if has_contradiction
        else HIGH if (supports>=2 and len(values)<=1)
        else MEDIUM
reason = f"근거 {len(ec.evidence)}건, 상이값 {len(values)}개, contradicts {contradicts}건"
return ClaimConfidence(claim_key(ec.subject,ec.predicate), ConfidenceAssessment(level, reason))
```

## 4. 충돌 검출 — detect_conflicts(claims, feature_id)  (결정적, BR-CONFLICT)
```text
conflicts = []
for ec in claims:
    vals = distinct_by(normalize_value, [(e.extracted_value, e.source, e.location)
                                          for e in ec.evidence if e.extracted_value])
    if len(vals) < 2: continue                      # 충돌 아님
    ctype = classify_conflict_type(ec, vals)         # BR-CONFLICT-003 순서 규칙
    conflicts.append(Conflict(type=ctype, claim=claim_key(ec.subject,ec.predicate),
                              values=[ConflictValue(v,src,loc) for v,src,loc in vals],
                              interpretation=render_interpretation(ec, ctype, vals)))
sort by claim; return conflicts

classify_conflict_type(ec, vals):
    norm = {normalize_value(v) for v,_,_ in vals}
    if norm & ABSENCE_TOKENS and (norm - ABSENCE_TOKENS):     # 부재 vs 요구
        return POLICY_CONFLICT
    if looks_behavioral(ec.predicate, norm) and has_doc_vs_code(ec.evidence):
        return STALE_KNOWLEDGE
    return VALUE_MISMATCH
```
- `ABSENCE_TOKENS = {absent,none,missing,n/a,null,없음,부재}`
- `looks_behavioral`: predicate/값이 검증·규칙·행위 계열(validated/rejected/enforced/검증 등).
- `has_doc_vs_code`: evidence에 문서(pdf/markdown)와 코드/DB/openapi가 모두 있고 상충.

## 5. 완본화 — enrich_feature_knowledge & analyze_project (Q5=A, BR-PIPE)
```text
def enrich(fk_shell, assets, llm) -> (FeatureKnowledge, warnings):
    claims_ex, w = extract_claims(fk_shell.feature, assets, llm)
    confidence = [assign_confidence(ec) for ec in claims_ex]
    conflicts = detect_conflicts(claims_ex, fk_shell.feature.id)
    claims = [to_claim(ec, feature_id) for ec in claims_ex]     # 대표값 산정
    evidence = flatten(ec.evidence for ec in claims_ex)
    fk = fk_shell.copy(update={claims, evidence, confidence, conflicts,
                               meta:{...,'stage':'complete'}})
    return fk, w

def analyze_project(path) -> Result:
    root = validate; assets,wscan = scan_project_assets(path)
    summaries, wk = build_knowledge(assets, llm, store, cache)   # UOW-02 셸 (캐시 히트 시 재사용)
    warnings = wscan+wk; all_conflicts=[]
    for fid in [s.id for s in summaries]:
        fk = store.load_feature(fid)
        if fk.meta.get("stage") != "complete":                  # 셸이면 완본화
            try:
                fk, we = enrich(fk, assets, llm); store.save_feature(fk); warnings += we
            except Exception as e: warnings.append(Warning("enrich_failed", source=fid))
        all_conflicts += summarize(fk.conflicts)
    cache.put(...updated)
    return build_result(summary, data={features, assets_count, conflicts_count},
                        conflicts=all_conflicts, warnings=warnings)

def get_conflicts(feature_id=None) -> Result:
    fks = [store.load_feature(feature_id)] if feature_id else store.list all
    conflicts = [ConflictOut ...]; return build_result(summary, conflicts=conflicts,
                 meta={conflicts_count})
```
- 캐시 완본 스테이지: `meta.stage=="complete"` 이면 재분석 생략(LLM 미호출) — BR-PIPE-003.

## 6. 데모(UOW-00) 기대 — 3충돌 (Ground Truth 대조)
| 충돌 | claim_key | 값(근거) | 검출 유형 |
|---|---|---|---|
| C-1 | owner.telephone.max_length | 20(pdf) / 10(openapi,code,db) | value_mismatch (P0) |
| C-2 | pet.birthdate.future_date_validation | rejected(design_note) / none(code) | stale_knowledge |
| C-3 | owner.email.required(presence) | required(pdf) / absent(openapi,code,db) | policy_conflict |
- `analyze_project("demo")`가 3충돌을 모두 반환, `get_conflicts`가 상세(값·소스·해석) 제공.

## 7. DoD
- [ ] 원자 Claim·Evidence·Confidence(근거 일치도) 생성.
- [ ] detect_conflicts가 데모 3충돌 검출(유형 정확), 결정적(2회 동일).
- [ ] analyze_project 전체 파이프라인 통과(스캔→지식→충돌→저장), 캐시 재사용.
- [ ] get_conflicts 상세 반환(FR-CONFLICT-OUT). 부분 실패 격리.
- [ ] FakeLLM 오프라인 테스트 + detect_conflicts 순수함수 단위/PBT.

## 8. 테스트 전략
- detect_conflicts/classify/assign_confidence는 **순수 함수** → FakeLLM 없이도 결정적 단위·PBT 가능.
- 추출/파이프라인은 FakeLLM 주입. 데모 3충돌은 손으로 만든 ExtractedClaim 픽스처로도 검증(결정성).

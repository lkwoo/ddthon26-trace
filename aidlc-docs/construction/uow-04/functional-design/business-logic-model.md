# UOW-04 (Task Impact Analysis) — 비즈니스 로직 모델 (business-logic-model)

**단계**: CONSTRUCTION / Functional Design (UOW-04)
**작성일**: 2026-09-09

> 저장된 지식(UOW-02 셸 + UOW-03 완본)을 컨텍스트로 자연어 작업의 영향을 분석한다.
> **지식 그라운딩**이 일반 LLM 대비 차별점 — 근거 참조·기존 충돌 경고가 결과에 박힌다.

---

## 1. 컴포넌트 배치
```text
trace/
├── models/
│   └── impact.py          # [신설] ImpactCandidate, TaskImpactResult (LLM 중간 스키마)
├── impact/                # [신설] C6
│   ├── __init__.py
│   ├── context.py         # build_context, KnowledgeContext, 관련도 랭킹
│   └── analyze.py         # analyze_task(LLM step), to_impact_out(매핑·강등·정렬)
├── engine/
│   └── analyze.py         # [수정] analyze_task_impact 추가(코어 공개)
└── prompts/templates/
    └── analyze_task.md    # [신설] C8
```

## 2. 컨텍스트 조립 — build_context(task, feature_id, store)  (Q1/Q2/Q3=A, BR-CTX)
```text
summaries = store.list_feature_summaries()
if feature_id: focus_ids = [feature_id]
else:          focus_ids = rank_by_relevance(task, summaries)[:N]   # 제목·소스 토큰 겹침
focus = [store.load_feature(fid) for fid in focus_ids (로드 실패 skip+warning)]
conflicts = flatten(fk.conflicts for fk in focus)                    # Q3=A
known_sources = ∪(fk.feature.related_sources ∪ {e.source for e in fk.evidence} for fk in focus)
return KnowledgeContext(task, summaries, focus, conflicts, known_sources)
```
- `rank_by_relevance`: 작업 텍스트를 소문자 토큰화 → 각 FeatureSummary(title+related_sources) 토큰과 교집합 크기 내림차순,
  동률 시 id 사전순(결정적). 지식이 없으면 focus=[] (BR-PIPE-003).

## 3. LLM step — analyze_task(ctx, llm)  (FR-IMPACT-002, BR-IMP)
```text
prompt = get_prompt("analyze_task",
    task=ctx.task,
    features=render_summaries(ctx.features),
    knowledge=render_focus(ctx.focus),        # 본문·claims·evidence(발췌)·기존 conflicts
    known_sources=render_sources(ctx.known_sources))
try: return llm.complete_structured(prompt, TaskImpactResult)
except TraceError: raise  # 상위 analyze_task_impact가 warning 강등(BR-PIPE-002)
```
- 프롬프트는 "제공된 known_sources 안에서만 path 지목, 근거(evidence) 참조, 근거 없으면 review·Insufficient evidence,
  유효 JSON만 출력"을 명시.

## 4. 매핑 — to_impact_out(result, ctx)  (BR-IMP-003/004/005, BR-CONFWARN)
```text
buckets = {MUST_CHANGE:[], LIKELY_CHANGE:[], REVIEW:[]}
for c in result.candidates:
    cat = c.category
    if c.path not in ctx.known_sources:            # 허구 path → review 강등(BR-IMP-004)
        cat = REVIEW; c.reason = f"[근거 밖 추정] {c.reason}"
    if not c.evidence:                              # 근거 부족(BR-IMP-005)
        cat = REVIEW
        if "Insufficient" not in c.reason: c.reason += " (Insufficient evidence)"
    buckets[cat].append(ImpactItem(path=c.path, reason=c.reason, evidence=c.evidence))
for k in buckets: buckets[k].sort(key=lambda it: it.path)      # 결정적 정렬
related = summarize_conflicts(ctx.conflicts)                    # Q3=A, P1
return ImpactOut(must_change=..., likely_change=..., review=...,
                 related_conflicts=related, change_plan=result.change_plan)
```

## 5. 조립 — analyze_task_impact(task, feature_id=None, path=".")  (BR-PIPE)
```text
store = KnowledgeStore(path)
ctx = build_context(task, feature_id, store)
warnings = []
if not ctx.focus:                                  # 지식 없음(BR-PIPE-003)
    return build_result("분석할 지식이 없습니다. 먼저 analyze_project를 실행하세요.",
                        warnings=[Warning("no_knowledge", ...)])
try:
    result = analyze_task(ctx, llm)
    impact = to_impact_out(result, ctx)
except TraceError:                                 # LLM 실패 강등(BR-PIPE-002)
    warnings.append(Warning("task_analysis_failed", ...))
    impact = ImpactOut(related_conflicts=summarize_conflicts(ctx.conflicts))   # 충돌은 그래도 노출
low = any(not it.evidence for bucket in (impact.must_change, impact.likely_change, impact.review) for it in bucket)
return build_result(summary, data={feature_scope, candidates_count},
                    impact=impact, conflicts=impact.related_conflicts, warnings=warnings,
                    meta={"confidence": "LOW" if low else "MEDIUM"})
```
- **소스 자동수정 없음**: 파일 쓰기 호출 없음(BR-PLAN-002).

## 6. Hero Task 기대 (데모 대조, US-04.3)
- Task: "Add SMS verification to Owner registration"
- feature_id=owner-management → related_conflicts 에 **telephone max_length 충돌(20 vs 10)** 노출(구현 권고 전 경고).
- must_change: Owner 검증/DTO; likely_change: OpenAPI/스키마; review: 테스트·문서. change_plan은 충돌 해소를 1순위.

## 7. DoD
- [ ] analyze_task_impact가 지식·근거를 컨텍스트로 사용(일반 프롬프트 단독 아님).
- [ ] 3범주 분류 + 각 이유·근거 참조. 근거 부족 → review + LOW.
- [ ] related_conflicts로 기존 충돌 경고(P1), 구현 권고 전 상단 노출.
- [ ] 순서형 Change Plan(충돌 해소 우선), 소스 자동수정 없음.
- [ ] LLM 실패·지식 부재 강등(예외 전파 없음). 허구 path review 강등.
- [ ] FakeLLM 오프라인 테스트 + to_impact_out/build_context 결정적 단위.

## 8. 테스트 전략
- `build_context`·`to_impact_out`·`rank_by_relevance`는 **순수/준순수** → FakeLLM 없이 결정적 단위(정렬·강등·화이트리스트).
- `analyze_task_impact`는 FakeLLM 주입(오프라인). Hero Task는 저장 지식 픽스처 + Fake 응답으로 충돌 경고·3범주 검증.

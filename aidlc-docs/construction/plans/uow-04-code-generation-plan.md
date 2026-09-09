# UOW-04 (Task Impact Analysis) — Code Generation 계획 (Part 1)

**단계**: CONSTRUCTION / Code Generation (UOW-04)
**작성일**: 2026-09-09
**입력**: functional-design(BR-CTX/IMP/CONFWARN/PLAN/PIPE/SEC/DET), nfr-design(P1~P9), logical-components
**앞 단계 반영**: 지식 그라운딩 컨텍스트 + 순수 매핑/강등 + 충돌 독립 노출 + PBT-04-A~D + 소스 자동수정 없음.
**기존 계약 소비**: `ImpactOut/ImpactItem/EvidenceRef/FeatureSummary/build_result/Warning`(result), `ImpactCategory`(domain),
`KnowledgeStore.load_feature/list_feature_summaries`(knowledge), `summarize_conflicts`(conflict), `LLMService.complete_structured`,
`build_catalog/render_catalog`(workflow), `get_prompt`(prompts).

---

## 생성/수정 파일 (logical-components 청사진)

### 코드
- [x] C1. `trace/models/impact.py` **[신설]** — `ImpactCandidate{path,category:ImpactCategory,reason,evidence:list[EvidenceRef]}`, `TaskImpactResult{candidates,change_plan}`.
- [x] C2. `trace/impact/__init__.py` **[신설]** — 패키지 공개 API.
- [x] C3. `trace/impact/context.py` **[신설]** — `KnowledgeContext`(dataclass), `rank_by_relevance`(순수), `build_context`(focus 로드·known_sources·손상 skip).
- [x] C4. `trace/impact/analyze.py` **[신설]** — `analyze_task`(LLM 1회, 실패 raise), `to_impact_out`(허구 path·근거부족 review 강등·카테고리 정렬).
- [x] C5. `trace/engine/analyze.py` **[수정]** — `analyze_task_impact(task, feature_id=None, *, path=".", llm=None)`(컨텍스트→LLM→매핑→build_result, 지식부재/실패 강등, 파일쓰기 없음).
- [x] C6. `trace/engine/__init__.py` **[수정]** — `analyze_task_impact` export.
- [x] C7. `trace/prompts/templates/analyze_task.md` **[신설]** — `${task}/${features}/${knowledge}/${known_sources}`, "화이트리스트 내 path·근거참조·근거없으면 review·순서형 change_plan(충돌해소 우선)·유효 JSON만" 명시.

### 테스트 (PBT/단위/통합)
- [x] T1. `tests/test_impact_context.py` — rank_by_relevance 결정성, build_context focus 선정·known_sources·손상 skip, 지식부재.
- [x] T2. `tests/test_impact_mapping.py` — to_impact_out: 허구 path→review, 근거부족→review+Insufficient, 카테고리 path 정렬.
- [x] T3. `tests/test_impact_properties.py` — PBT-04-A(매핑 건전성)·B(근거부족)·C(정렬 결정성/멱등)·D(related_conflicts 정합). hypothesis derandomize.
- [x] T4. `tests/test_analyze_task_impact.py` — FakeLLM: Hero Task(SMS 인증) 3범주+telephone 충돌 경고, 지식부재/LLM실패 강등, 소스 자동수정 없음.
- [x] T5. `tests/test_llm_integration.py` **[수정]** — `@pytest.mark.llm_integration` analyze_task_impact 실 API 통합 1건.

### DoD 검증
- [x] V1. `pytest -q` 전체 green(기존 113 pass 유지 + 신규), `llm_integration`는 skip.
- [x] V2. 신규 모듈 mypy-clean.
- [x] V3. Hero Task 시나리오: related_conflicts에 telephone 충돌 노출 + 3범주 분류 재현(FakeLLM 픽스처).
- [x] V4. code-summary.md 작성.

---

## 핵심 알고리즘 (functional-design 반영 요약)

**rank_by_relevance** (C3, 순수): 작업 토큰 ∩ (title+related_sources) 토큰 크기 내림차순, 동률 id 사전순 → 상위 top_n id.

**build_context** (C3): summaries 전체 + focus(feature_id 또는 랭킹 top_n) 상세 로드(손상 skip+warning) → conflicts·known_sources 조립.

**to_impact_out** (C4, 순수): `path ∉ known_sources` → review 강등; `evidence == []` → review + Insufficient evidence; 카테고리별 path 정렬; related_conflicts = summarize_conflicts(ctx.conflicts).

**analyze_task_impact** (C5): build_context → focus 없으면 안내 warning+빈 impact → try analyze_task→to_impact_out (except→warning 강등+충돌만) → confidence LOW 판정 → build_result(impact, conflicts=related). **파일 쓰기 없음.**

---

## 결정/제약
- 신규 런타임 의존성 없음. `to_impact_out`/`rank_by_relevance`는 표준 라이브러리·모델만(순수 → PBT).
- 로그/warning/reason은 rel_path·claim_key만(원문·시크릿·절대경로 금지).
- 프로젝트 루트 `path=".", llm=None`(테스트 주입), UOW-06 어댑터가 세션 루트 주입.

## Part 2 (승인 후 실행)
C1~C7 + T1~T5 생성 → V1~V4 검증 → `aidlc-docs/construction/uow-04/code/code-summary.md` 작성.

# UOW-04 (Task Impact Analysis) — NFR Design Patterns

**단계**: CONSTRUCTION / NFR Design (UOW-04)
**작성일**: 2026-09-09
**입력**: nfr-requirements(COST/PERF/REL/SEC/TST/PBT-04-A~D), functional-design(BR-CTX/IMP/CONFWARN/PLAN/PIPE/SEC/DET)
**참고**: 추가 질문 없음 — 패턴이 앞 단계 결정에서 일의적으로 도출됨.

---

## P1. 지식 컨텍스트 조립 (NFR-04-COST-2/PERF-2, BR-CTX, Q1/Q2=A)
- **패턴**: *Grounding context builder*. `build_context(task, feature_id, store)`:
  전체 `list_feature_summaries`(요약) + focus 상세(feature_id 또는 `rank_by_relevance` 상위 N=3) 로드.
  focus 로드 실패는 skip+warning(NFR-04-REL-4).
- **`rank_by_relevance`**(순수): 작업 텍스트 토큰 ∩ (title+related_sources) 토큰 크기 내림차순, 동률 id 사전순 → 결정적.
- **`known_sources`** = focus의 related_sources ∪ evidence.source — 매핑 화이트리스트(Q1=A, BR-CTX-003).

## P2. 구조화 LLM step + 상위 강등 (NFR-04-REL-1, BR-PIPE-002)
- **패턴**: *Structured call, degrade at orchestrator*. `analyze_task(ctx, llm)`는 `complete_structured(prompt, TaskImpactResult)`.
  `TraceError`는 이 step에서 잡지 않고 상위 `analyze_task_impact`가 warning 강등(빈 impact) — 충돌은 그래도 노출.
- 스키마: `TaskImpactResult{candidates:[ImpactCandidate], change_plan:[str]}`.

## P3. 매핑/강등 순수함수 (NFR-04-TST-1, PBT-04-A/B/C, BR-IMP)
- **패턴**: *Pure projection with safety demotion*. `to_impact_out(result, ctx)`:
  1. `path ∉ known_sources` → **review 강등** + reason "[근거 밖 추정]" (PBT-04-A, 환각 억제).
  2. `evidence == []` → **review 강등** + "Insufficient evidence" (PBT-04-B, NFR-AI-003).
  3. 카테고리별 `path` 안정 정렬(PBT-04-C, 입력 순서 무관).
- 네트워크·모델 없음 → FakeLLM 없이 결정적 단위·PBT.

## P4. 충돌 노출 (NFR-04-REL-2/PERF-3, PBT-04-D, BR-CONFWARN)
- **패턴**: *Independent conflict surfacing*. `related_conflicts = summarize_conflicts(ctx.conflicts)` —
  focus Feature들의 저장 conflicts를 **LLM과 독립적으로** 채움. LLM 실패 시에도 유지(경고 지속).
- `build_result`가 related_conflicts를 요약 상단에 얹어 구현 권고 전 강조(US-04.3).

## P5. 오케스트레이션 analyze_task_impact (BR-PIPE)
- **패턴**: *Context-first + graceful degradation*.
  1) build_context → focus 없으면 안내 warning + 빈 impact(BR-PIPE-003).
  2) try analyze_task → to_impact_out; except → warning 강등 + related_conflicts만 담은 ImpactOut.
  3) 근거 없는 항목 존재 시 meta.confidence="LOW"(NFR-AI-003).
  4) **파일 쓰기 없음**(소스 자동수정 금지, BR-PLAN-002).

## P6. 프롬프트 템플릿 (NFR-04-MAINT-1, C8)
- `prompts/templates/analyze_task.md`. 변수: `${task}`,`${features}`,`${knowledge}`,`${known_sources}`.
  StrictTemplate(미해결 변수→ConfigError). "known_sources 안에서만 path 지목, 근거 참조, 근거 없으면 review·Insufficient
  evidence, 순서형 change_plan(충돌 해소 우선), 유효 JSON만" 명시.

## P7. 테스트 배치 (NFR-04-TST, PBT)
| 파일 | 내용 |
|---|---|
| `tests/test_impact_mapping.py` | to_impact_out 단위 — 허구 path/근거부족 review 강등, 카테고리 정렬 |
| `tests/test_impact_context.py` | build_context/rank_by_relevance — focus 선정·known_sources·손상 skip |
| `tests/test_impact_properties.py` | PBT-04-A(매핑 건전성)·B(근거부족)·C(정렬 결정성)·D(related_conflicts 정합) |
| `tests/test_analyze_task_impact.py` | FakeLLM — Hero Task 3범주·충돌경고, 지식부재/LLM실패 강등, 자동수정 없음 |
| `tests/test_llm_integration.py` **수정** | analyze_task_impact 실 API 통합 1건(옵트인) |

## P8. 결정성/보안
- LLM 결정성은 settings(temp=0). 매핑·정렬·랭킹은 완전 결정적(PBT-04-C).
- 프롬프트/로그/reason은 rel_path·claim_key만(원문·시크릿·절대경로 금지, NFR-04-SEC-2). known_sources 화이트리스트(SEC-1).

## P9. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | P2/P5 LLM·지식부재·손상 강등, P4 충돌 독립 노출. |
| Property-Based Testing | **Compliant** | P7 PBT-04-A~D 4속성(순수함수 매핑 건전성 포함). |
| Security Baseline | **N/A(미적용)** | opt-out. P8 보안 패턴은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

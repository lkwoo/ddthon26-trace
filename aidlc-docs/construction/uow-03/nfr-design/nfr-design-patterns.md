# UOW-03 (Claims/Evidence/Conflict) — NFR Design Patterns

**단계**: CONSTRUCTION / NFR Design (UOW-03)
**작성일**: 2026-09-09
**입력**: nfr-requirements(COST/PERF/REL/SEC/TST/PBT-03-A~D), functional-design(BR-CLAIM/EVID/CONF/CONFLICT/OUT/PIPE/DET/SEC)
**참고**: 추가 질문 없음 — 패턴이 앞 단계 결정에서 일의적으로 도출됨.

---

## P1. 원자 Claim 추출 step (NFR-03-COST-1/2, BR-CLAIM/EVID, Q3=A)
- **패턴**: *Structured extraction over projected catalog*. `extract_claims(feature, assets, llm)`:
  관련 자산만(`rel_path ∈ feature.related_sources`) → `build_catalog`(UOW-02 발췌 4,000자 상속) →
  `render_catalog` → `llm.complete_structured(prompt, ClaimExtractionResult)`. Feature당 **1회** 호출.
- 반환 직전 **허구 소스 Evidence 드롭**: `source ∉ related rel_paths` 인 Evidence 제거 + `Warning`(BR-EVID-004, NFR-03-REL-2).

## P2. Feature별 격리 강등 (NFR-03-REL-1, BR-PIPE-002)
- **패턴**: *Per-feature graceful degradation*. 추출 중 `TraceError`는 **그 Feature에서 포착** →
  `([], [Warning("extract_failed", source=feature.id)])` 로 강등. 그 Feature는 UOW-02 셸 유지, 전체 파이프라인 계속.
- 상위(analyze_project)는 Feature 루프 각 반복을 try/except로 격리(`enrich_failed` warning) — 한 Feature 실패가 전체를 막지 않음.

## P3. 비-LLM 결정적 코어 (NFR-03-PERF-3/TST-1, BR-CONF/CONFLICT/DET) — **핵심 차별점**
- **패턴**: *Pure deterministic functions*. `assign_confidence`, `detect_conflicts`, `classify_conflict_type`는
  네트워크·모델 없이 evidence 구조만으로 계산 → 무런타임 비용·완전 재현.
- **충돌 존재 = 구조적 비교**(LLM 판단 아님): 한 claim_key의 evidence에서 `normalize_value` distinct ≥ 2 → Conflict 1건(BR-CONFLICT-001).
- **Confidence 규칙**(BR-CONF): `has_contradiction`(contradicts>0 또는 distinct≥2)→LOW; `supports≥2 ∧ distinct≤1`→HIGH; 그 외→MEDIUM.
- 안정 정렬: conflicts는 `claim_key` 순, values는 `(normalize_value, source)` 순으로 정렬 후 저장(NFR-03-DET, PBT-03-B 멱등 근거).

## P4. 충돌 유형 분류 — 국소화 + 폴백 (NFR-03-REL-3/MAINT-2, BR-CONFLICT-003/005)
- **패턴**: *Ordered rule table with safe default*. `classify_conflict_type(ec, vals)` 결정적 순서:
  1. `ABSENCE_TOKENS`(상수) 교집합 ∧ 요구값 존재 → `POLICY_CONFLICT`.
  2. `looks_behavioral(predicate, norm)` ∧ `has_doc_vs_code(evidence)` → `STALE_KNOWLEDGE`.
  3. 그 외 → `VALUE_MISMATCH`(P0 기본).
- **전결정성**(PBT-03-C): 임의 입력에도 예외 없이 유효 `ConflictType` 하나 반환 — 모호/미매칭은 `VALUE_MISMATCH`로 폴백(누락 금지).
- `ABSENCE_TOKENS`·행위 계열 토큰은 `conflict/detect.py` 모듈 상수로 국소화(확장 용이, NFR-03-MAINT-2).

## P5. 완본화 & 캐시-완본 스테이지 (NFR-03-PERF-1/2, BR-PIPE-001/003)
- **패턴**: *Enrich shell → complete, stage-gated cache*. `enrich_feature_knowledge(fk_shell, assets, llm)`:
  extract→confidence→detect→대표값 Claim/평탄 Evidence 채움→`meta.stage="complete"` 로 재저장.
- `analyze_project`는 `build_knowledge`(UOW-02 캐시-우선)로 셸 확보 후, **`meta.stage != "complete"` 인 Feature만** 완본화 →
  자산 불변 재실행은 캐시 히트로 전체 LLM 미호출(UOW-02 콘텐츠해시 캐시와 정합).

## P6. 조회 출력 (BR-OUT, FR-CONFLICT-OUT-001/002)
- **패턴**: *Aggregate + build_result*. `get_conflicts(feature_id)`: 지정 시 해당 Feature, 미지정 시 전체 합산 →
  `ConflictOut{type, claim, values:[{value,source,location}], interpretation}` 목록, `meta.conflicts_count`.
- 손상 저장 파일은 로드 중 skip+warning(목록 계속, NFR-03-REL-4) — `KnowledgeStore.list_feature_summaries` 정책과 정합.
- Result 조립은 `build_result`(UOW-0F, 충돌 상위 노출).

## P7. 프롬프트 템플릿 (NFR-03-MAINT-1, C8)
- `prompts/templates/extract_claims.md`. 변수: `${feature_title}`,`${feature_description}`,`${sources}`.
  StrictTemplate(미해결 변수→ConfigError). "원자 Claim(subject+predicate+value 하나)로 분해, 유효 JSON만 출력" 명시(`_extract_json` 정합).

## P8. 테스트 배치 (NFR-03-TST, PBT-03-A~D)
| 파일 | 내용 |
|---|---|
| `tests/test_conflict_detect.py` | detect_conflicts 순수함수 단위 — demo 3충돌(C-1 value_mismatch/C-2 stale_knowledge/C-3 policy_conflict) 손수 픽스처, 유형 정확 |
| `tests/test_confidence.py` | assign_confidence 규칙 단위(LOW/HIGH/MEDIUM 경계) |
| `tests/test_conflict_properties.py` | PBT-03-A(건전성)·B(결정성/멱등)·C(전결정성)·D(Confidence 정합) — hypothesis, derandomize |
| `tests/test_analyze_project.py` | FakeLLM 주입 — 스캔→지식→완본화→충돌 반환, 부분실패 격리, 캐시-완본 스테이지 재사용(LLM 미호출) |
| `tests/test_llm_integration.py` | UOW-02 `llm_integration` 마커 재사용 — analyze_project 실 API 통합 1건(env+키 시), 없으면 skip |

## P9. 결정성/보안
- LLM 결정성은 settings(temp=0)만(UOW-0F). 동일 관련 자산 → 동일 프롬프트(정렬 카탈로그).
- 경고/로그는 `rel_path`·`claim_key`·`feature_id`·`code`만(원문·시크릿·절대경로 금지, NFR-03-SEC-3).
  `Evidence.location`은 위치 표기만, 원문 스니펫 대량 복사 금지(NFR-03-SEC-2).

## P10. 확장 컴플라이언스 요약 (활성만)
| 확장 | 판정 | 근거 |
|---|---|---|
| Resiliency Baseline | **Compliant** | P2 Feature별 격리·P1 허구근거 드롭·P4 모호시 value_mismatch 폴백·P6 손상 skip. |
| Property-Based Testing | **Compliant** | P8 PBT-03-A~D 4속성(순수함수 검출 건전성·멱등·전결정성·Confidence 정합). |
| Security Baseline | **N/A(미적용)** | opt-out. P9 보안 패턴은 요구사항으로 유효. |

**Blocking 판정**: 활성 확장 위반 없음.

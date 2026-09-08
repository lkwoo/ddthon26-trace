# UOW-0F Foundation — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**작성일**: 2026-09-08
**입력**: unit-of-work.md(UOW-0F), component-methods.md(공통 Result·코어 시그니처), components.md(C4/C7/C8/S4)
**성격**: enabler 단위 — 직접 스토리 없음. 이후 전 단위가 기대는 **계약을 동결**한다.

> 이 문서는 3개 관심사(도메인 엔티티 · 비즈니스 로직 · 비즈니스 규칙)를 하나로 통합한다.
> 0F는 순수 계약이라 분량보다 **다음 단위들이 무엇에 의존하는지**를 명확히 잇는 것이 목적이다.

---

## 1. 도메인 엔티티 (C4, `trace/models/`)

Application Design의 개념 모델을 dataclass로 확정. 외부 의존 없음 → 오프라인 테스트 가능.

| 엔티티 | 필드 | 앞 단계 근거 |
|---|---|---|
| `Confidence` | HIGH/MEDIUM/LOW | FR-CONFIDENCE-001 (근거 일치도 기반) |
| `EvidenceRelation` | direct/supporting/related/contradicting | FR-EVIDENCE-001 |
| `ConflictType` | value_mismatch(P0)/missing_impl/undocumented(P1) | FR-CONFLICT-001 |
| `Evidence` | source·type·location·extracted_value·relation | FR-EVIDENCE-001, NFR-AI-002 |
| `Claim` | subject·predicate·value·evidence[]·confidence | **FR-CLAIM-001 원자 Claim** |
| `Conflict` | type·claim·values[{value,source,location}]·interpretation | FR-CONFLICT-OUT-001/002 |
| `Feature` | id·title·description·related_sources | FR-KNOWLEDGE-001 |
| `FeatureKnowledge` | feature·overview·business_rules·claims·conflicts·dependencies·confidence | FR-KNOWLEDGE-002 |

**핵심 설계 결정 — `Claim.key = subject.predicate`**: 충돌 검출(UOW-03)의 그룹핑 단위.
같은 key에 서로 다른 `value`를 주장하는 Evidence가 모이면 value_mismatch다. 이것이 RAG와의
구조적 차별점(요구사항 §1.3)을 코드로 고정한 지점이다.

## 2. 비즈니스 로직 (공통 계약, `trace/common/` + `trace/llm/`)

- **`Result` 봉투**: 모든 코어 함수 반환형. `to_dict()`가 핵심 우선 순서
  (summary→data→conflicts→impact→evidence→warnings→meta)로 직렬화 → MCP 어댑터(UOW-05)가 그대로 사용.
- **`LLMService.structured(step_key, prompt)`**: C3 워크플로우 step의 유일한 LLM 진입점.
  - `live`: Claude 호출 → JSON 추출 → 실패 시 제약 교정 재시도 1회(§17.4).
  - `replay`: `<replay_dir>/<step_key>.json` 재생 → **API 키 없이 결정적 데모**(NFR-AI-004/REL-001).
- **`get_prompt(name, **vars)`**: 프롬프트를 코드 밖 `templates/*.md`에서 로드(NFR-MAINT-002).

## 3. 비즈니스 규칙 (불변식)

1. **시크릿은 env에서만** 읽고 로그/결과에 마스킹 (NFR-SEC-001/005). `mask_secrets` + 로깅 필터.
2. **직렬화 왕복 무손실**: `from_dict(to_dict(x)) == x` (모든 모델). → 속성 테스트로 강제.
3. **Sonnet 5 샘플링 금지**: `temperature` 미전송(400 방지). 결정성은 구조화 출력+replay로.
4. **로그는 stderr**: stdio MCP 전송(stdout)을 오염시키지 않음 (UOW-05 전제).
5. **부분 실패 허용**: `Result.add_warning`로 경고 누적, 전체 중단 없음 (FR-ANALYSIS-003).

## 4. 다음 단위로 넘기는 계약 (병렬화 이음새)

`Claim/Evidence/Conflict/Feature/FeatureKnowledge` · `Result` · `LLMService.structured` ·
`get_prompt` · `load_config/get_llm_settings`. 이 시그니처가 고정되었으므로 UOW-01/05/04는
UOW-02/03 완성을 기다리지 않고 병렬 착수 가능(unit-of-work-dependency.md).

## 5. 확장 준수 요약

- **Property-Based Testing (전면)**: 모델 직렬화 왕복·`Claim.key` 안정성·`mask_secrets` 무크래시를
  Hypothesis 속성 테스트로 커버(PBT-01/02). ✅ 적용.
- **Resiliency**: 오류 타입 계층 + 사람이 읽는 `Result.error` + 진단 로깅(RESILIENCY-05). 인프라성
  룰(멀티존/DR/오토스케일)은 로컬 단일 프로세스라 **N/A**. ✅/N-A.
- **Security Baseline (확장)**: 미적용(Q8=B). 단 NFR-SEC-001/005는 `mask_secrets`·env-only로 충족.

## 6. 구현·검증 (완료조건)

- 코드: `trace/models`, `trace/common`, `trace/config`, `trace/prompts`, `trace/llm` 임포트 가능.
- 테스트: `tests/test_models.py`(속성) · `test_common.py` · `test_config_prompts_llm.py` → **23 통과**.
- 완료조건 충족: 모델·Result·config·프롬프트 로더·LLM 스켈레톤 계약 고정.

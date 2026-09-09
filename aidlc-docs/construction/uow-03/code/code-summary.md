# UOW-03 (Claims/Evidence/Conflict) — Code Summary

**단계**: CONSTRUCTION / Code Generation (UOW-03)
**작성일**: 2026-09-09
**결과**: `pytest` **113 passed, 2 skipped**(옵트인 `llm_integration`), 신규 모듈 **mypy-clean**.

---

## 생성/수정 파일

### 코드 (trace/)
| 파일 | 내용 |
|---|---|
| `models/domain.py` **수정** | `ConflictType += STALE_KNOWLEDGE, POLICY_CONFLICT` (하위 호환 — 기존 데이터 영향 없음). |
| `models/extraction.py` **신설** | `ExtractedClaim{subject,predicate,evidence}`, `ClaimExtractionResult{claims}` (LLM 중간 스키마). |
| `conflict/__init__.py` **신설** | 패키지 공개 API. |
| `conflict/detect.py` **신설** | `ABSENCE_TOKENS`, `detect_conflicts`(결정적 순수), `classify_conflict_type`(순서 규칙+폴백), 내부 헬퍼. |
| `conflict/summarize.py` **신설** | `summarize_conflicts → list[ConflictOut]`. |
| `workflow/claims.py` **신설** | `extract_claims`(Feature당 1회·허구근거 드롭), `assign_confidence`(비-LLM), `enrich_feature_knowledge`(완본화). |
| `engine/analyze.py` **신설** | `analyze_project(path, *, llm=None)`, `get_conflicts(feature_id=None, *, path=".")`, `_build_llm_service`. |
| `engine/__init__.py` **수정** | `analyze_project`, `get_conflicts` export. |
| `prompts/templates/extract_claims.md` **신설** | 원자 Claim 추출 프롬프트(`${feature_title}/${feature_description}/${sources}`). |

### 테스트 (tests/)
| 파일 | 내용 |
|---|---|
| `test_conflict_detect.py` | demo 3충돌(C-1 value_mismatch/C-2 stale_knowledge/C-3 policy_conflict) 유형 정확, 값 일치·단일값 → 0건, 폴백, 정렬. |
| `test_confidence.py` | LOW/HIGH/MEDIUM 경계 규칙 + reason 존재. |
| `test_conflict_properties.py` | PBT-03-A(건전성)·B(결정성/멱등)·C(전결정성)·D(Confidence 정합). |
| `test_analyze_project.py` | FakeLLM 파이프라인, 2회차 캐시-완본 스테이지 LLM 미호출, 추출 실패 격리, get_conflicts 조회. |
| `test_llm_integration.py` **수정** | analyze_project 실 API 통합 케이스 추가(옵트인). |

---

## 앞 단계 결정의 반영

- **결정적 충돌 검출(핵심 차별점)**: `detect_conflicts`는 evidence의 `normalize_value` distinct ≥ 2를
  구조적으로 비교(LLM 판단 아님). RAG 대비 차별점을 코드로 입증(BR-CONFLICT-001, NFR Design P3).
- **3유형 분류 전결정성**: `classify_conflict_type`은 순서 규칙(policy → stale → value_mismatch) +
  모호 시 value_mismatch 폴백 → 임의 입력에 예외 없이 유효 유형 하나(PBT-03-C 통과).
- **근거 일치도 Confidence(비-LLM)**: contradicts/상이값 → LOW, 다근거·일치 → HIGH, 그 외 MEDIUM(PBT-03-D 통과).
- **캐시-완본 스테이지**: `analyze_project`는 `meta.stage=="complete"` Feature를 재분석 생략 →
  자산 불변 재실행 시 LLM 0콜(테스트 실증, BR-PIPE-003).
- **Feature별 격리 강등**: 추출/완본화 실패는 warning으로 강등, 전체 파이프라인 계속(BR-PIPE-002).

## 구현 중 발견·수정

- **PBT-03-B(결정성)로 실제 결함 검출**: 동일 `claim_key`를 가진 두 ExtractedClaim이 있을 때 정렬이
  입력 순서에 의존 → 비결정. 정렬 키를 `(claim, 값 목록)` 완전 순서로 보강해 해소.

## 결정/제약

- **신규 런타임 의존성 없음**. `conflict/detect`는 표준 라이브러리·모델만 의존(순수 → PBT).
- **프로젝트 루트**: 코어 `analyze_project(path)`·`get_conflicts(path=".")`가 명시 인자로 루트를 받는다.
  MCP 어댑터(UOW-06)가 세션 루트를 주입한다(원 설계 시그니처 보강).
- 로그/warning은 rel_path·claim_key·feature_id·code만(원문·시크릿·절대경로 비노출).

## DoD
- [x] 원자 Claim·Evidence·Confidence(근거 일치도) 생성.
- [x] detect_conflicts가 demo 3충돌 유형 정확·결정적(2회 동일, PBT).
- [x] analyze_project 전체 파이프라인 통과(스캔→지식→충돌→저장), 캐시 재사용(LLM 0콜).
- [x] get_conflicts 상세 반환, 부분 실패 격리.
- [x] FakeLLM 오프라인 + 순수함수 단위/PBT. 실 API는 옵트인.

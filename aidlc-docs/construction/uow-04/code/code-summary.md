# UOW-04 (Task Impact Analysis) — Code Summary

**단계**: CONSTRUCTION / Code Generation (UOW-04)
**작성일**: 2026-09-09
**결과**: `pytest` **131 passed, 3 skipped**(옵트인 `llm_integration`), 신규 모듈 **mypy-clean**.

---

## 생성/수정 파일

### 코드 (trace/)
| 파일 | 내용 |
|---|---|
| `models/impact.py` **신설** | `ImpactCandidate{path,category,reason,evidence}`, `TaskImpactResult{candidates,change_plan}`. |
| `impact/__init__.py` **신설** | 패키지 공개 API. |
| `impact/context.py` **신설** | `KnowledgeContext`, `rank_by_relevance`(순수), `build_context`(focus·known_sources·손상 skip). |
| `impact/analyze.py` **신설** | `analyze_task`(LLM 1회·실패 raise), `to_impact_out`(순수·허구 path/근거부족 review 강등·완전 정렬). |
| `engine/analyze.py` **수정** | `analyze_task_impact(task, feature_id=None, *, path=".", llm=None)` 코어 공개(지식부재/LLM 실패 강등, 파일쓰기 없음). |
| `engine/__init__.py` **수정** | `analyze_task_impact` export. |
| `prompts/templates/analyze_task.md` **신설** | 화이트리스트 내 path·근거참조·순서형 change_plan(충돌해소 우선). |

### 테스트 (tests/)
| 파일 | 내용 |
|---|---|
| `test_impact_context.py` | rank_by_relevance 결정성, build_context focus·known_sources·손상 skip·지식부재. |
| `test_impact_mapping.py` | to_impact_out 허구 path/근거부족 review 강등·정렬·related_conflicts·change_plan. |
| `test_impact_properties.py` | PBT-04-A(매핑 건전성)·B(근거부족)·C(정렬 결정성/멱등)·D(related_conflicts 정합). |
| `test_analyze_task_impact.py` | FakeLLM Hero Task 3범주+telephone 충돌 경고, 지식부재/LLM실패 강등, 소스 자동수정 없음. |
| `test_llm_integration.py` **수정** | analyze_task_impact 실 API 케이스 추가(옵트인). |

---

## 앞 단계 결정의 반영

- **지식 그라운딩(차별점)**: `analyze_task_impact`는 저장된 FeatureKnowledge·Evidence를 컨텍스트로 사용
  (일반 LLM 프롬프트 단독 아님, FR-IMPACT-002). `known_sources` 화이트리스트 밖 path는 신뢰 불가로 review 강등.
- **근거 부족 → 겸손한 출력(NFR-AI-003)**: evidence 없는 후보는 review + "Insufficient evidence", meta.confidence LOW.
- **충돌 인지 경고(P1)**: focus Feature의 기존 conflicts(UOW-03 산출)를 `related_conflicts`로 노출 —
  **LLM 실패 시에도** 저장 지식에서 채워 경고를 유지(Hero Task: telephone 20 vs 10).
- **순서형 Change Plan·자문용**: change_plan은 충돌 해소 우선. **소스 파일 쓰기 없음**(BR-PLAN-002, 테스트로 확인).
- **부분 실패 격리**: 지식 부재("먼저 analyze_project 실행")·LLM 실패는 warning 강등(예외 전파 없음).

## 구현 중 결정

- **정렬 완전 순서화(PBT-04-C 대비)**: UOW-03 교훈을 적용해 `to_impact_out` 카테고리 정렬 키를
  `(path, reason, evidence)`로 확장 — 동일 path 후보에도 입력 순서 무관 결정성 보장.
- **관련도 랭킹**: 외부 임베딩·검색 라이브러리 없이 토큰 겹침 휴리스틱(순수·결정적) — 의존성 최소.

## 결정/제약
- **신규 런타임 의존성 없음**. `to_impact_out`/`rank_by_relevance`는 표준 라이브러리·모델만(순수 → PBT).
- 로그/warning/reason은 rel_path·claim_key만(원문·시크릿·절대경로 비노출).
- 프로젝트 루트 `path=".", llm=None`(테스트 주입), UOW-06 어댑터가 세션 루트 주입.

## DoD
- [x] 지식·근거 컨텍스트 사용(일반 프롬프트 단독 아님).
- [x] 3범주 분류 + 이유·근거 참조. 근거 부족 → review + LOW.
- [x] related_conflicts로 기존 충돌 경고(P1), 요약 상단 노출.
- [x] 순서형 Change Plan(충돌 해소 우선), 소스 자동수정 없음.
- [x] LLM 실패·지식 부재 강등(예외 전파 없음). 허구 path review 강등.
- [x] FakeLLM 오프라인 + to_impact_out/build_context 결정적 단위·PBT.

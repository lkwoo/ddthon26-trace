# TRACE — 컴포넌트 정의 (Components)

**단계**: INCEPTION / Application Design
**작성일**: 2026-09-08
**결정 반영**: Q1=A(계층별 서브모듈), Q2=A(얇은 어댑터), Q3=A(순차 파이프라인), Q4=A(공통 result envelope), Q5=A(대상 밖 `.trace/`)

> 상세 비즈니스 규칙·데이터 모델 필드는 Construction/Functional Design(유닛별)에서 확정. 여기서는 컴포넌트 경계·책임·인터페이스만 정의.

---

## 패키지 구조 (Q1=A)

```text
trace/
  mcp_server/     # C1  MCP 서버 인터페이스 (얇은 어댑터)
  engine/         # C2  로컬 지식 엔진 (스캔·파싱·분류·오케스트레이션 진입)
  workflow/       # C3  AI 워크플로우 계층 (LLM 호출 step들)
  knowledge/      # C4  지식 모델 + 저장소 (Feature/Claim/Evidence/Conflict, MD+YAML I/O)
  conflict/       # C5  충돌 검출 (value_mismatch 등)
  impact/         # C6  Task Impact Analysis
  config/         # C7  설정·제외규칙·상수
  prompts/        # C8  프롬프트 템플릿 (코드와 분리, NFR-MAINT-002)
  cli/            # C9  폴백 CLI (얇은 어댑터, Q5/FR-DEMO-002)
```

런타임 산출물(대상 프로젝트 기준): `.trace/knowledge/features/*.md`, `.trace/cache/*` (Q5=A)

---

## C1. MCP 서버 인터페이스 (`mcp_server/`)
- **매핑**: 요구사항 §4.1-A, §12
- **책임**: 5개 MCP 도구 노출, 입력 스키마 검증, 코어 호출, 결과 봉투 직렬화, 리소스(`.trace/knowledge/*.md`) 노출, (P1) 프롬프트 템플릿. stdio 전송.
- **인터페이스(제공)**: MCP tools/resources/prompts
- **의존**: C2(engine), C4(knowledge), C6(impact) — 얇은 어댑터로 호출만 (Q2=A, NFR-CORE-001)
- **불변식**: AI/비즈니스 로직을 직접 갖지 않는다.

## C2. 로컬 지식 엔진 (`engine/`)
- **매핑**: §4.1-B, §5·§6, §13
- **책임**: 로컬 파일 스캔, 자산 분류, 콘텐츠 파싱(소스/MD/텍스트/**PDF**/OpenAPI/SQL/설정/테스트), 제외 규칙 적용, 부분 실패 허용, `analyze_project` 파이프라인 진입점(코어 함수 구현), 결과 영속화 호출.
- **인터페이스(제공)**: 코어 함수 `scan_project`, `analyze_project`, `list_features`, `get_feature_knowledge`, `get_conflicts`, `analyze_task_impact` (오케스트레이션 소유)
- **의존**: C3(workflow), C4(knowledge), C5(conflict), C6(impact), C7(config)
- **불변식**: 로컬 파일시스템 직접 접근은 여기로 국한(NFR-LOCAL-001).

## C3. AI 워크플로우 계층 (`workflow/`)
- **매핑**: §4.1-C, §14
- **책임**: 명시적 순차 step (Feature 식별 → 구조화 추출 → Claim 정규화 → Evidence 그룹화 → Confidence → 지식 생성 / Task 분석 흐름). 각 step은 구조화(JSON) 출력 요구·검증, 근거 그라운딩, 환각 처리(LOW/Review). LLM 클라이언트 캡슐화.
- **인터페이스(제공)**: `identify_features()`, `extract_claims()`, `group_evidence()`, `assign_confidence()`, `generate_feature_knowledge()`, `analyze_task()` (내부 step API)
- **의존**: C8(prompts), C7(config: 모델/키), LLM 제공자(Claude)
- **불변식**: 프롬프트 문자열을 코드에 인라인하지 않는다(C8 사용).

## C4. 지식 모델 & 저장소 (`knowledge/`)
- **매핑**: §4.1-D, §7·§8·§9
- **책임**: 도메인 모델(Feature, Claim[subject/predicate/value], Evidence, Confidence, Conflict) 정의, MD+YAML Front Matter 직렬화/역직렬화, 단일 진실원 유지, `.trace/knowledge/` I/O, 캐시.
- **인터페이스(제공)**: `save_feature()`, `load_feature()`, `list_feature_summaries()`, `read_resource(path)`
- **의존**: C7(config: 경로)
- **불변식**: 구조화 값은 YAML 정규 필드에 1회만.

## C5. 충돌 검출 (`conflict/`)
- **매핑**: §8.5·§8.6, §10
- **책임**: 동일 정규화 Claim에 연관된 Evidence 값 비교 → `value_mismatch`(P0) 검출, (P1) missing_implementation/undocumented_behavior/structural_mismatch. 상충 값·소스·짧은 해석 생성.
- **인터페이스(제공)**: `detect_conflicts(feature)`, `summarize_conflicts(feature_id?)`
- **의존**: C4(knowledge)
- **불변식**: 소스 코드가 항상 옳다고 가정하지 않음(기대 vs 유효 동작 구분).

## C6. Task Impact Analysis (`impact/`)
- **매핑**: §11
- **책임**: 자연어 작업을 기존 Feature Knowledge/Evidence 컨텍스트로 분석, Must/Likely/Review 분류 + 이유·근거, 충돌 인지 경고(P1), 순서형 Change Plan 생성.
- **인터페이스(제공)**: `analyze_task_impact(task, feature_id?)`
- **의존**: C4(knowledge), C5(conflict), C3(workflow: LLM 추론), C8(prompts)
- **불변식**: 일반 LLM 프롬프트 단독 금지(지식 기반). 소스 자동수정 없음.

## C7. 설정 (`config/`)
- **책임**: 제외 규칙, 지원 확장자, LLM 모델/키(환경변수, NFR-SEC-001), 경로·캐시 정책, 결정성 파라미터.
- **인터페이스(제공)**: `load_config()`, `get_exclusions()`, `get_llm_settings()`
- **불변식**: 시크릿은 코드/로그에 하드코딩·노출 금지.

## C8. 프롬프트 (`prompts/`)
- **책임**: step별 프롬프트 템플릿(파일), 구조화 출력 스키마 지시, (P1) MCP 프롬프트 템플릿.
- **인터페이스(제공)**: `get_prompt(name, **vars)`
- **불변식**: 코드와 분리 저장(NFR-MAINT-002).

## C9. 폴백 CLI (`cli/`)
- **매핑**: §18.6, FR-DEMO-002 (P1)
- **책임**: 동일 코어 함수를 호출하는 얇은 예제 실행기(예: `trace analyze-task "..."`). 제품 인터페이스 아님.
- **의존**: C2(engine) 코어 함수
- **불변식**: 로직 미포함, 코어 재사용만(Q2=A).

## (데이터) UOW-00 데모 데이터셋
- 코드 컴포넌트 아님. `demo/` 아래 픽스처(Petclinic Owner 조각 + 합성 PDF + 의도적 충돌). C2의 분석 대상 입력.

## C10. 온보딩 맵 빌더 (`map/`) *(Increment 2 신설)*
- **매핑**: 요구사항 §4.10 FR-MAP-001~007, UOW-07
- **책임**: 진입점 식별 · 정적 관계 추출(Java/Python import·호출, 그 외 LLM 폴백) · Feature→파일 매핑(C4 재사용) · 핵심 경로 함수 호출 관계 · Mermaid 렌더(의존 flowchart + 흐름 sequenceDiagram) · "여기서 시작하세요" 온보딩 내러티브 · `.trace/knowledge/overview.md` 직렬화.
- **인터페이스(제공)**: `extract_relations`, `find_entry_points`, `map_features_to_files`, `render_dependency_graph`, `render_sequence`, `build_map`, `save_overview`, `load_overview`.
- **의존**: C4(knowledge), C3(workflow: LLM 서술·폴백), C8(prompts), C7(config).
- **불변식**: 정적 추출은 best-effort(실패=warning+LLM 폴백); 관계 서술은 Evidence 인용, 근거부족은 LOW 표기; 프롬프트는 C8 사용.
- **상세**: `onboarding-map-design.md` 참조. 코어 함수 `generate_onboarding_map`은 C2 engine이 오케스트레이션(C10을 building block으로 사용), 어댑터 C1/C9는 코어함수만 호출.

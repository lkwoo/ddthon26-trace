# UOW-07 프로젝트 온보딩 맵 — Code Generation Plan (단일 진실원)

**단계**: CONSTRUCTION / Code Generation (per-unit) — Part 1 계획
**단위**: UOW-07 (온보딩 맵), 단일 컴포넌트 C10 `traceki/map/` + 어댑터 배선
**입력 설계**: `aidlc-docs/construction/07-map/functional-design/functional-design.md`,
`onboarding-map-design.md`(C10), requirements §4.10 FR-MAP-001~007
**프로젝트 유형**: Greenfield 단일 유닛(모놀리식 패키지) — 코드 위치 = 워크스페이스 루트 `traceki/`
**이 계획이 Code Generation의 단일 진실원이다.** 각 단계 완료 즉시 `[x]`로 표시하고, 계획 밖 로직은 만들지 않는다.

---

## 1. 유닛 컨텍스트

### 구현 스토리 (추적성)
| 스토리 | 내용 | 구현 위치 |
|---|---|---|
| US-07.1 | 온보딩 맵 생성·조회 | `generate_onboarding_map` 코어 함수 + overview.md 영속화 |
| US-07.2 | 진입점·의존 그래프 | `find_entry_points`, `extract_relations`(dep_edges), `render_dependency_graph` |
| US-07.3 | Feature→파일 매핑 | `map_features_to_files`(C4 지식 재사용) |
| US-07.4 | 함수 호출 관계 | `extract_relations`(call_edges), `render_sequence` |
| US-07.5 | 내러티브·근거 | `describe_relations`(C3 LLM step) + Evidence 인용 |

### 의존 (모두 구현 완료 — 재사용만)
- **UOW-0F**: `models`(Evidence·Feature), `common.Result`·로깅·`mask_secrets`, `llm.LLMService.structured`, `prompts.get_prompt`, `config.Config/load_config`.
- **UOW-01**: `engine.scanner.collect_assets`, `engine.assets.Asset`.
- **UOW-02**: `knowledge.KnowledgeStore`·`default_store`·`slugify`, `Feature`/`FeatureKnowledge`.

### 인터페이스·계약 (동결 — 준수)
- 코어 함수는 `Result`를 반환하고 핵심 우선 순서(`summary→data→conflicts→impact→evidence→warnings→meta`)를 지킨다.
- LLM step은 `llm.structured(step_key, prompt)` 계약을 쓴다. **replay step_key = `describe_relations`**.
- 어댑터(C1 MCP·C9 CLI)는 **얇게** — 코어 함수만 호출, 비즈니스 로직 없음(NFR-CORE-001/002).
- 영속화는 대상 프로젝트의 `.trace/knowledge/overview.md`(KnowledgeStore base 재사용).

---

## 2. 코드 생성 단계 (순차 실행)

### Step 1 — Business Logic: 도메인 모델 (`traceki/map/models.py`)  [US-07.1~5]
- [x] `traceki/map/__init__.py` 패키지 docstring 생성(C10 목적·재사용 원칙 명시)
- [x] `models.py`: `EntryPoint`, `FileNode`, `DependencyEdge`, `CallEdge`, `FeatureFileMap`, `RelationGraph`, `OnboardingMap` dataclass 정의
- [x] 각 모델에 `to_dict`(+ 필요한 곳에 `from_dict`) — overview 왕복(P3)·Result 직렬화 지원
- [x] `Evidence`(models)를 관계 근거로 그대로 재사용(FR-MAP-007), 신규 모델 정의하지 않음

### Step 2 — Business Logic: 정적 관계 추출 (`traceki/map/relations.py`)  [US-07.2, US-07.4]
- [x] `extract_relations(assets, config) -> RelationGraph`: 파일노드·dep_edges·call_edges·unresolved 구성
  - [x] Python: `ast`로 `import`/`from...import`(dep), `FunctionDef`·`Call`(call) 추출, 파싱 실패는 예외 누출 없이 `unresolved`에 적재(규칙 4, P2)
  - [x] Java: 정규식 휴리스틱 — `import x.y.Z;`(dep), 메서드 시그니처·호출 패턴(call)
  - [x] 그 외 언어/실패 → `unresolved` + warning (부분 실패 허용, FR-MAP-004)
- [x] `find_entry_points(assets, graph) -> list[EntryPoint]`: Java `@RestController`/`@*Mapping`·`public static void main`, Python `if __name__=="__main__"`·`def main`·FastAPI/Flask 라우트 휴리스틱, 근거(reason) 포함
- [x] `map_features_to_files(assets, store) -> list[FeatureFileMap]`: 저장된 Feature의 `related_sources`를 파일 카테고리와 결합(C4 재사용, US-07.3)

### Step 3 — Business Logic: Mermaid 렌더 (`traceki/map/mermaid.py`)  [US-07.2, US-07.4]
- [x] `render_dependency_graph(graph) -> str`: `flowchart LR`, 노드 id 안전화, 모든 dep_edge 참조 노드를 출력에 포함(P1)
- [x] `render_sequence(key_flow) -> str`: `sequenceDiagram`, 단계 렌더
- [x] `_sanitize_label`/`_node_id`: 특수문자·개행·따옴표 이스케이프(멱등, P4, content-validation 규칙 8)

### Step 4 — Business Logic: overview 영속화 (`traceki/map/overview.py`)  [US-07.1]
- [x] `save_overview(onboarding_map, base_dir=None) -> str`: `.trace/knowledge/overview.md` = YAML front matter(구조: entry_points·edges·feature_maps·mermaid) + Markdown 본문(내러티브 + 임베드 Mermaid). `KnowledgeStore` base 디렉터리 규칙 재사용, `mask_secrets` 적용(규칙 7)
- [x] `load_overview(base_dir=None) -> OnboardingMap`: front matter 파싱 왕복 복원(P3)
- [x] `overview_path(base_dir=None) -> str`

### Step 5 — Business Logic: LLM 서술 step (`traceki/map/describe.py`)  [US-07.5]
- [x] `describe_relations(map_context, llm) -> dict`: `get_prompt("onboarding_map", ...)` → `llm.structured("describe_relations", prompt)` → `{narrative, relation_notes[], key_flow[]}` 관대한 정규화
- [x] 근거 없는 LLM 주장 미채택·저신뢰 LOW 표기 준수(규칙 2·3, FR-MAP-007/NFR-AI-003)

### Step 6 — Business Logic: 오케스트레이션 코어 함수 (`traceki/map/__init__.py`)  [US-07.1~5]
- [x] `generate_onboarding_map(path, feature_id=None, refresh=False, config=None, store=None) -> Result`
  - [x] `refresh=False` + overview.md 존재 → `load_overview` 재사용(규칙 6, NFR-PERF-003)
  - [x] 아니면: `collect_assets`(UOW-01) → `extract_relations` → `find_entry_points` → `map_features_to_files` → `describe_relations`(LLM) → `build_map`(정적 엣지 우선 병합, 규칙 1) → `render_*` → `save_overview`
  - [x] `Result.ok(summary=narrative, data={entry_points,file_graph,feature_file_maps,call_relations,mermaid}, evidence=[...], warnings=[...])`
  - [x] 부분 실패·경로 오류를 사용자 친화 `Result.error`/warning으로 변환(규칙 4·5)
- [x] `__all__`로 공개 API 노출

### Step 7 — Business Logic Summary (문서)
- [x] `aidlc-docs/construction/07-map/code/business-logic-summary.md`: 생성 파일·규칙 매핑·PBT 커버리지 요약

### Step 8 — API Layer: C8 프롬프트 템플릿 (`traceki/prompts/templates/onboarding_map.md`)  [US-07.5]
- [x] 온보딩 서술 프롬프트 작성: 입력(진입점·의존·호출·Feature 컨텍스트), 출력 JSON 스키마(`narrative`·`relation_notes[{relation,note,evidence}]`·`key_flow[{step,file,symbol}]`), 근거 인용·불확실성 규칙 명시

### Step 9 — API Layer: C2 엔진 재노출 (`traceki/engine/__init__.py`)
- [x] `__all__`에 `generate_onboarding_map` 추가
- [x] `__getattr__` 지연 재노출(from `traceki.map`) — 순환 임포트 방지 패턴 준수

### Step 10 — API Layer: C1 MCP 도구 (`traceki/mcp_server/__init__.py`)  [US-07.1, US-07.2]
- [x] `@mcp.tool` `generate_onboarding_map(path=".", feature_id=None, refresh=False)` — 코어 함수 1:1 위임(얇은 어댑터)
- [x] `@mcp.resource("trace://overview")` — 저장된 overview.md 노출(리소스, NFR-MCP-UX-002 정신)
- [x] INSTRUCTIONS 문구에 온보딩 맵 흐름 한 줄 추가

### Step 11 — API Layer: C9 CLI 서브커맨드 (`traceki/cli/__init__.py`)  [US-07.1]
- [x] `trace map [path] [--feature ID] [--refresh] [--json]` 서브파서·핸들러 추가(얇은 어댑터, 사람이 읽는 출력 + `--json` 원시 Result)

### Step 12 — API Layer Summary (문서)
- [x] `aidlc-docs/construction/07-map/code/api-layer-summary.md`: MCP 도구/리소스·CLI 배선 요약

### Step 13 — Replay 픽스처 (`demo/replay/describe_relations.json`)  [결정적 재현]
- [x] Petclinic 데모 `describe_relations` 응답 픽스처 작성(진입점·Feature 근거 인용 포함) → API 키 없이 결정적 재현(NFR-AI-004, NFR-REL-001)

### Step 14 — 테스트: 단위 + PBT (`tests/test_map.py`)  [검증]
- [x] Python `ast` 추출·Java 정규식 추출 단위 테스트
- [x] Mermaid 렌더 단위 테스트, overview 왕복 테스트
- [x] PBT P1(노드⊇엣지)·P2(무크래시)·P3(overview 왕복)·P4(라벨 안전화 멱등) — Hypothesis

### Step 15 — 테스트: 통합 (`tests/test_map_integration.py`)  [검증]
- [x] replay 백엔드로 `generate_onboarding_map(demo/)` — 진입점·의존 그래프·Feature→파일·핵심 흐름·내러티브가 overview.md에 Mermaid 포함 생성, 관계에 근거 인용, 결정적 재현
- [x] CLI `trace map` / MCP 도구 스모크

### Step 16 — 문서: README + 코드 요약 마감
- [x] `README.md`에 `trace map` 사용 예시·MCP 도구 추가
- [x] `aidlc-docs/construction/07-map/code/code-generation-summary.md` 작성

### Step 17 — 진행 상태 갱신
- [x] `aidlc-state.md` UOW-07 Code Generation `[x]`, 다음 Build and Test로 갱신
- [x] audit.md에 완료 기록 append, 커밋

---

## 3. 코드 레이아웃 (확정 경로 — aidlc-docs/ 아님)
```
traceki/map/__init__.py       # 오케스트레이션 코어 함수 generate_onboarding_map + 공개 API
traceki/map/models.py         # 도메인 dataclass
traceki/map/relations.py      # 정적 추출(Python ast · Java 정규식) + 진입점 + Feature 매핑
traceki/map/mermaid.py        # Mermaid 렌더 + 라벨 안전화
traceki/map/overview.py       # save/load_overview (.trace/knowledge/overview.md)
traceki/map/describe.py       # describe_relations LLM step
traceki/prompts/templates/onboarding_map.md   # C8 프롬프트
demo/replay/describe_relations.json            # replay 픽스처
tests/test_map.py             # 단위 + PBT
tests/test_map_integration.py # 통합(데모)
```
배선(기존 파일 in-place 수정): `traceki/engine/__init__.py`, `traceki/mcp_server/__init__.py`,
`traceki/cli/__init__.py`, `README.md`.

## 4. 완료 기준
- Step 1~17 모두 `[x]`
- US-07.1~5 구현 완료, FR-MAP-001~007 코드 접지
- 신규 테스트 통과(기존 63 + UOW-07 추가), replay 결정적 재현
- 어댑터 얇음 유지(코어 함수만 호출), 순환 의존 없음

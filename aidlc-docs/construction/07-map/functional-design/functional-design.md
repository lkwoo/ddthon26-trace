# UOW-07 프로젝트 온보딩 맵 — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: `onboarding-map-design.md`(C10), unit-of-work.md(UOW-07), requirements §4.10 FR-MAP-001~007
**스토리**: US-07.1(생성·조회), US-07.2(진입점·의존 그래프), US-07.3(Feature→파일), US-07.4(함수 호출), US-07.5(내러티브·근거)
**의존**: UOW-0F(models·Result·LLMService·get_prompt), UOW-01(Asset), UOW-02(Feature·KnowledgeStore)

> 기존 모델(`Asset`, `Evidence`, `Feature`, `FeatureKnowledge`, `KnowledgeStore`, `LLMService`, `get_prompt`)을 **재사용**한다. 신규 코드는 `traceki/map/` 하위에 둔다.

## 1. 도메인 (`traceki/map/models.py`)

```python
@dataclass class EntryPoint:     kind: str; symbol: str; file: str; reason: str
@dataclass class FileNode:       path: str; module: str; type: str          # code/api/db/config/test
@dataclass class DependencyEdge: src: str; dst: str; kind: str="import"; evidence: Evidence|None=None
@dataclass class CallEdge:       caller: str; callee: str; file: str; evidence: Evidence|None=None
@dataclass class FeatureFileMap: feature_id: str; title: str; files: list[dict]  # [{path,category}]
@dataclass class RelationGraph:  nodes: list[FileNode]; dep_edges: list[DependencyEdge]
                                 call_edges: list[CallEdge]; unresolved: list[str]
@dataclass class OnboardingMap:  entry_points; file_graph: RelationGraph; feature_file_maps
                                 call_relations; narrative: str; mermaid: dict
                                 evidence: list[Evidence]; warnings: list[str]
```
- `Evidence`(source/type/location/extracted_value/relation)를 그대로 관계 근거로 재사용(FR-MAP-007).

## 2. 비즈니스 로직

- **`generate_onboarding_map(path, feature_id=None, refresh=False) -> Result`** (C2 코어 함수):
  `refresh=False`이고 `overview.md` 캐시 존재 → `load_overview` 재사용(NFR-PERF-003). 아니면:
  `collect_assets`(UOW-01 재사용) → `extract_relations`(C10) → `find_entry_points`(C10) →
  `map_features_to_files`(C4 지식) → `describe_relations`(C3 LLM) → `build_map`(병합) →
  `render_*`(Mermaid) → `save_overview`(C4) → Result.
  `data={entry_points, file_graph, feature_file_maps, call_relations, mermaid}`,
  `summary=narrative`, `evidence=[...]`, `warnings=[...]`.
- **`relations.py`** 정적 추출(FR-MAP-004, Java/Python):
  - Python: `ast`로 `import`/`from ... import`(의존), `FunctionDef`·`Call` 노드(호출) 추출.
  - Java: 정규식 휴리스틱 — `import x.y.Z;`(의존), 메서드 시그니처·호출 패턴(호출), `@RestController`/`@*Mapping`·`public static void main`(진입점).
  - 그 외 언어/파싱 실패 → `RelationGraph.unresolved`에 파일 경로 적재(LLM 폴백 위임) + warning.
- **`describe_relations(map_context, llm)`** (C3 step): `get_prompt("onboarding_map", context=...)` →
  `llm.structured("describe_relations", prompt)` → `{narrative, relation_notes[], key_flow[]}`.
- **`mermaid.py`**: `render_dependency_graph`(`flowchart LR`, 노드 id 안전화), `render_sequence`(`sequenceDiagram`, key_flow 단계).
- **`save_overview/load_overview`**: `.trace/knowledge/overview.md` = YAML front matter(구조) + Markdown(내러티브 + 임베드 Mermaid). `KnowledgeStore` 디렉터리 재사용.

## 3. 비즈니스 규칙

1. **하이브리드 병합**(FR-MAP-002): 정적 뼈대가 관계의 사실(엣지), LLM은 서술·근거·핵심흐름. 충돌 시 정적 엣지 우선, LLM은 rationale만.
2. **근거 인용**(FR-MAP-007, NFR-AI-002): 모든 관계·흐름 서술에 `Evidence(source, location)` ≥1. 근거 없는 LLM 주장은 채택 안 함.
3. **불확실성**(NFR-AI-003): 근거 부족 관계는 `confidence=LOW`/"Insufficient evidence" 표기, 단정 금지.
4. **부분 실패 허용**(FR-MAP-004, FR-ANALYSIS-003): 개별 파일 정적 파싱 실패 → warning + unresolved 폴백, 전체 중단 없음.
5. **경로 검증·제외**(NFR-SEC-004): `collect_assets` 재사용으로 이미 검증·제외된 assets만 대상.
6. **캐시**(NFR-PERF-003): `refresh=False` + overview.md 존재 시 LLM 재호출 없이 재사용.
7. **시크릿 비노출**(NFR-SEC-005): overview.md·Result에 기존 `mask_secrets` 적용.
8. **Mermaid 문법 검증**(content-validation): 노드 라벨 특수문자 이스케이프, 순환 라벨 허용, 렌더 문자열은 파싱 가능한 형태로만 생성.

## 4. 확장 준수

- **PBT (전면, Hypothesis)** — 순수 로직 속성:
  - P1: `render_dependency_graph(g)`는 `g`의 모든 dep_edge 노드를 출력에 포함(노드⊇엣지참조 불변).
  - P2: Python `extract_relations`는 임의 소스 문자열에 무크래시(파싱 실패=unresolved, 예외 누출 없음).
  - P3: `save_overview`→`load_overview` 왕복(round-trip)에서 entry_points·edges 보존.
  - P4: Mermaid 렌더 출력에 미이스케이프 개행/따옴표로 인한 문법 파손 없음(라벨 안전화 멱등).
- **Resiliency**: 부분 실패·warning 누적·사용자 친화 오류(로컬 단일 프로세스, 인프라 룰 N/A). 관측성=로깅(NFR-LOG-001): 관계추출/폴백/저신뢰 로그.

## 5. 검증 (Code Generation에서 구현)

- `tests/test_map.py`: 정적 추출(Python `ast`·Java 정규식) 단위, Mermaid 렌더, overview 왕복, PBT P1~P4.
- `tests/test_map_integration.py`: 데모(Java Petclinic) 대상 `generate_onboarding_map` — 진입점·의존 그래프·Feature→파일·핵심 흐름·내러티브가 overview.md에 Mermaid 포함 생성, 관계에 근거 인용, replay 결정적 재현.
- CLI `trace map demo/` / MCP `generate_onboarding_map` 스모크.

## 6. 다음 단계 (Code Generation 이연)
- `onboarding_map.md` 프롬프트 실제 내용·JSON 스키마, Java 정규식 세부, Mermaid 이스케이프 규칙, replay 픽스처(`describe_relations` 응답 캐시), README `trace map` 예시.

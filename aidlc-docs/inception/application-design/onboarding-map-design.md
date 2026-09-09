# TRACE — 애플리케이션 설계 (Increment 2: 프로젝트 온보딩 맵)

**단계**: INCEPTION / Application Design (증분)
**작성일**: 2026-09-09
**입력**: `requirements.md` §4.10 FR-MAP-001~007, `stories.md` EPIC UOW-07(US-07.1~5), `personas.md` P4 뉴비
**정착 결정 재사용**: Q1=A(계층별 서브모듈), Q2=A(얇은 어댑터), Q3=A(순차 파이프라인), Q4=A(공통 Result envelope), Q5=A(대상 밖 `.trace/`)

> 이 문서는 온보딩 맵 기능을 위해 **추가되는 컴포넌트(C10)·메서드·의존성·데이터 흐름**만 정의한다.
> 기존 C1~C9 경계·원칙은 그대로 유지하며, 아래는 그 위에 얹는 증분이다.

---

## 1. 설계 결정 (증분)

| # | 결정 | 근거 |
|---|---|---|
| M1 | 온보딩 맵 전용 신규 컴포넌트 **C10 `map/`** 신설 (engine에 몰지 않음) | 모듈 분리(NFR-MAINT-001), 단위=서브모듈 관행. 관계 추출·Mermaid·내러티브는 별도 책임 |
| M2 | 코어 함수 `generate_onboarding_map`은 **C2 engine이 오케스트레이션**, building block은 C10 | 기존 코어함수(analyze_project 등)가 engine 소유인 관행과 일치. 어댑터(C1/C9)는 코어함수만 호출 |
| M3 | 관계 추출 = **하이브리드**: C10 정적 추출기(결정적 뼈대) + C3 workflow LLM step(근거 서술) | FR-MAP-002. 기존 Claim↔Evidence 근거기반 철학 재사용 |
| M4 | 정적 추출기는 **이미 스캔된 Asset.content 위에서** 동작(신규 파일 접근 없음) | 파일 접근은 C2/C4로 국한(NFR-LOCAL-001) 유지 |
| M5 | 영속화 = **`.trace/knowledge/overview.md`** (YAML front matter + Markdown + 임베드 Mermaid), C4 저장소 재사용 | FR-MAP-006, Q5=A. 기존 features/*.md I/O 패턴과 동형 |
| M6 | 정적 대상 언어 = **Java·Python**, 그 외 = **LLM 폴백** | FR-MAP-004, Q5=A. 데모(Java Petclinic)·TRACE(Python) 확실 커버 |

---

## 2. 신규 컴포넌트 C10 — 온보딩 맵 빌더 (`traceki/map/`)

- **매핑**: FR-MAP-001~007, UOW-07
- **책임**:
  - 진입점 식별(실행/요청 진입점: `main`, 컨트롤러/핸들러 등)
  - **정적 관계 추출**(Java/Python): 파일 간 import/의존 단서, 함수 정의·호출 단서 → 결정적 뼈대
  - Feature→파일 매핑 조립(C4 지식 재사용)
  - 핵심 경로 함수 호출 관계 조립(정적 단서 + C3 LLM 서술 병합, 근거 부착)
  - **Mermaid 렌더**: 파일/모듈 의존 그래프(`flowchart`) + 핵심 흐름(`sequenceDiagram`)
  - "여기서 시작하세요" 온보딩 내러티브 조립(진입점→핵심 Feature→핵심 흐름 순)
  - `OnboardingMap` 도메인 모델 + overview.md 직렬화
- **서브파일(개념)**: `models.py`(도메인), `relations.py`(정적 추출기), `mermaid.py`(렌더러), `builder.py`(조립·오케스트레이션 헬퍼)
- **인터페이스(제공)**: 아래 §3 참조
- **의존**: C4(knowledge: Feature·asset·저장소 I/O), C3(workflow: LLM 서술·폴백), C8(prompts), C7(config)
- **불변식**:
  - 정적 추출기는 **best-effort** — 파싱 실패 파일은 `warnings`로 남기고 LLM 폴백으로 계속(FR-MAP-004, FR-ANALYSIS-003 원칙)
  - 모든 관계·흐름 서술은 실제 자산(파일 경로/위치)을 **Evidence로 인용**(FR-MAP-007, NFR-AI-002)
  - 근거 부족 관계는 `LOW`/`Insufficient evidence` 표기, 단정 금지(NFR-AI-003)
  - AI 프롬프트는 C8 템플릿 사용(코드 인라인 금지, NFR-MAINT-002)

---

## 3. 컴포넌트 메서드 (증분)

### C2 engine — 신규 코어 함수 (= MCP 도구/CLI 구현 대상)
```python
def generate_onboarding_map(path: str = ".",
                            feature_id: str | None = None,
                            refresh: bool = False) -> Result:
    """온보딩 맵 생성·조회. 스캔(또는 캐시 재사용)→정적 관계 추출(C10)→Feature 매핑(C4)
       →핵심 경로 함수 관계+LLM 내러티브(C3)→Mermaid 렌더(C10)→overview.md 영속화(C4).
       data: {entry_points, file_graph:{nodes,edges}, feature_file_maps,
              call_relations, mermaid:{dependency, sequence}}.
       summary: '여기서 시작하세요' 온보딩 내러티브(Markdown).
       evidence: 관계별 근거 참조. warnings: 정적추출 실패/LLM폴백/저신뢰(FR-MAP-004/007).
       refresh=False이고 overview.md 캐시 존재 시 재사용(NFR-PERF-003)."""
```

### C10 map — building blocks
```python
def extract_relations(assets: list[Asset]) -> RelationGraph:
    """이미 스캔된 assets에서 파일 의존(import)·함수 정의/호출 단서를 정적 추출.
       Java/Python 지원, 그 외 언어는 needs_llm 플래그로 표시(폴백 위임). best-effort."""

def find_entry_points(assets: list[Asset], relations: RelationGraph) -> list[EntryPoint]:
    """실행/요청 진입점 식별(main, 컨트롤러/핸들러 애노테이션·라우트 단서 등)."""

def map_features_to_files(features: list[Feature], assets: list[Asset]) -> list[FeatureFileMap]:
    """C4 Feature 지식의 Evidence 소스를 파일로 역매핑(코드/API/DB/설정/테스트 범주)."""

def render_dependency_graph(graph: RelationGraph) -> str:   # Mermaid flowchart
def render_sequence(call_path: list[CallEdge]) -> str:       # Mermaid sequenceDiagram

def build_map(assets, features, relations, entry_points,
              narrative: dict) -> OnboardingMap:
    """정적 뼈대 + LLM 서술(narrative)을 병합해 OnboardingMap 조립(근거 부착)."""

def save_overview(m: OnboardingMap, store: KnowledgeStore) -> str:   # .trace/knowledge/overview.md
def load_overview(store: KnowledgeStore) -> OnboardingMap | None      # 캐시 재사용
```

### C3 workflow — 신규 AI step
```python
def describe_relations(map_context: str, llm: LLMService) -> dict:
    """정적 뼈대(진입점·의존·호출 단서)를 컨텍스트로 받아 LLM이 관계·핵심 흐름·온보딩
       내러티브를 근거와 함께 서술. 정적 추출 불가 언어의 관계도 여기서 서술 폴백.
       구조화(JSON) 출력: {narrative, relation_notes:[{from,to,rationale,evidence,confidence}],
       key_flow:[step...]}. 스키마 검증 실패 시 제약교정 재시도→실패 시 warning(NFR-AI-003)."""
```

### C8 prompts — 신규 템플릿
- `onboarding_map.md` — 진입점/의존/호출 뼈대 → 온보딩 내러티브·관계 서술·핵심 흐름(JSON 스키마 지시, 근거 인용 요구, 근거 부족 시 LOW 표기).

### C1 mcp_server — 신규 도구
```python
@mcp.tool(description="프로젝트 온보딩 맵 생성: 진입점·파일/모듈 의존 그래프·Feature→파일 매핑·핵심 함수 호출 흐름·'여기서 시작하세요' 내러티브(Mermaid 포함).")
def generate_onboarding_map(path: str = ".", feature_id: str | None = None, refresh: bool = False) -> dict
```

### C9 cli — 신규 서브커맨드
```text
trace map [path] [--feature <id>] [--refresh] [--json]
    # engine.generate_onboarding_map 호출, Result 출력(요약=온보딩 내러티브, --json=원시 봉투)
```

---

## 4. 신규 데이터 모델 (C10 map, 개념)

```python
class EntryPoint:      kind: str; symbol: str; file: str; reason: str
class FileNode:        path: str; module: str; type: str      # code/api/db/config/test
class DependencyEdge:  src: str; dst: str; kind: str; evidence: EvidenceRef   # kind: import|module
class CallEdge:        caller: str; callee: str; file: str; evidence: EvidenceRef
class FeatureFileMap:  feature_id: str; files: list[dict]      # [{path, category}]
class RelationGraph:   nodes: list[FileNode]; dep_edges: list[DependencyEdge]
                       call_edges: list[CallEdge]; unresolved: list[str]  # needs LLM fallback
class OnboardingMap:   entry_points; file_graph(RelationGraph); feature_file_maps
                       call_relations; narrative: str; mermaid: dict; evidence; warnings
```
- 기존 `Evidence`(source/type/location/extracted_value/relation)를 그대로 재사용해 근거 인용(FR-MAP-007).
- overview.md = YAML front matter(구조: entry_points, edges, feature_maps) + Markdown(narrative + 임베드 Mermaid). 단일 진실원(NFR-AI-001).

---

## 5. 데이터 흐름 — generate_onboarding_map

```text
[대상 프로젝트 파일]
      │ (C2 scan/parse — 캐시 assets 재사용, C7 제외규칙)
      ▼
   assets ──► [C10 extract_relations] ──► RelationGraph (정적 뼈대: 의존·호출, unresolved 표시)
      │                │
      │                ├──► [C10 find_entry_points] ──► entry_points
      │                │
      │  (C4 features) ├──► [C10 map_features_to_files] ──► feature_file_maps
      │                │
      ▼                ▼
   [C3 describe_relations] (C8 prompt, LLM) ──► narrative + relation_notes + key_flow  (근거·LOW표기)
      │                                                   │  (unresolved 언어 폴백 서술 포함)
      ▼                                                   ▼
   [C10 build_map] ◄──────────────────────────────────────┘
      │ (정적 뼈대 + LLM 서술 병합, Evidence 부착)
      ▼
   [C10 render_dependency_graph / render_sequence] ──► mermaid{dependency, sequence}
      │
      ▼
   [C10 save_overview → C4 store] ──► .trace/knowledge/overview.md
      │
      ▼
   Result envelope (summary=내러티브 → data → evidence → warnings) ──► [C1 도구] / [C9 CLI]
```

---

## 6. 의존성 (증분 — 순환 없음)

| 컴포넌트 | 의존 대상 (추가분) |
|---|---|
| **C10 map** (신규) | C4(knowledge), C3(workflow), C8(prompts), C7(config) |
| C2 engine | **+C10** (generate_onboarding_map 오케스트레이션) |
| C1 mcp_server | (기존) C2 코어함수 — generate_onboarding_map 추가 |
| C9 cli | (기존) C2 코어함수 — map 서브커맨드 추가 |

- 위상: C7/C8(leaf) ← C4 ← C10 ← C2 ← C1/C9. **C2→C10→C3**(기존 C2→C3와 동형, 순환 없음).
- 어댑터(C1/C9)는 여전히 코어함수만 호출, C10/C3에 직접 의존하지 않음(NFR-CORE-001 유지).

---

## 7. NFR / 확장 컴플라이언스 (설계 수준)

- **NFR-CORE-001/002**: 코어(C2 코어함수+C10 building block)와 어댑터(C1/C9) 분리, 코어 재사용 ✅
- **NFR-MAINT-001/002**: C10 신규 모듈 경계, 프롬프트는 C8 `onboarding_map.md`로 분리 ✅
- **NFR-LOCAL-001**: C10은 스캔된 Asset 위에서만 동작(신규 FS 접근 없음), 영속화는 C4 ✅
- **NFR-AI-001/002/003**: overview.md 구조화(YAML) + 관계 근거 인용 + 근거부족 LOW 표기 ✅
- **NFR-PERF-003**: overview.md 캐시 재사용(refresh=False) ✅
- **NFR-SEC-001/005**: LLM 키 env(C7), 결과/overview에 시크릿 비노출 — 기존 mask 재사용 ✅
- **Resiliency 확장**: 로컬 in-process 유지 → 인프라 룰 N/A 그대로, 관측성=로깅(NFR-LOG-001) ✅
- **PBT 확장(전면 적용)**: C10 정적 추출기(import/호출 파싱)·Mermaid 렌더·overview 직렬화는 **순수 로직**으로 속성 테스트 적합 → Functional Design에서 속성 식별(PBT-01). 예: 렌더 후 파싱 왕복(round-trip) 불변, 그래프 노드⊇엣지 참조 불변.

---

## 8. Construction 이연 사항 (UOW-07)
- 정적 추출기 정규식/파서 세부(Java import·메서드 호출 휴리스틱, Python `ast`), Mermaid 이스케이프 규칙 (Functional Design)
- `onboarding_map.md` 프롬프트 실제 내용·JSON 스키마 (Code Generation)
- overview.md YAML 스키마 확정 + PBT 속성 목록(Hypothesis) (Functional Design)
- Hero 온보딩 시나리오 replay 픽스처(결정적 재현) (Code Generation / Build&Test)

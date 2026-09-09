# UOW-07 온보딩 맵 — Code Generation 요약

**단계**: CONSTRUCTION / Code Generation (per-unit) — Part 2 완료
**계획**: `aidlc-docs/construction/plans/07-map-code-generation-plan.md` (17단계 전부 완료)
**결과**: 신규 테스트 17개 + 기존 회귀 갱신 → **전체 80개 통과** (replay, API 키 불필요)

## 생성/수정 파일

### 신규 (Business Logic — C10 `traceki/map/`)
| 파일 | 책임 | 스토리 |
|---|---|---|
| `traceki/map/__init__.py` | `generate_onboarding_map` 오케스트레이션 코어 함수 + 공개 API | US-07.1~5 |
| `traceki/map/models.py` | EntryPoint/FileNode/DependencyEdge/CallEdge/FeatureFileMap/RelationGraph/OnboardingMap (`Evidence` 재사용) | US-07.1~5 |
| `traceki/map/relations.py` | 정적 추출: Python `ast`, Java 정규식, 진입점, Feature 매핑 + `unresolved` 폴백 | US-07.2/3/4 |
| `traceki/map/mermaid.py` | `flowchart LR`·`sequenceDiagram` 렌더 + 라벨 안전화(멱등) | US-07.2/4 |
| `traceki/map/overview.py` | `.trace/knowledge/overview.md` MD+YAML 왕복 저장/로드(캐시) | US-07.1 |
| `traceki/map/describe.py` | `describe_relations` LLM step (근거·핵심 흐름) | US-07.5 |

### 신규 (API Layer · 재현 · 검증)
- `traceki/prompts/templates/onboarding_map.md` — C8 온보딩 서술 프롬프트(JSON 스키마·근거 인용 규칙).
- `demo/replay/describe_relations.json` — Petclinic replay 픽스처(결정적 재현).
- `tests/test_map.py` — 단위(Python/Java 추출·Mermaid·overview 왕복) + PBT P1~P4.
- `tests/test_map_integration.py` — 데모 replay E2E(진입점·그래프·Feature 매핑·overview.md Mermaid·근거·캐시·오류·왕복).

### 수정 (얇은 배선, in-place)
- `traceki/engine/__init__.py` — `generate_onboarding_map` 지연 재노출(`__getattr__`, 순환 방지).
- `traceki/mcp_server/__init__.py` — MCP 도구 `generate_onboarding_map` + 리소스 `trace://overview` (도구 6·리소스 3).
- `traceki/cli/__init__.py` — `trace map [path] [--feature] [--refresh] [--json]` 서브커맨드.
- `tests/test_mcp_server.py` — 6번째 도구·overview 리소스·온보딩 도구 디스패치 반영.
- `README.md` — `trace map` 예시·MCP 도구/리소스·Claude Code 예시.

## 비즈니스 규칙 준수 (functional-design §3)
1. 하이브리드 병합 — 정적 엣지가 사실, LLM은 서술/근거(`__init__` 병합, describe는 엣지 미생성). ✅
2. 근거 인용 — dep/call 엣지에 `Evidence`, 프롬프트가 evidence 인용 강제, `r.evidence` 노출. ✅
3. 불확실성 LOW — 프롬프트가 "Insufficient evidence" 지시, unresolved warning. ✅
4. 부분 실패 허용 — 파싱 실패→`unresolved`, LLM 실패→정적 맵+warning(무중단). ✅
5. 경로 검증·제외 — `collect_assets`(UOW-01) 재사용. ✅
6. 캐시 — `refresh=False` + overview.md 존재 시 `load_overview` 재사용. ✅
7. 시크릿 비노출 — `save_overview`에서 `mask_secrets`. ✅
8. Mermaid 안전화 — `_sanitize_label`/`_node_id` 멱등. ✅

## PBT 커버리지 (Hypothesis)
- P1 노드⊇엣지참조, P2 무크래시, P3 overview 왕복 보존, P4 라벨 안전화 멱등 — 전부 통과.

## 실행 증거
`trace map ./demo --refresh` (replay): 진입점 OwnerRestController(REST)·PostMapping·RequestMapping,
Feature→파일 6개, 파일 13·의존 17·호출 24건, overview.md 저장, 내러티브에 telephone value_mismatch 저신뢰 경고 포함.

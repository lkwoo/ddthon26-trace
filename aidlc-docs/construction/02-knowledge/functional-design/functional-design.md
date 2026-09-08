# UOW-02 Feature/Knowledge — Functional Design

**단계**: CONSTRUCTION / Functional Design (per-unit)
**입력**: component-methods.md(C2·C3·C4), services.md, unit-of-work.md(UOW-02), 요구사항 §7·§8
**스토리**: US-02.x(Feature 자동 검출·지식 뷰·영속화), FR-KNOWLEDGE-001/002/003
**의존**: UOW-0F(models·Result·config·prompts·LLMService), UOW-01(collect_assets), UOW-00(replay 픽스처)

## 1. 컴포넌트

- **C4 지식 저장소 (`trace/knowledge/`)**: `KnowledgeStore(base)` — `<base>/.trace/knowledge/features/<id>.md`
  에 **MD+YAML** 단일 진실원으로 저장. `save_feature/load_feature/list_feature_summaries/read_resource`.
  구조화 값은 YAML front matter(무손실 왕복), 서술은 Markdown 본문(MCP 리소스로 노출).
- **C3 워크플로우 step (`trace/workflow/`)**: `identify_features(assets, llm)`,
  `generate_feature_knowledge(feature, assets, llm, claims, conflicts)`. `LLMService.structured(step_key, prompt)` 사용.
- **C2 파이프라인 (`trace/engine/pipeline.py`)**: `analyze_project`, `list_features`, `get_feature_knowledge`.

## 2. 비즈니스 로직

- **`analyze_project(path)`**: collect_assets(01) → identify_features → (per feature) generate_knowledge
  → `register_enrich_hook`(UOW-03 Claim/Conflict 주입점) → save_feature. data: {features[], conflicts_count, assets_count}.
- **`list_features()`** / **`get_feature_knowledge(id)`**: store에서 조회. get은 conflicts/evidence를
  Result 상위 필드로 승격(NFR-MCP-UX-002), 리소스 경로를 meta에 포함.

## 3. 비즈니스 규칙

1. **캐시 재사용**(NFR-PERF-003, Q5=A): store에 지식이 있고 `refresh=False`면 재분석 없이 반환(`cached=True`).
2. **부분 실패 허용**(FR-ANALYSIS-003): Feature별 지식 생성 실패는 warning 누적 후 계속(전체 중단 없음).
3. **개방-폐쇄 확장점**: `register_enrich_hook`로 UOW-03이 파이프라인 본문 수정 없이 Claim/Conflict를 주입.
4. **근거 그라운딩**(NFR-AI-002): 프롬프트에 자산 발췌 주입, "제공된 자산에만 근거" 지시.
5. **결정성**(NFR-AI-004): replay 백엔드 step_key(`identify_features`, `generate_knowledge.<id>`)로
   API 키 없이 재현. (UOW-00 계약과 일치, `demo/replay/*.json` 신설.)

## 4. 저장 포맷

`.trace/knowledge/features/<id>.md` = `---`\<YAML: to_dict()\>`---` + `# 제목` + overview/규칙/충돌/의존 본문.
`from_dict(front_matter)`로 무손실 로드.

## 5. 검증

`tests/test_knowledge_pipeline.py` 8개 통과: 저장소 왕복·리소스 본문·슬러그 속성 테스트 +
**replay로 demo 분석** → Hero Feature(owner-registration) 검출·영속화·조회·캐시 재사용. 전체 40개 통과.

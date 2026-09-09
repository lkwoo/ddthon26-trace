# UOW-07 온보딩 맵 — Business Logic 요약 (Step 1~6)

신규 컴포넌트 C10 `traceki/map/`. 기존 모델·서비스를 재사용하고, 관계 추출·서술·렌더·영속화만 신설.

| 파일 | 핵심 함수 | 규칙/속성 |
|---|---|---|
| `models.py` | 7개 dataclass + `to_dict`/`from_dict` (`Evidence` 재사용) | P3 왕복 근거 |
| `relations.py` | `extract_relations`(Python `ast`/Java 정규식), `find_entry_points`, `map_features_to_files` | 규칙 4(부분 실패→`unresolved`), P2 무크래시 |
| `mermaid.py` | `render_dependency_graph`(flowchart), `render_sequence`(sequence), `_sanitize_label`/`_node_id` | 규칙 8, P1(노드⊇엣지)·P4(멱등) |
| `overview.py` | `save_overview`/`load_overview`/`overview_exists`(`.trace/knowledge/overview.md`) | 규칙 6(캐시)·7(`mask_secrets`), P3 |
| `describe.py` | `build_context`, `describe_relations`(`llm.structured("describe_relations")`) | 규칙 2·3(근거·저신뢰) |
| `__init__.py` | `generate_onboarding_map` 오케스트레이션(캐시→스캔→정적→LLM→병합→렌더→저장) | 규칙 1(정적 엣지 우선), NFR-CORE-001 |

**하이브리드 병합(규칙 1)**: 정적 추출이 엣지의 사실을 소유하고, `describe_relations`는 내러티브·주해·핵심 흐름만 생성(엣지 미생성). LLM 실패 시 `_fallback_narrative`로 정적 요약 제공(무중단).

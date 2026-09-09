# Unit & Property Test Instructions — TRACE

**단계**: CONSTRUCTION / Build and Test
**작성일**: 2026-09-09

---

## 실행
```bash
pytest                      # 전체 (기본 -q, 실 API 불필요)
pytest -v                   # 상세
pytest tests/test_conflict_detect.py            # 특정 파일
pytest -k "conflict or impact"                  # 키워드 필터
```

## 기대 결과
- **145 passed, 3 skipped** (skip = 옵트인 `llm_integration` 3건).
- 네트워크·API 키 없이 전량 통과(FakeLLM 주입·순수 함수).

## 테스트 맵 (유닛 ↔ 파일)
| 유닛 | 테스트 파일 |
|---|---|
| UOW-0F Foundation | test_domain_rules, test_models_serialize, test_result_warnings, test_config_settings, test_prompts_loader, test_llm_service |
| UOW-00 데모 데이터셋 | test_demo_dataset_integrity |
| UOW-01 스캐너/파서 | test_scanner_scan, test_scanner_properties, test_classifier |
| UOW-02 Feature/지식/캐시 | test_features_workflow, test_features_properties, test_knowledge_store, test_analysis_cache |
| UOW-03 Claims/충돌 | test_conflict_detect, test_confidence, test_conflict_properties |
| UOW-04 Task Impact | test_impact_context, test_impact_mapping, test_impact_properties |
| UOW-05 MCP 서버 | test_serialize_result, test_core_wrappers, test_mcp_server |
| UOW-06 통합 | test_hero_e2e |
| (공통) 파이프라인 | test_analyze_project |

## 속성 기반 테스트 (hypothesis, PBT)
`settings(derandomize=True)`로 재현 가능:
- **PBT-01-A~D**(스캐너): test_scanner_properties
- **PBT-02-A~D**(id 안전화·해시·발췌·round-trip): test_features_properties
- **PBT-03-A~D**(충돌 건전성·결정성·유형 전결정·Confidence 정합): test_conflict_properties
- **PBT-04-A~D**(매핑 건전성·근거부족 강등·정렬 결정성·related_conflicts 정합): test_impact_properties

## 정적 타입 체크
```bash
mypy                        # packages = ["trace"]
```
- 신규 유닛(UOW-01~06) 모듈은 mypy-clean.
- 알려진 잔여 1건: `trace/llm/client.py`의 `_sdk_client` None→Anthropic 할당(UOW-0F 유래, 기능 영향 없음).

## 결정성/재현성
- 충돌 검출·Confidence·영향 매핑·랭킹은 순수 함수 → 동일 입력 동일 출력.
- LLM 결정성 파라미터(temperature=0)는 설정에서만 관리.

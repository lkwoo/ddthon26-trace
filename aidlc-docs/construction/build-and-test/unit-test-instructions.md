# Unit Test Instructions — TRACE

> 단위별 순수 로직·직렬화·불변식 검증. 충돌 검출/신뢰도 산정은 결정적 순수 함수이므로
> Hypothesis 속성 기반 테스트(PBT)로 불변식을 검증한다(units-generation Q10=A 반영).

## 실행

```bash
pip install -e ".[dev]"
python3 -m pytest -q            # 전체(단위+속성+통합) 83개
```

특정 단위만:

```bash
python3 -m pytest tests/test_models.py tests/test_common.py -q          # UOW-0F 모델/Result/로깅
python3 -m pytest tests/test_config_prompts_llm.py -q                   # UOW-0F 설정/프롬프트/LLM(replay)
python3 -m pytest tests/test_engine_scanner.py -q                       # UOW-01 스캐너/파서
python3 -m pytest tests/test_knowledge_pipeline.py -q                   # UOW-02 저장소/파이프라인
python3 -m pytest tests/test_conflict.py -q                            # UOW-03 Claims/Conflict(PBT)
python3 -m pytest tests/test_impact.py -q                              # UOW-04 Task Impact
python3 -m pytest tests/test_mcp_server.py -q                          # UOW-05 MCP 어댑터
python3 -m pytest tests/test_map.py -q                                 # UOW-07 온보딩 맵(단위+PBT)
```

## 커버리지 매핑 (단위 → 테스트 → 검증 대상)

| 단위 | 테스트 파일 | 핵심 검증 |
|---|---|---|
| UOW-0F | test_models, test_common, test_config_prompts_llm | 모델 직렬화 왕복, Result 봉투 키 순서, replay LLM 결정성 |
| UOW-01 | test_engine_scanner | 자산 분류·파싱·제외규칙·경로검증(NFR-SEC-004)·부분실패=warning |
| UOW-02 | test_knowledge_pipeline | 저장소 MD+YAML 왕복, analyze_project 캐시, 미지 feature 오류 |
| UOW-03 | test_conflict | **속성**: normalize_value 멱등, 동일값 무충돌, 불일치 대칭, 순서 무관 결정성; 신뢰도 규칙 |
| UOW-04 | test_impact | Must/Likely/Review 분류·근거 동반·충돌 인지·소스 불변(FR-IMPACT-003) |
| UOW-05 | test_mcp_server | 도구 6종 등록, 리소스 노출, stdio 디스패치, 봉투 키 순서 |
| UOW-07 | test_map | Python `ast`/Java 정규식 관계 추출, Mermaid 렌더·라벨 안전화, overview 왕복, **PBT P1~P4** |

## 속성 테스트(Hypothesis) 불변식

- `normalize_value(normalize_value(v)) == normalize_value(v)` (멱등)
- 동일 정규화 값만 있으면 `detect_conflicts == []` (표기 달라도 무충돌)
- 서로 다른 값 2개 → 정확히 1건 value_mismatch, 두 값 모두 근거 보존
- 입력 순서를 뒤집어도 `to_dict()` 동일 (안정 정렬 → 결정성)

### UOW-07 온보딩 맵 불변식 (test_map.py)

- **P1** 의존 그래프 렌더는 모든 dep_edge가 참조하는 노드를 출력에 선언한다(끊긴 노드 없음)
- **P2** Python 관계 추출은 임의 입력(깨진 소스 포함)에도 예외를 누출하지 않고 `unresolved`로 흡수
- **P3** overview.md 저장→로드 왕복이 진입점·엣지를 보존(front matter 직렬화 결정성)
- **P4** `_sanitize_label`은 멱등 — 한 번 안전화한 라벨을 다시 안전화해도 불변

## API 키 없이 실행 (NFR-AI-004)

모든 테스트는 `replay` 백엔드(`demo/replay/*.json` 픽스처)로 동작하므로 `ANTHROPIC_API_KEY` 불필요.

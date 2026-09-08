# Build and Test Summary — TRACE

> CONSTRUCTION 최종 단계. 8개 단위(UOW-0F~06) 완료 후 전체 빌드·테스트 지침 요약과 검증 결과.

## 상태 요약

| 항목 | 결과 |
|---|---|
| 단위 완료 | UOW-0F, 00, 01, 02, 03, 04, 05, 06 — **8/8** |
| 설치 | `pip install -e .` 성공, `trace`/`trace-mcp` 진입점 노출 |
| 테스트 | `pytest` **62개 전부 통과** (단위 + Hypothesis 속성 + 통합) |
| Hero E2E | replay 백엔드로 API 키 없이 결정적 재현 — value_mismatch(전화번호 20 vs 10) 검출→영향분석→5단계 Change Plan |
| 저장소 밖 실행 | 설치된 `trace` 명령이 `/tmp`에서 정상 동작 (stdlib 충돌 해소) |
| 시연 증거 | `result/hero-run.txt`(실제 CLI 전사), `result/README.md` |

## 지침 파일

| 파일 | 내용 |
|---|---|
| build-instructions.md | 사전요건·설치·의존성·시크릿·트러블슈팅 |
| unit-test-instructions.md | 단위별 테스트·PBT 불변식·커버리지 매핑 |
| integration-test-instructions.md | Hero 시나리오 CLI/MCP E2E·수동 절차 |
| performance-test-instructions.md | replay 지연·캐시 재사용 측정 |

## 빠른 실행(요약)

```bash
pip install -e ".[dev]"
python3 -m pytest -q                                 # 62 passed

export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR=$PWD/demo/replay TRACE_HOME=/tmp/trace
trace analyze-project ./demo --refresh
trace conflicts                                      # value_mismatch 1건
trace analyze-task "Add SMS verification to Owner registration"
```

## NFR/평가 대응 링크

- **NFR-REL-001 / NFR-AI-004** — replay 백엔드로 반복 가능·API 키 불필요 E2E.
- **NFR-SEC-001** — 시크릿 env 전용, `mask_secrets` 마스킹, 소스에 평문 키 부재(테스트로 강제).
- **완성도(평가)** — 진입점→코어→구현까지 호출 완결, 실행 전사(result/)가 README 기능과 정합.
- **사용성(평가)** — README 30초 replay 데모·`.mcp.json` 스니펫·예제 프롬프트로 막힘 없이 시작.

## 다음 단계

Build and Test 완료. OPERATIONS 단계는 현재 placeholder(배포·모니터링은 향후 확장).

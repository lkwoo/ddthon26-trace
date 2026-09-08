# Integration Test Instructions — TRACE

> 단위 간 상호작용을 Hero 시나리오로 관통 검증한다. replay 백엔드로 API 키 없이 **결정적·반복 가능**
> (NFR-REL-001). 앞 단계 반영: workflow-planning의 Hero 흐름(스캔→지식→충돌→영향)을 그대로 통과.

## Hero 시나리오

> "Owner 등록에 SMS 인증 추가" 작업 착수 전, 전화번호 `max_length` 값 불일치(요구 20 vs 코드/명세 10)를
> 근거와 함께 경고하고 변경 영향·Change Plan을 제시한다.

## 자동 통합 테스트

```bash
python3 -m pytest tests/test_cli_integration.py tests/test_mcp_server.py -q
```

- `test_cli_full_hero_flow_exit_codes` — analyze-project→list-features→conflicts→analyze-task 전 흐름 종료코드 0, `value_mismatch`·`Change Plan` 출력
- `test_tool_dispatch_hero_flow` (MCP) — 도구 디스패치로 동일 흐름, 봉투 키 순서(summary 우선)
- `test_impact_does_not_mutate_sources` — 소스 자동수정 없음(FR-IMPACT-003) 불변 검증

## 수동 E2E (CLI, 저장소 밖에서도 동작)

```bash
export TRACE_LLM_BACKEND=replay
export TRACE_REPLAY_DIR=$PWD/demo/replay
export TRACE_HOME=/tmp/trace-e2e            # 지식 저장 위치(격리)

trace analyze-project ./demo --refresh      # Feature 1개, 충돌 1건, 자산 12개
trace list-features
trace conflicts                             # [value_mismatch] Owner.telephone.max_length: 10 ... / 20 ← ...pdf
trace analyze-task "Add SMS verification to Owner registration"
                                            # 반드시변경/변경가능/검토 + 충돌 경고 + 5단계 Change Plan
```

기대 산출은 `result/hero-run.txt`(실제 실행 전사)와 일치해야 한다.

## 수동 E2E (MCP stdio 서버)

```bash
export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR=$PWD/demo/replay
trace-mcp                                   # stdio로 대기(도구 5 + 리소스 2)
```

Claude Code 연결은 `.mcp.json`에 `trace-mcp`를 stdio 서버로 등록(README 스니펫). 도구 호출 시
코어 함수 결과 봉투(summary→data→conflicts→impact→evidence→warnings→meta)를 그대로 반환.

## 검증 포인트

| 상호작용 | 기대 |
|---|---|
| 스캔→지식 | Hero Feature(owner-registration) 식별, `.trace/knowledge/features/*.md` 저장 |
| 지식→충돌 | Claim(Owner.telephone.max_length) 그룹에서 값 10/20 불일치 → 1건 검출, 근거 소스 인용 |
| 지식→영향 | 컨트롤러=반드시 변경, 충돌 인지 경고, 순서형 Change Plan ≥3단계 |
| 코어→MCP/CLI | 동일 Result를 두 어댑터가 동일하게 직렬화(얇은 어댑터, NFR-CORE-001) |

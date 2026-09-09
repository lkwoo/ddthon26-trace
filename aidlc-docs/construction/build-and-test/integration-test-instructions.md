# Integration Test Instructions — TRACE

> 단위 간 상호작용을 Hero 시나리오로 관통 검증한다. replay 백엔드로 API 키 없이 **결정적·반복 가능**
> (NFR-REL-001). 앞 단계 반영: workflow-planning의 Hero 흐름(스캔→지식→충돌→영향)을 그대로 통과.

## Hero 시나리오

> "Owner 등록에 SMS 인증 추가" 작업 착수 전, 전화번호 `max_length` 값 불일치(요구 20 vs 코드/명세 10)를
> 근거와 함께 경고하고 변경 영향·Change Plan을 제시한다.

## 자동 통합 테스트

```bash
python3 -m pytest tests/test_cli_integration.py tests/test_mcp_server.py tests/test_map_integration.py -q
```

- `test_cli_full_hero_flow_exit_codes` — analyze-project→list-features→conflicts→analyze-task 전 흐름 종료코드 0, `value_mismatch`·`Change Plan` 출력
- `test_tool_dispatch_hero_flow` (MCP) — 도구 디스패치로 동일 흐름, 봉투 키 순서(summary 우선)
- `test_impact_does_not_mutate_sources` — 소스 자동수정 없음(FR-IMPACT-003) 불변 검증
- `test_map_integration` (UOW-07) — analyze-project로 Feature 적재 후 `generate_onboarding_map(demo/)`: 진입점(REST 컨트롤러)·의존 그래프·Feature→파일 매핑·내러티브(OwnerRestController 언급)·Mermaid 생성, overview.md 왕복, 캐시 재사용, 잘못된 경로 → `Result.error`

## 온보딩 맵 E2E (UOW-07, Increment 2)

> 신규 온보딩 맵 흐름: 낯선 프로젝트의 진입점·파일 의존·함수 호출·Feature 매핑을 정적 추출 +
> LLM 서술(하이브리드)로 만들어 `.trace/knowledge/overview.md`에 영속화. replay로 결정적 재현.

```bash
export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR=$PWD/demo/replay TRACE_HOME=/tmp/trace-e2e

trace analyze-project ./demo --refresh      # 먼저 Feature 지식 적재(맵의 Feature→파일 매핑 근거)
trace map ./demo --refresh                  # 진입점·의존/호출 그래프·Feature 매핑·내러티브 생성
                                            #   → OwnerRestController(REST) 진입점, dep/call 엣지,
                                            #     owner-registration Feature 매핑, overview.md 저장
trace map ./demo                            # 2회차: overview.md 캐시 재사용(cached, refresh 없음)
trace map ./demo --json                     # 원시 Result 봉투(summary→data→…→meta)
```

- 정적 추출이 엣지의 사실을 소유하고 `describe_relations`(LLM)는 내러티브·주해·핵심 흐름만 생성(엣지 미생성).
- LLM 실패 시에도 `_fallback_narrative`로 정적 요약을 반환(무중단, 규칙 4).
- 내러티브는 전화번호 `value_mismatch` 저신뢰 주의를 근거와 함께 표기(FR-MAP-007/NFR-AI-003).

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
trace-mcp                                   # stdio로 대기(도구 6 + 리소스 3, 온보딩 맵 도구·trace://overview 포함)
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
| 스캔→맵(정적) | 진입점·dep/call 엣지·파일노드 추출, 파싱 실패는 `unresolved`로 흡수(무중단) |
| 지식→맵(Feature) | 저장된 Feature의 `related_sources`로 Feature→파일 매핑(C4 재사용) |
| 맵→영속화 | overview.md(YAML front matter + Mermaid 본문) 저장→로드 왕복, refresh 없으면 캐시 |

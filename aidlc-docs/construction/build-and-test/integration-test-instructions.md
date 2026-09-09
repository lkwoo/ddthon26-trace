# Integration & E2E Test Instructions — TRACE

**단계**: CONSTRUCTION / Build and Test
**작성일**: 2026-09-09

---

## 1. Hero E2E (오프라인, 결정적) — 유닛 간 상호작용
demo/(Petclinic 부분집합 + 의도적 충돌)에 스크립트 FakeLLM을 주입해 전 파이프라인을 구동한다.

```bash
pytest tests/test_hero_e2e.py -v
```
검증하는 유닛 상호작용:
- engine(스캔) → workflow(식별·지식) → conflict(검출) → knowledge(저장) → impact(영향).
- **3충돌**(value_mismatch·policy_conflict·stale_knowledge) 유형 정확.
- analyze_task_impact가 기존 충돌을 related_conflicts로 경고 + Must/Likely/Review + Change Plan.
- 2회 반복 동일(캐시 히트 무LLM, NFR-AI-004).

## 2. 데모 하니스 (수동 실행 증거)
```bash
python demo/run_demo.py                                  # 콘솔 출력
python demo/run_demo.py > result/hero-demo-output.txt 2>/dev/null   # 증거 저장
```
- API 키 불필요. 매 실행 동일 출력. `result/hero-demo-output.txt`가 실행 증거.

## 3. MCP 서버 통합 (구성 검증)
```bash
pytest tests/test_mcp_server.py -v
```
- `build_server()`가 5 도구·리소스 템플릿·프롬프트 등록 확인(`importorskip("mcp")`).
- `_root()` 환경변수 우선, `trace-mcp` 엔트리포인트 import 가능.

## 4. CLI 통합 (수동)
```bash
# 임시 프로젝트에서 (analyze는 실 LLM 필요 → 키 설정 시)
export TRACE_PROJECT_ROOT=/path/to/project
trace analyze                      # 지식 생성(LLM)
trace features                     # 저장 지식(무LLM)
trace conflicts --json             # 구조화 출력
trace impact "Add SMS verification to Owner registration"
```

## 5. 실 API 통합 (옵트인, 기본 skip)
```bash
export TRACE_RUN_LLM_INTEGRATION=1
export ANTHROPIC_API_KEY=sk-ant-...
pytest -m llm_integration -v
```
- 대상: identify_features / analyze_project / analyze_task_impact 실 API 스모크(3건).
- 키·env 미설정 시 자동 skip(CI·일반 실행은 비용·네트워크 없음).

## 6. Claude Code 수동 E2E (GUI)
[`result/README.md`](../../../result/README.md)의 절차대로 `.mcp.json` 연결 후 Hero 예제 프롬프트 실행.
예상 결과는 `result/hero-demo-output.txt`와 동일.

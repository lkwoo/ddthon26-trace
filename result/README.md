# result/ — 시연 증거 인덱스

TRACE Hero 시나리오의 실행 증거를 담습니다.

| 파일 | 내용 |
|---|---|
| [`hero-demo-output.txt`](hero-demo-output.txt) | `python demo/run_demo.py`의 **실제 콘솔 출력**(무키·결정적). analyze_project→list_features→get_conflicts→analyze_task_impact 전 구간. |
| [`usage-walkthrough.md`](usage-walkthrough.md) | P1/P2/P3 페르소나별 사용 여정(언제·요청·도구·증거·이점). |
| `screenshots/` (선택) | Claude Code GUI 스크린샷 — 아래 절차로 생성. |

## 결정적 실행 증거 재생성 (API 키 불필요)

```bash
python demo/run_demo.py > result/hero-demo-output.txt 2>/dev/null
```
스캔·파싱·충돌검출·영향매핑은 실제 코드가 수행하고 LLM만 고정 응답으로 대체하므로 매번 동일한 출력이 나옵니다.

## GUI 스크린샷 생성 절차 (Claude Code, 실 API 키 필요)

이 저장소의 자동화 환경에서는 GUI 캡처가 불가하여 **결정적 CLI 실행 증거**로 갈음했습니다.
실제 Claude Code 화면 스크린샷이 필요하면 아래 절차로 직접 캡처하세요:

1. `pip install -e ".[dev]"` 후 `.env`에 `ANTHROPIC_API_KEY` 설정.
2. 분석할 프로젝트(예: 이 저장소의 `demo/`)에 [`README.md`](../README.md)의 `.mcp.json` 스니펫 배치
   (`TRACE_PROJECT_ROOT`를 `demo/` 절대경로로).
3. Claude Code에서 TRACE 도구가 뜨는지 확인 후, Hero 예제 프롬프트를 순서대로 실행:
   - "이 프로젝트를 분석해줘"  → `analyze_project`
   - "발견된 충돌을 보여줘"    → `get_conflicts`
   - "Owner 등록에 SMS 인증 추가 시 영향과 리스크는?" → `analyze_task_impact`
4. 각 단계의 화면(도구 호출 → 충돌 경고 → Change Plan)을 `result/screenshots/`에 저장.

예상 화면 내용은 `hero-demo-output.txt`와 동일한 3충돌·영향·Change Plan입니다.

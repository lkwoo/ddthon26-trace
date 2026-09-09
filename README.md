# TRACE — 개발자 지식 인텔리전스

> 프로젝트 산출물(요구사항·OpenAPI·소스·DB·설정·테스트·문서)을 **기능 단위 지식**으로 재구성하고,
> 문서와 구현이 **어긋난 지점(충돌)을 근거와 함께** 드러내는 로컬 MCP 서버입니다.
> Claude Code 같은 MCP 클라이언트가 코드를 만들기 **직전에** 호출해, 낡은 명세 위에서 자신 있게
> 잘못 구현하는 것을 막습니다.

**차별점**: 충돌 검출은 LLM의 자기 판단이 아니라 **근거(Evidence)의 구조적 비교**로 이뤄집니다
(같은 사실에 대해 문서·코드·스키마가 말하는 값이 다르면 충돌). 그래서 결정적이고 재현 가능합니다.

---

## 30초 시연 (Claude Code 연동)

### 1) 설치
```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows(Git Bash) / macOS·Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) API 키 (커밋 금지 — 환경변수/.env)
```bash
cp .env.example .env                 # ANTHROPIC_API_KEY 채우기
```

### 3) Claude Code에 연결 — `.mcp.json` 복붙
분석할 프로젝트 루트(`cwd`)에 아래 `.mcp.json`을 두면 Claude Code가 stdio로 TRACE를 띄웁니다.
```json
{
  "mcpServers": {
    "trace": {
      "command": "trace-mcp",
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "TRACE_PROJECT_ROOT": "."
      }
    }
  }
}
```
> `command`는 `pip install` 후 등록되는 콘솔 스크립트입니다. `TRACE_PROJECT_ROOT` 미지정 시 실행 디렉터리를 분석합니다.

### 4) Hero 예제 프롬프트 (Claude Code 대화창)
```
1. "이 프로젝트를 분석해줘" 			  → analyze_project
2. "발견된 문서/구현 충돌을 보여줘" 		  → get_conflicts
3. "Owner 등록에 SMS 인증을 추가하려는데 영향과 리스크를 알려줘"
                                          → analyze_task_impact
```
Hero 흐름 결과 예시는 [`result/hero-demo-output.txt`](result/hero-demo-output.txt),
페르소나별 사용 여정은 [`result/usage-walkthrough.md`](result/usage-walkthrough.md) 참고.

---

## MCP 도구 (5) — 코어 함수 1:1

| 도구 | 설명 |
|---|---|
| `trace_analyze_project` | 프로젝트 스캔 → 기능 지식화 → 결정적 충돌 검출·저장 |
| `trace_list_features` | 식별된 Feature 요약 목록 |
| `trace_get_feature_knowledge` | 한 Feature의 지식(claims·confidence·conflicts·리소스 URI) |
| `trace_get_conflicts` | 검출된 문서/구현 충돌(근거·유형 포함) |
| `trace_analyze_task_impact` | 자연어 작업의 영향(Must/Likely/Review)·관련 충돌·순서형 Change Plan |

리소스: `trace://feature/<id>` (지식 본문 Markdown) · 프롬프트: `review_before_implementation` (구현 전 검토 유도).

## 폴백 CLI (`trace`) — MCP 없이도 동일 코어

```bash
trace analyze                       # 스캔·지식화·충돌검출 (LLM 사용 → 키 필요)
trace features                      # Feature 목록 (캐시/저장 지식)
trace knowledge owner-registration  # 한 Feature 지식
trace conflicts                     # 충돌 목록 (--feature <id> 로 한정)
trace impact "Add SMS verification to Owner registration"   # 영향 분석
trace conflicts --json              # 구조화(JSON) 출력
```
`analyze` 이후 `features/knowledge/conflicts`는 저장된 지식을 읽으므로 **키 없이** 동작합니다(캐시 폴백).

## 키 없이 결정적 데모

```bash
python demo/run_demo.py          # 결정적 재현 (API 키 불필요)
python demo/run_demo.py --live   # 실제 Claude 자동 검출 (ANTHROPIC_API_KEY 필요, 비결정적)
```
`demo/`는 spring-petclinic-rest 스타일의 **5개 도메인·약 48개 자산**(소스·스펙 PDF·스키마·설정·테스트)에
**의도적 충돌 9건**(값 불일치·정책 충돌·오래된 지식 각 3)을 심은 프로젝트다. 기본 모드는 스캔·파싱·
충돌검출·영향매핑을 실제 코드로 수행하고 LLM만 고정 응답으로 대체 → **매 실행 동일**. 충돌 목록은
[`demo/README.md`](demo/README.md)의 Ground Truth 표 참고.

---

## 아키텍처 (코어/인터페이스 분리, NFR-CORE-001)

```
스캔·파싱(engine) → 기능 식별·지식(workflow) → Claim/Evidence/충돌(conflict) → 작업 영향(impact)
                                   │
                          공통 Result envelope
                                   │
                 ┌─────────────────┴─────────────────┐
            MCP 서버(mcp_server, C1)            폴백 CLI(cli, C9)
```
- 충돌 검출·Confidence·영향 매핑은 **순수 함수** — 속성 기반 테스트(hypothesis)로 불변식 검증.
- LLM은 `LLMService` 뒤로 캡슐화(구조화 출력 검증·재시도), 테스트는 FakeLLM 주입(오프라인).

## 개발

```bash
pytest                  # 전체 테스트(실 API 불필요; 옵트인 통합은 기본 skip)
mypy                    # 타입 체크
```
실 API 통합 테스트: `TRACE_RUN_LLM_INTEGRATION=1` + 유효한 `ANTHROPIC_API_KEY`.

## 보안

- API 키는 **환경변수/.env**로만 주입, 소스·로그 비노출(late lookup, NFR-SEC-001/002).
- 생성 지식(`.trace/`)·`.env`는 `.gitignore` 대상. 로컬 stdio 단일 프로세스 — 원격 노출 없음.

## 설계 문서

`aidlc-docs/` — AI-DLC 단계별 산출물(요구사항→유저스토리→설계→NFR→코드). 용어는 `aidlc-docs/GLOSSARY.md`.

## 라이선스

MIT

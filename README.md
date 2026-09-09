# TRACE — Technical Relationship & Analysis for Change Evidence

> 흩어진 프로젝트 산출물(요구사항·OpenAPI·소스·DB·설정·테스트·문서)을 **Feature 단위 지식**으로 재구성하고,
> 문서와 구현이 **어긋난 지점(Conflict)을 근거와 함께** 드러내는 **로컬 MCP 서버**입니다.
> Claude Code 같은 AI 코딩 에이전트가 코드를 생성하기 **직전에** 호출해, stale spec 위에서 잘못된 코드를
> 자신 있게 만들어내는 것을 방지합니다.

<p align="center">
  <img src="docs/TRACE.png" alt="TRACE 개요 — Feature·Conflict·Impact·Evidence를 구현 직전에 근거와 함께 제공하는 MCP 지식 계층" width="720">
</p>

---

## 🎯 What — 어떤 문제를 푸는가

변경 티켓 하나("Owner 등록에 SMS 인증을 추가하라")를 받으면, 지금은 **요구사항 문서·OpenAPI·소스·DB
스키마·테스트를 각각 열어 사람이 직접 대조**해야 합니다. 그 과정에서:

- 정보가 **파일 단위로 흩어져** 있어 Feature 단위로 재구성되지 않고,
- 문서와 구현이 **서로 어긋나 있어도 아무도 모른 채** 개발이 진행되며 (예: 요구는 전화번호 20자, 코드·DB는 10자),
- **AI 에이전트는 그 Conflict를 모른 채** stale spec을 근거로 자신 있게 코드를 생성하고,
- 놓친 컴포넌트와 Conflict는 **구현을 마친 뒤에야** 드러나 재작업·장애로 이어집니다.

**TRACE는 구현에 착수하기 전에** *"이 작업과 무엇이 관련돼 있고, 무엇이 어긋나 있으며, 무엇을 먼저 검토·변경해야
하는가"* 를 **근거(Evidence)와 함께** tool call 결과로 제공합니다.

### 차별점 — 'Retrieval' vs 'Reconciliation'

| 구분 | RAG / Wiki / 코딩 어시스턴트 | **TRACE (MCP)** |
| --- | --- | --- |
| 데이터 단위 | 유사 chunk / 파일 / free text | **정규화된 Claim** (subject + predicate + value) |
| 응답 형태 | "관련 있어 보이는" 텍스트 | **Claim ↔ Evidence 링크 + cross-source 값 비교** |
| 불일치 처리 | 감지하지 못하고 요약만 | **Conflict(value_mismatch 등)를 first-class output으로 검출** |
| 신뢰 근거 | LLM의 self-confidence | **근거 일치도 기반 Confidence** |
| 소비 방식 | 사람이 채팅으로 질의 | **AI 에이전트가 구현 직전 MCP tool로 자동 질의** |

> RAG는 **'비슷한 것(retrieval)'**을 찾고, TRACE는 **'어긋난 것(reconciliation)'**을 찾습니다.
> 그리고 그 결과를 사람이 아니라 **코드 생성 직전의 AI 에이전트에게 직접 전달**합니다.
> 그래서 Conflict 검출은 LLM의 자체 판단이 아니라 **Evidence의 구조적 비교**로 이뤄져 —
> deterministic하고 reproducible합니다.

---

## 👥 Who · When — 세 가지 진입점

세 사용자 모두 **Claude Code 안에서** 자연어로 요청하고, 에이전트가 TRACE MCP tool을 호출합니다.
(아래 그림의 세 인물이 각 persona입니다.)

<p align="center">
  <img src="docs/TRACE_personas.png" alt="TRACE 세 페르소나 — 데브(Understand)·마이라(Maintain)·피엠(Plan Change)" width="720">
</p>

| Persona | 핵심 질문 | 언제 사용하는가 | 산출물 | 사용 도구 |
| --- | --- | --- | --- | --- |
| **데브 · Understand**<br/>(Developer) | *"어디를 바꿔야 하지?"* | 낯선 코드베이스에 처음 투입된 **첫 며칠**, 기능을 손대기 전마다 | 자산을 **Feature 단위로 재구성** + 근거 참조 → 빠른 온보딩 | `analyze_project` → `list_features` → `get_feature_knowledge` |
| **마이라 · Maintain**<br/>(Maintainer) | *"왜 이 문제가 생겼고, 무엇을 고쳐야 하지?"* | 운영 이슈·정책 불일치를 **조사할 때마다** | 어긋난 지점과 **양쪽 근거**, 함께 갱신해야 할 테스트·문서 | `get_conflicts` → `get_feature_knowledge` |
| **피엠 · Plan Change**<br/>(PM) | *"이 요구사항이 바뀌면 영향은 어디까지 번지지?"* | 새 요구사항·정책 변경을 **검토할 때**(착수 직전) | 영향 범위·리스크·**착수 전 결정 지점** + 우선순위화된 Change Plan | `analyze_task_impact` |

### 📖 Persona별 시나리오 — 실제 작업 화면 기록

각 페르소나가 업무를 성공적으로 수행하는 과정을 **자연어 요청 → 호출 tool → 실제 콘솔 출력 →
읽어낸 것/다음 행동** 순으로 기록했습니다. 아래 시나리오의 작업 화면은 **실제 Claude(Amazon
Bedrock, `global.anthropic.claude-opus-4-8`)로 라이브 실행**한 결과입니다.

| 시나리오 | 업무 | 결과(라이브 실행 증거) |
|---|---|---|
| [**데브 · Understand**](demo/scenario/dev/README.md) | 낯선 코드베이스 온보딩 | 48자산 → 6 Feature 재구성, `owner-registration`을 11자산·15 claim·근거와 함께 이해 |
| [**마이라 · Maintain**](demo/scenario/maira/README.md) | "세금(VAT)이 안 붙는다" 운영 이슈 조사 | 원인을 **설정 `disabled` + 코드 `absent`** 이중 드리프트로, 양쪽 근거·위치와 함께 지목 |
| [**피엠 · Plan Change**](demo/scenario/pm/README.md) | "Owner 등록에 SMS 인증 추가" 영향 검토 | 착수 전 충돌 6건 경고 + 영향 11건(Must/Likely/Review) + **충돌 선결 8단계 Change Plan** |

> 세 페르소나는 **동일한 코어 지식**을 각자의 진입점(MCP tool)에서 소비합니다. 세 명 요약 여정은
> [`result/usage-walkthrough.md`](result/usage-walkthrough.md), API 키 없는 결정적 전체 출력은
> [`result/hero-demo-output.txt`](result/hero-demo-output.txt)를 참고하세요.

---

## 🚀 How — Quick Start

### 1) 설치
```bash
python -m venv .venv
source .venv/Scripts/activate        # Windows(Git Bash) / macOS·Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

### 2) 백엔드·API 키 (커밋 금지 — 환경변수 / `.env`)
```bash
cp .env.example .env
```
두 백엔드를 지원합니다(`TRACE_LLM_PROVIDER`로 선택):
- **Anthropic 1st-party** (기본): `ANTHROPIC_API_KEY=sk-ant-...`
- **Amazon Bedrock**: `TRACE_LLM_PROVIDER=bedrock` + AWS 자격증명(또는 `AWS_BEARER_TOKEN_BEDROCK`
  단일 토큰) + `AWS_REGION` + `TRACE_LLM_MODEL=<Bedrock 모델 ID>`
  (예: `global.anthropic.claude-opus-4-8`). Bedrock extra 설치: `pip install -e ".[bedrock]"`.

> 키·자격증명 값은 **소스·설정·저장소에 평문 저장하지 않습니다**(late lookup, NFR-SEC-001/002).
> `.env`는 `.gitignore` 대상입니다.

### 3) Claude Code에 연결 — `.mcp.json`
분석할 프로젝트 루트(`cwd`)에 아래 `.mcp.json`을 두면 Claude Code가 stdio로 TRACE를 실행합니다.
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
> `command`는 `pip install` 후 등록되는 console script입니다. `TRACE_PROJECT_ROOT`를 지정하지 않으면 실행 디렉터리를 분석합니다.

### 4) Hero 시나리오 프롬프트 (Claude Code)
```
1. "이 프로젝트를 분석해줘"                                    → analyze_project
2. "발견된 문서/구현 Conflict를 보여줘"                        → get_conflicts
3. "Owner 등록에 SMS 인증을 추가하려는데 영향과 리스크를 알려줘"  → analyze_task_impact
```
Hero 흐름 결과 예시는 [`result/hero-demo-output.txt`](result/hero-demo-output.txt)를 참고하세요.

### API 키 없이 바로 체험 — Deterministic Demo
```bash
python demo/run_demo.py                     # 결정적 재현 (API 키 불필요, 매 실행 동일)
python demo/run_demo.py --live              # 실제 Claude로 자동 검출 (키 필요, 비결정적)
python demo/tools/extract_features_live.py  # demo/를 실제 LLM으로 지식화 → demo/.trace/에 저장
python demo/scenario/dev/capture_dev_scenario.py  # 데브 여정 결정적 캡처(API 키 불필요)
```
`demo/`는 spring-petclinic-rest 스타일의 **5개 도메인·약 48개 자산**(소스·spec PDF·스키마·설정·테스트)에
**의도적 Conflict 9건**(value_mismatch·policy_conflict·stale_knowledge 각 3)을 심은 프로젝트입니다.
기본 모드는 스캔·파싱·Conflict 검출·Impact 매핑을 **실제 코드로 수행**하고 LLM만 고정 응답으로 대체하므로
**매 실행 결과가 동일**합니다. 전체 Conflict 목록은 [`demo/README.md`](demo/README.md)의 Ground Truth 표를 참고하세요.

> **실행 증거**: 위 커맨드의 실제 콘솔 출력을 [`demo/scenario/`](demo/scenario/)(페르소나별 라이브 화면)와
> [`result/hero-demo-output.txt`](result/hero-demo-output.txt)(결정적 전체 흐름)에 그대로 담았습니다.
> 스크린샷 대신 **재현 가능한 텍스트 트랜스크립트**로 제공하므로, 같은 명령으로 직접 확인할 수 있습니다.

### 문제가 생기면 — Troubleshooting
- `환경변수 ANTHROPIC_API_KEY 가 설정되지 않았습니다` → `.env`에 키를 넣거나 셸에 export. (결정적
  데모는 키 없이 동작합니다.)
- Bedrock `The provided model identifier is invalid` / `not authorized` → `TRACE_LLM_MODEL`을 해당
  리전에서 접근 가능한 Bedrock 모델 ID/inference profile로 지정(리전에 따라 `us.`/`global.` 접두 필요).
- `analyze` 이후 `features`/`knowledge`/`conflicts`가 비어 있음 → 먼저 `trace analyze`(또는
  `analyze_project`)로 지식을 생성해야 합니다(이후 조회는 키 없이 저장 지식을 읽음).

---

## 🧰 MCP Tools (5) — core 함수와 1:1

| Tool | 설명 |
|---|---|
| `trace_analyze_project` | 프로젝트 스캔 → Feature 지식화 → deterministic Conflict 검출·저장 |
| `trace_list_features` | 식별된 Feature 요약 목록 |
| `trace_get_feature_knowledge` | 한 Feature의 지식(claims · confidence · conflicts · resource URI) |
| `trace_get_conflicts` | 검출된 문서/구현 Conflict(근거·유형 포함) |
| `trace_analyze_task_impact` | 자연어 작업의 Impact(Must / Likely / Review) · 관련 Conflict · 우선순위화된 Change Plan |

Resource: `trace://feature/<id>` (지식 본문 Markdown) · Prompt: `review_before_implementation` (구현 전 검토 유도).

### Fallback CLI (`trace`) — MCP 없이도 동일한 core

```bash
trace analyze                       # 스캔·지식화·Conflict 검출 (LLM 사용 → API 키 필요)
trace features                      # Feature 목록 (캐시/저장 지식)
trace knowledge owner-registration  # 한 Feature 지식
trace conflicts                     # Conflict 목록 (--feature <id> 로 한정)
trace impact "Add SMS verification to Owner registration"   # Impact 분석
trace conflicts --json              # 구조화(JSON) 출력
```
`analyze` 이후 `features` / `knowledge` / `conflicts`는 저장된 지식을 읽으므로 **API 키 없이** 동작합니다(cache fallback).

---

## 🏗 아키텍처 — core / interface 분리 (NFR-CORE-001)

```
스캔·파싱(engine) → Feature 식별·지식(workflow) → Claim / Evidence / Conflict → Impact 분석(impact)
                                   │
                          공통 Result envelope
                                   │
                 ┌─────────────────┴─────────────────┐
            MCP Server(mcp_server, C1)          Fallback CLI(cli, C9)
```
- Conflict 검출 · Confidence · Impact 매핑은 **pure function** — property-based testing(hypothesis)으로 invariant를 검증합니다.
- LLM 호출은 `LLMService`로 캡슐화(structured output 검증·재시도)하고, 테스트는 FakeLLM을 주입해 오프라인으로 동작합니다.

## 🔧 개발 · 품질

```bash
pytest                  # 전체 테스트 (실제 API 불필요; opt-in 통합 테스트는 기본 skip)
mypy                    # 타입 체크 (전 패키지 clean)
```
- **완성도**: 진입점(MCP tool / CLI)부터 실제 구현까지 호출이 닿으며, 위 데모·시나리오로 E2E 동작을
  확인할 수 있습니다. 핵심 로직은 property-based testing(hypothesis)으로 invariant를 검증합니다.
- **에러 핸들링**: 경계(tool/CLI)에서 예외를 `Result`로 강등하고(`error_to_result`), Feature 단위
  실패는 warning으로 격리해 전체 흐름을 계속합니다. 경로 트래버설·손상 파일은 방어적으로 skip합니다.
- 실제 API 통합 테스트: `TRACE_RUN_LLM_INTEGRATION=1` + 유효한 자격증명(opt-in, 기본 skip).

## 🔒 유지보수성 · 보안

- **시크릿 관리**: 키·자격증명은 **환경변수 / `.env`**로만 주입하며 소스·로그·저장소에 평문으로 두지
  않습니다 (late lookup, NFR-SEC-001/002). 생성 지식(`.trace/`)과 `.env`는 `.gitignore` 대상입니다.
- **입력 검증·격리**: 프로젝트 경로 검증(트래버설 차단), LLM structured output 스키마 검증·재시도,
  손상/누락 자산 skip. 로컬 stdio 단일 프로세스라 원격 노출이 없습니다.
- **구조·모듈화**: core(engine/workflow/conflict/impact) ↔ interface(mcp_server/cli)를 분리하고
  설정을 `config/`로 외부화 — 후속 개발자가 백엔드(anthropic/bedrock)나 tool을 확장하기 쉽습니다.
- **관측 가능성**: 구조적 로깅(`event=...`)으로 스캔·지식화·충돌 검출 단계를 추적합니다.

## 📚 설계 문서 · AI-DLC 과정

- `aidlc-docs/` — AI-DLC 단계별 산출물(Requirements → User Stories → Design → NFR → Code)이 서로
  이어지도록 축적돼 있습니다. 용어 정의는 [`aidlc-docs/GLOSSARY.md`](aidlc-docs/GLOSSARY.md),
  진행 상태는 [`aidlc-docs/aidlc-state.md`](aidlc-docs/aidlc-state.md).
- **개발 과정 증거**: 각 단계 결정이 다음 단계로 이어진 흐름이 **git 커밋 이력**(`[AI-DLC:<Phase>/<Stage>] …`)에
  그대로 남아 있어, 요구사항→설계→코드→데모→시나리오로 이어지는 근거를 추적할 수 있습니다.

## License

MIT

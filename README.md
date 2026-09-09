# TRACE — 개발자 지식 인텔리전스

**흩어진 개발 자산(요구사항·API 명세·소스·DB·설정·테스트·PDF)을 기능(Feature) 중심·근거 기반
지식으로 재구성하고, 코드를 짜기 전에 "어긋난 것(충돌)"과 영향 범위를 근거와 함께 알려주는
로컬 MCP 서버입니다.**

RAG류 도구가 "비슷한 것"을 검색하는 것과 달리, TRACE는 자산에서 정규화된
**Claim(`subject.predicate = value`)** 을 뽑아 **같은 주장에 붙은 서로 다른 값**을
`value_mismatch` 충돌로 **결정적으로 검출**합니다. 이 판정은 LLM이 아니라 순수 함수라 재현됩니다.

---

## 누구의 어떤 문제를 푸나

기능 하나를 건드리려면 요구사항 문서, API 스펙, 코드, DB 스키마, 테스트가 서로 맞는지 일일이
대조해야 합니다. 문서는 "전화번호 최대 20자"라는데 코드·스키마는 10자라면, 보통 **구현을 하다가**
뒤늦게 발견합니다. TRACE는 착수 직전에 이 불일치를 근거(어느 파일의 어느 위치)와 함께 경고합니다.

---

## 처음이신가요? — 터미널·코딩 경험 없이 따라하기

**아래 6단계만 그대로 따라 하면 API 키 없이 데모가 돌아갑니다.** 명령어는 복사해서 붙여넣으면 됩니다.

> 💡 **알아두기**: "터미널"은 컴퓨터에 글자로 명령을 내리는 검은 창입니다. 아래 회색 상자 안의 글자를
> 복사(`Ctrl+C`)해서 터미널에 붙여넣고(`Ctrl+V` 또는 마우스 오른쪽 클릭) `Enter`를 누르면 실행됩니다.

### 준비물

- **컴퓨터** (Windows 10/11 또는 macOS)
- **Python 3.10 이상** — 프로그램을 실행하는 도구 (아래 2단계에서 설치)
- **API 키·계정은 필요 없습니다.** 데모는 미리 저장해 둔 응답을 재생하므로 인터넷·결제·로그인이 전부 불필요합니다.

### 1단계 — 터미널(명령 창) 열기

- **Windows**: 화면 왼쪽 아래 시작 버튼 → `PowerShell` 이라고 검색 → **Windows PowerShell** 클릭
- **macOS**: `⌘(Command) + Space` → `터미널` 또는 `Terminal` 입력 → `Enter`

### 2단계 — Python이 있는지 확인 (없으면 설치)

터미널에 아래를 입력하고 `Enter`:

```bash
python --version
```

`Python 3.10.x` 이상이 보이면 통과입니다. (macOS에서 안 되면 `python3 --version`으로 다시 시도)

숫자가 안 나오거나 오류가 나면 아직 없는 것입니다. [python.org/downloads](https://www.python.org/downloads/) 에서
설치 파일을 받아 실행하세요.

> ⚠️ **Windows 설치 시 중요**: 설치 첫 화면 맨 아래 **"Add Python to PATH"** 체크박스를 꼭 켠 뒤 설치하세요.
> 이걸 놓치면 터미널이 python을 찾지 못합니다. (놓쳤다면 파이썬을 다시 설치하며 체크하면 됩니다.)

### 3단계 — 이 프로젝트 내려받기

**방법 A (간단)**: [GitHub 저장소](https://github.com/lkwoo/ddthon26-trace)에서 초록색
**`Code` 버튼 → `Download ZIP`** → 내려받은 zip을 더블클릭해 압축을 풀면 `ddthon26-trace` 폴더가 생깁니다.

**방법 B (git이 있다면)**:

```bash
git clone https://github.com/lkwoo/ddthon26-trace.git
```

### 4단계 — 프로젝트 폴더로 이동

`cd`는 "이 폴더로 들어가라"는 뜻입니다. `cd ` 까지만 입력하고 **폴더를 터미널 창으로 끌어다 놓으면**
경로가 자동으로 채워집니다. `Enter`를 누르세요.

```bash
cd 프로젝트폴더경로/ddthon26-trace
```

### 5단계 — 설치 (한 번만)

```bash
pip install -e .
```

> `pip`이 없다는 오류가 나면 `python -m pip install -e .` (macOS는 `python3 -m pip install -e .`)로 시도하세요.
> 필요한 부품(라이브러리)을 자동으로 내려받으므로 처음엔 1~2분 걸릴 수 있습니다.

### 6단계 — 데모 실행

아래 **OS에 맞는 상자**를 통째로 복사해 붙여넣고 `Enter` 하세요.

**macOS / Linux (터미널)**

```bash
export TRACE_LLM_BACKEND=replay
export TRACE_REPLAY_DIR="$PWD/demo/replay"

trace analyze-project ./demo --refresh    # 프로젝트를 스캔·분석
trace conflicts                           # ⚠️ 문서와 코드가 어긋난 부분을 근거와 함께 표시
trace map ./demo --refresh                # 신입 온보딩 맵 생성
```

**Windows (PowerShell)** — Windows는 `export` 대신 `$env:`를 씁니다:

```powershell
$env:TRACE_LLM_BACKEND="replay"
$env:TRACE_REPLAY_DIR="$PWD\demo\replay"

trace analyze-project ./demo --refresh
trace conflicts
trace map ./demo --refresh
```

`trace conflicts`에서 `Owner.telephone.max_length: 20(PDF) vs 10(코드/명세)` 같은 경고가 뜨면 성공입니다.
막히면 맨 아래 [트러블슈팅](#트러블슈팅)을 참고하세요.

---

## API 키로 내 프로젝트 분석하기 (live 모드) — 이게 실제 사용법입니다

위 데모는 미리 저장해 둔 응답을 재생하는 것이라 **동봉된 `demo/` 폴더에만** 동작합니다.
**여러분의 진짜 프로젝트**를 분석하려면 Claude API 키를 넣고 `live` 모드로 실행하세요.

### 1단계 — Claude API 키 발급받기

1. [console.anthropic.com](https://console.anthropic.com) 에 로그인 (없으면 가입)
2. 왼쪽 메뉴 **API Keys → Create Key** → 만들어진 `sk-ant-...` 문자열을 복사

> 🔐 이 키는 **비밀번호**입니다. 남에게 보여주거나, 코드·깃(GitHub)에 넣지 마세요. 사용량만큼 요금이 부과됩니다.

### 2단계 — 키를 `.env` 파일에 저장 (권장, 가장 안전)

터미널에 키를 직접 치면 명령 기록에 남습니다. 대신 프로젝트 폴더의 **`.env` 파일**에 넣으면 TRACE가
자동으로 읽고, 이 파일은 깃에 커밋되지 않습니다.

1. `ddthon26-trace` 폴더 안의 **`.env.example`** 파일을 복사해 이름을 **`.env`** 로 바꿉니다.
   (메모장·텍스트 편집기로 열어 "다른 이름으로 저장" 해도 됩니다.)
2. `.env` 를 열어 아래 두 줄을 이렇게 고칩니다:

```bash
TRACE_LLM_BACKEND=live
ANTHROPIC_API_KEY=sk-ant-...        # 1단계에서 복사한 실제 키로 교체
```

3. 저장한 뒤 분석을 실행합니다 (환경변수 설정 없이 바로 됩니다):

```bash
trace analyze-project ./분석할/프로젝트/경로 --refresh
trace conflicts
trace map ./분석할/프로젝트/경로 --refresh
```

> `./분석할/프로젝트/경로` 자리에 실제 분석 대상 폴더를 넣으세요. `cd `를 친 뒤 폴더를 터미널로
> 끌어다 놓으면 경로가 자동으로 채워집니다. 지금 폴더를 분석하려면 그냥 `.` 을 쓰면 됩니다.

### 2단계 (대안) — 파일 대신 환경변수로 넣기

`.env`를 만들지 않고 그때그때 넣어도 됩니다.

**macOS / Linux (터미널)**

```bash
export TRACE_LLM_BACKEND=live
export ANTHROPIC_API_KEY=sk-ant-...        # 발급받은 키
export TRACE_LLM_MODEL=claude-sonnet-5     # (선택) 기본값이라 생략 가능

trace analyze-project ./분석할/프로젝트/경로 --refresh
trace conflicts
```

**Windows (PowerShell)**

```powershell
$env:TRACE_LLM_BACKEND="live"
$env:ANTHROPIC_API_KEY="sk-ant-..."
$env:TRACE_LLM_MODEL="claude-sonnet-5"

trace analyze-project ./분석할/프로젝트/경로 --refresh
trace conflicts
```

> 이렇게 넣은 값은 **터미널 창을 닫으면 사라집니다.** 창을 다시 열면 다시 넣어야 하므로,
> 계속 쓸 거라면 위 `.env` 파일 방식을 권합니다.

### Amazon Bedrock을 쓰는 경우

회사 AWS 계정 등으로 Bedrock을 통해 Claude를 쓴다면 `sk-ant` 키 대신 Bedrock API 키(bearer 토큰, `ABSK...`)를 씁니다:

```bash
TRACE_LLM_BACKEND=bedrock
AWS_BEARER_TOKEN_BEDROCK=ABSK...
AWS_REGION=ap-northeast-2
TRACE_BEDROCK_MODEL=apac.anthropic.claude-sonnet-4-5-20250929-v1:0   # 리전 접두사(us./eu./apac.)를 맞추세요
```

> IAM 사용자에 `bedrock:InvokeModel` 권한이 있고, Bedrock 콘솔에서 해당 모델 액세스가 활성화돼 있어야 합니다.

---

## 30초 데모 (API 키 불필요)

> 터미널이 익숙하다면 이 섹션으로 바로 시작하세요. 처음이라면 위
> [처음이신가요?](#처음이신가요--터미널코딩-경험-없이-따라하기) 6단계를 따라 하면 됩니다.
> (아래 명령은 macOS/Linux 기준이며, Windows PowerShell은 `export`를 `$env:`로 바꿔 씁니다.)

TRACE는 사전 캐시된 응답을 재생하는 **replay 백엔드**를 내장해, API 키 없이도 Hero 시나리오를
결정적으로 재현합니다. 동봉된 `demo/`(Spring Petclinic 조각 + 의도적 충돌)로 바로 확인하세요.

```bash
pip install -e .

export TRACE_LLM_BACKEND=replay
export TRACE_REPLAY_DIR="$PWD/demo/replay"
export TRACE_HOME="$PWD/.trace-demo"   # 지식 저장 위치 (선택)

trace analyze-project ./demo --refresh   # 스캔→Feature→Claim→충돌→영속화
trace list-features
trace conflicts                          # ⚠️ Owner.telephone.max_length: 20(PDF) vs 10(코드/명세)
trace analyze-task "Add SMS verification to Owner registration"
trace map ./demo --refresh               # 신입 온보딩 맵: 진입점·의존 그래프·Feature→파일·Mermaid
```

> **처음 보는 프로젝트라면** `trace map <경로>`부터. 진입점(예: `@RestController`), 파일 의존
> 그래프, Feature→파일 매핑, 핵심 흐름을 근거와 함께 요약하고 Mermaid 다이어그램이 포함된
> `.trace/knowledge/overview.md`를 남깁니다.

실제 실행 전사는 [`result/hero-run.txt`](result/hero-run.txt)(Hero)·
[`result/onboarding-map-run.txt`](result/onboarding-map-run.txt)(온보딩 맵)에 있고,
시연 스크린샷은 [`screenshots/`](screenshots/)에 있습니다 — Hero(`01`~`03`, live Bedrock)와
온보딩 맵(`04`~`05`, replay). 자세한 설명은 [`screenshots/README.md`](screenshots/README.md).

---

## Claude Code에 MCP 서버로 연결

[Claude Code](https://claude.com/claude-code)는 터미널에서 AI(Claude)와 대화하며 코드를 다루는 도구입니다.
TRACE를 여기에 연결하면 아래처럼 **한국어로 말만 하면** TRACE 도구가 자동으로 실행됩니다.
프로젝트 루트에 `.mcp.json` 파일을 만들면 됩니다. (동봉된 `.mcp.json.example`을 복사해 값을 채우면 편합니다.)

```json
{
  "mcpServers": {
    "trace": {
      "command": "trace-mcp",
      "env": {
        "TRACE_LLM_BACKEND": "live",
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "TRACE_LLM_MODEL": "claude-sonnet-5"
      }
    }
  }
}
```

> 데모를 그대로 재현하려면 `"TRACE_LLM_BACKEND": "replay"`, `"TRACE_REPLAY_DIR": "<repo>/demo/replay"`로
> 두면 키 없이 동작합니다. `ANTHROPIC_API_KEY`는 **환경변수로만** 주입하고 코드/저장소에 넣지 마세요.

### Claude Code에서 이렇게 말해보세요

- "이 프로젝트를 분석해줘" → `analyze_project`
- "Owner 등록 기능에 대해 알려줘" → `get_feature_knowledge`
- "충돌 있어?" → `get_conflicts`
- "Owner 등록에 SMS 인증 추가하려는데 어디를 바꿔야 해?" → `analyze_task_impact`
- "이 프로젝트 처음인데 어디부터 봐야 해?" → `generate_onboarding_map`

노출되는 MCP 도구/리소스:

| 도구 | 하는 일 |
|---|---|
| `analyze_project(path, refresh)` | 스캔·분석해 Feature 지식·충돌 생성(1회) |
| `list_features()` | 검출된 Feature 요약 |
| `get_feature_knowledge(feature_id)` | 단일 Feature 지식 상세 |
| `get_conflicts(feature_id?)` | value_mismatch 등 충돌 목록 |
| `analyze_task_impact(task, feature_id?)` | 착수 전 Must/Likely/Review + Change Plan |
| `generate_onboarding_map(path, feature_id?, refresh?)` | 진입점·의존 그래프·Feature→파일·Mermaid 온보딩 맵 |

리소스: `trace://features`(인덱스), `trace://feature/{id}`(지식 문서 MD+YAML), `trace://overview`(온보딩 맵).

---

## 동작 방식

```
스캔·파싱(로컬)         Feature 검출        Claim/Evidence 추출      결정적 충돌 검출
 assets ─────────▶ identify_features ─▶ extract_claims ────────▶ detect_conflicts
 (UOW-01)            (LLM)               (LLM)                    (순수 함수, UOW-03)
                         │                                            │
                         ▼                                            ▼
                 generate_knowledge ───▶ .trace/knowledge/features/<id>.md (MD+YAML)
                                                      │
                                       analyze_task_impact (착수 전 영향, UOW-04)
```

- **LLM 백엔드 2종**: `live`(실제 Claude) / `replay`(사전 응답 재생, 키 없이 결정적 재현).
- **충돌·신뢰도는 결정적 코드**: LLM은 추출까지만. 판정은 재현 가능(NFR-AI-004).
- **로컬 우선**: 파일시스템 접근은 엔진에 국한, 산출물은 대상 프로젝트 `.trace/`에 저장.

---

## 설정 (환경변수)

`.env.example`를 복사해 `.env`로 두거나 환경변수로 지정합니다. `.env`는 `.gitignore` 처리됩니다.

MCP 클라이언트(Claude Code 등)에 TRACE 서버를 등록하려면 `.mcp.json.example`을 `.mcp.json`으로 복사해 값을 채웁니다. `.mcp.json`은 실제 시크릿(Bedrock bearer 토큰 등)을 담으므로 `.env`와 마찬가지로 `.gitignore` 처리됩니다.

| 변수 | 기본 | 설명 |
|---|---|---|
| `TRACE_LLM_BACKEND` | `replay` | `live` 또는 `replay` |
| `ANTHROPIC_API_KEY` | — | `live`에서만 필요 (환경변수로만) |
| `TRACE_LLM_MODEL` | `claude-sonnet-5` | live 모델 |
| `TRACE_REPLAY_DIR` | — | replay 픽스처 디렉터리 |
| `TRACE_HOME` | 현재 디렉터리 | 지식 저장 루트(`.trace/`) |
| `TRACE_LOG_LEVEL` | `INFO` | 로그 레벨(로그는 stderr로만) |

---

## 개발 / 테스트

```bash
pip install -e .[dev]
pytest            # 단위 + Hypothesis 속성 + 통합 (replay로 오프라인 전부 통과)
```

---

## 트러블슈팅

- **`replay 픽스처 없음`**: `TRACE_REPLAY_DIR`가 `demo/replay`를 가리키는지 확인하거나
  `TRACE_LLM_BACKEND=live` + `ANTHROPIC_API_KEY`로 실행하세요.
- **`분석된 지식이 없습니다`**: `analyze_project`(또는 `trace analyze-project`)를 먼저 실행하세요.
- **`live LLM 백엔드에 ANTHROPIC_API_KEY가 필요합니다`**: 키를 환경변수로 설정하거나 replay로 실행.
- **Claude Code가 도구를 못 봄**: `.mcp.json`의 `command`(`trace-mcp`)가 PATH에 있는지(`pip install -e .`) 확인.

---

## 라이선스 / 상태

해커톤 산출물. AI-DLC 워크플로우로 설계·구현되었으며 전 과정이 git 이력에 남아 있습니다
(`aidlc-docs/` 참조).

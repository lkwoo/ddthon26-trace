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

## 30초 데모 (API 키 불필요)

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

프로젝트 루트에 `.mcp.json`을 만들면 Claude Code가 TRACE 도구를 사용합니다.

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

# 실행 증거 (result/)

TRACE가 실제로 동작함을 보여주는 산출물입니다.

## `hero-run.txt` — Hero 시나리오 CLI 전사

`demo/` 데이터셋에 대해 replay 백엔드로(**API 키 없이**) 다음 흐름을 실행한 실제 출력입니다:

1. `trace analyze-project ./demo --refresh` — 자산 스캔 → Feature 검출 → Claim/근거 추출 →
   충돌 검출 → 지식 영속화.
2. `trace list-features` — 검출된 Feature(Owner Registration).
3. `trace conflicts` — **value_mismatch** 검출: `Owner.telephone.max_length`
   = 20(요구 PDF) vs 10(OpenAPI·SQL·Java), 각 값의 근거 소스 인용.
4. `trace analyze-task "Add SMS verification to Owner registration"` — 착수 전 영향:
   Must/Likely/Review 파일 + 관련 충돌 경고 + 순서형 Change Plan.

재현:

```bash
pip install -e .
export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR="$PWD/demo/replay" TRACE_HOME="$PWD/.trace-demo"
trace analyze-project ./demo --refresh && trace conflicts \
  && trace analyze-task "Add SMS verification to Owner registration"
```

## Claude Code GUI 스크린샷 (권장 추가)

MCP 서버(`trace-mcp`)를 Claude Code에 연결한 화면 캡처는 사용자의 실제 클라이언트가 필요하므로
이 저장소에는 포함하지 않았습니다. README의 `.mcp.json` 스니펫으로 연결한 뒤,
"이 프로젝트 분석해줘 → 충돌 있어? → SMS 인증 추가하려면 어디 바꿔야 해?" 대화를 캡처해
이 디렉터리에 `screenshots/`로 추가하면 됩니다. CLI 전사(`hero-run.txt`)는 동일 코어 함수를
호출하므로 기능 동작의 증거로 충분합니다.

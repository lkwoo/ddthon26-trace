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

## `hero-run-live-opus48.txt` — live 전사 (Bedrock Opus 4.8)

replay가 아니라 **실제 Claude 호출**(Amazon Bedrock · `global.anthropic.claude-opus-4-8`,
리전 `ap-northeast-2`)로 동일 Hero 흐름을 실행한 전사입니다. 실제 모델도 value_mismatch를
검출하고 충돌을 인지한 Change Plan을 생성함을 보여줍니다.

## `onboarding-map-run.txt` — 온보딩 맵 CLI 전사 (신규 기능, replay)

낯선 프로젝트에 처음 앉은 신입 관점의 온보딩 맵 생성 전사입니다:

1. `trace analyze-project ./demo --refresh` — 맵의 Feature→파일 매핑 근거가 될 지식 적재.
2. `trace map ./demo --refresh` — **진입점**(OwnerRestController REST·엔드포인트) 검출,
   **파일 의존 17건·함수 호출 24건** 그래프, **Feature→파일** 매핑, 근거 인용 **내러티브**
   (telephone 값 불일치를 저신뢰로 표기), `.trace/knowledge/overview.md` 저장.
3. `trace map ./demo` — 2회차 **캐시 재사용**(정적 추출·LLM 생략).

## `overview-shot.txt` / `overview-excerpt.txt` — 생성된 overview.md

`trace map` 이 저장한 온보딩 맵 파일입니다. 내러티브 + 진입점 + **임베드 Mermaid**
(`flowchart LR` 의존 그래프 · `sequenceDiagram` 핵심 흐름) + Feature→파일 매핑을 담습니다.
`overview-shot.txt` 는 스크린샷용 발췌, `overview-excerpt.txt` 는 전체 본문 발췌입니다.

## 시연 스크린샷 → `../screenshots/`

터미널 화면을 PNG로 렌더링해 저장소 루트 `screenshots/` 에 두었습니다
(`01-analyze-project.png`, `02-conflicts.png`, `03-analyze-task.png` = live Hero,
`04-onboarding-map.png`, `05-overview-mermaid.png` = replay 온보딩 맵). 렌더러는
`render_screenshot.py`, 상세 설명은 `screenshots/README.md` 참조.

### Claude Code GUI 캡처(선택)

MCP 서버(`trace-mcp`)를 Claude Code에 연결한 GUI 캡처는 사용자의 실제 클라이언트가 필요합니다.
README의 `.mcp.json` 스니펫으로 연결한 뒤 "이 프로젝트 분석해줘 → 충돌 있어? →
SMS 인증 추가하려면 어디 바꿔야 해?" 대화를 캡처하면 됩니다. 위 CLI 스크린샷·전사가 동일
코어 함수를 호출하므로 기능 동작 증거로는 이미 충분합니다.

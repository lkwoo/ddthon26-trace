# 시연 스크린샷 (screenshots/)

`demo/` 데이터셋(Spring Petclinic REST + 합성 충돌 문서)에 대해 TRACE CLI를 실제 실행한 화면입니다.
1~3번은 **live 백엔드(Amazon Bedrock · Claude Opus 4.8, 리전 `ap-northeast-2`)** — 로그의
`model=global.anthropic.claude-opus-4-8` 이 실제 모델 호출 증거입니다. 4~5번(온보딩 맵)은
**replay 백엔드**로 API 키 없이 결정적으로 재현한 화면입니다.

| # | 파일 | 백엔드 | 화면 | 무엇을 보여주는가 |
|---|---|---|---|---|
| 1 | `01-analyze-project.png` | live | `trace analyze-project ./demo --refresh` | 자산 스캔 → Feature 2개 자동 검출 → Claim/근거 추출 → 충돌 보강 → Feature 지식 영속화까지 파이프라인이 끝까지 동작 |
| 2 | `02-conflicts.png` | live | `trace conflicts` | 구조적 차별점 — `Owner.telephone.max_length` 의 **value_mismatch**: 코드/DB/OpenAPI/테스트=**10** vs 요구 PDF=**20**, 각 값의 근거 소스를 인용 |
| 3 | `03-analyze-task.png` | live | `trace analyze-task "Add SMS verification to Owner registration"` | 착수 전 영향 분석 — 반드시 변경/변경 가능/검토 파일 분류 + **관련 충돌 경고** + 순서형 Change Plan(2단계에서 "코드=10 vs 명세=20 충돌부터 해소" 명시) |
| 4 | `04-onboarding-map.png` | replay | `trace map ./demo --refresh` | **신규 온보딩 맵** — 진입점(OwnerRestController REST·엔드포인트) 검출, Feature→파일 매핑, 파일 의존 17건·함수 호출 24건 그래프, 근거 인용 내러티브(telephone 저신뢰 경고 포함), 2회차 `overview.md` **캐시 재사용** |
| 5 | `05-overview-mermaid.png` | replay | `.trace/knowledge/overview.md` | 저장된 온보딩 맵 파일 — 내러티브 + 진입점 + **임베드 Mermaid**(`flowchart LR` 의존 그래프 · `sequenceDiagram` 핵심 흐름) + Feature→파일. GitHub·IDE에서 그대로 렌더 |

## 재현 방법

### live (실제 Claude 호출, 위 스크린샷과 동일 경로)

```bash
pip install -e .
cp .env.example .env          # 편집: TRACE_LLM_BACKEND=bedrock
# .env 에 AWS_BEARER_TOKEN_BEDROCK, AWS_REGION=ap-northeast-2,
#          TRACE_BEDROCK_MODEL=global.anthropic.claude-opus-4-8 설정
trace analyze-project ./demo --refresh
trace conflicts
trace analyze-task "Add SMS verification to Owner registration"
```

### replay (API 키 없이 결정적 재현 — 4~5번 온보딩 맵 포함)

```bash
export TRACE_LLM_BACKEND=replay TRACE_REPLAY_DIR="$PWD/demo/replay"
trace analyze-project ./demo --refresh && trace conflicts
trace map ./demo --refresh    # 온보딩 맵 생성 → .trace/knowledge/overview.md
trace map ./demo              # 2회차: 캐시 재사용
```

## 스크린샷 렌더링

이 PNG들은 위 명령의 실제 터미널 출력을 `result/render_screenshot.py`(PIL 기반, 한글
모노스페이스 폰트)로 터미널 창 스타일로 렌더링한 것입니다. 원본 전사는
`result/hero-run-live-opus48.txt`(live)·`result/hero-run.txt`(replay Hero)·
`result/onboarding-map-run.txt`(replay 온보딩 맵)·`result/overview-shot.txt`(overview.md 발췌)에 있습니다.

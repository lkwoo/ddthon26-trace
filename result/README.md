# result/ — 시연 증거 인덱스

TRACE의 실행 증거(스크린샷·페르소나 시나리오·콘솔 트랜스크립트)를 한곳에서 찾도록 안내합니다.
원본은 각 위치에 두고(단일 출처), 여기서는 **링크로 인덱싱**합니다.

## 🖼 시연 스크린샷 — [`screenshots/`](../screenshots/)

실제 tool 출력을 터미널 화면으로 렌더링한 이미지입니다(`python demo/tools/render_screens.py`로 재생성).

| 이미지 | 페르소나 · tool |
|---|---|
| [`dev-owner-knowledge.png`](../screenshots/dev-owner-knowledge.png) | 데브 · `get_feature_knowledge(owner-registration)` — claims·conflicts·근거 |
| [`maira-tax-rootcause.png`](../screenshots/maira-tax-rootcause.png) | 마이라 · `get_conflicts` — 세금 미적용 근본 원인(설정 disabled + 코드 absent) |
| [`pm-impact-plan.png`](../screenshots/pm-impact-plan.png) | 피엠 · `analyze_task_impact` — 충돌 경고 + Must/Likely/Review + Change Plan |

## 📖 페르소나 시나리오 — [`demo/scenario/`](../demo/scenario/)

각 페르소나가 업무를 수행하는 과정을 **자연어 요청 → tool → 실제 콘솔 출력 → 읽어낸 것** 순으로
기록했습니다(작업 화면은 실제 Bedrock opus 라이브 실행 결과).

| 시나리오 | 업무 |
|---|---|
| [데브 · Understand](../demo/scenario/dev/README.md) | 낯선 코드베이스 온보딩 — 48자산 → 6 Feature 재구성 |
| [마이라 · Maintain](../demo/scenario/maira/README.md) | "세금(VAT)이 안 붙는다" 운영 이슈 근본 원인 조사 |
| [피엠 · Plan Change](../demo/scenario/pm/README.md) | "Owner 등록에 SMS 인증 추가" 변경 영향 검토 |

## 📄 콘솔 트랜스크립트

| 파일 | 내용 |
|---|---|
| [`hero-demo-output.txt`](hero-demo-output.txt) | `python demo/run_demo.py`의 **실제 콘솔 출력**(무키·결정적). analyze_project→list_features→get_conflicts→analyze_task_impact 전 구간. |
| [`usage-walkthrough.md`](usage-walkthrough.md) | P1/P2/P3 페르소나별 요약 사용 여정(언제·요청·도구·증거·이점). |

---

## 두 실행 트랙 — 라이브 vs 결정적 (둘 다 실제 코어 코드가 수행)

TRACE는 스캔·파싱·**충돌 검출·영향 매핑을 실제 코드(순수 함수)로 수행**하고, LLM 부분만 백엔드를
바꿔 끼웁니다. 두 트랙은 서로를 보완합니다.

| 트랙 | 명령 | 성격 | 무엇을 증명하나 |
|---|---|---|---|
| **라이브** | `python demo/tools/extract_features_live.py` | 실제 Claude(Bedrock opus), **비결정적** | 실제 모델로 Feature/Claim 자동 추출이 동작함(이 실행 기준 39충돌) |
| **결정적** | `python demo/run_demo.py` | LLM만 고정 스텁, **무키·매번 동일** | 키 없이 재현 가능 + 검출 정확성(큐레이션된 9충돌 = 회귀 기준) |

> **결정적 모드는 "가짜 결과"가 아닙니다.** 실제 탐지 로직 위에 LLM 입력만 고정한 것으로,
> 큐레이션된 9충돌은 [`tests/test_demo_dataset_integrity.py`](../tests)가 지키는 ground truth입니다.
> 키 없이 전 구간을 재현할 수 있어 **사용성**과 **정확성 검증**을 동시에 만족시킵니다.

## 재생성 방법

```bash
# 결정적 콘솔 트랜스크립트 (API 키 불필요)
python demo/run_demo.py > result/hero-demo-output.txt 2>/dev/null

# 시연 스크린샷 (실제 tool 출력 → 터미널 PNG, 키 불필요)
python demo/tools/render_screens.py            # → screenshots/*.png

# 라이브 지식 생성 (실제 Bedrock opus, 자격증명 필요 — .env 참고)
python demo/tools/extract_features_live.py     # → demo/.trace/knowledge/features/*.md
```

> 위 스크린샷은 Claude Code GUI 캡처가 아니라 **실제 tool 콘솔 출력을 렌더링**한 이미지입니다.
> 실제 Claude Code 화면 캡처가 필요하면, 저장소 루트 [`README.md`](../README.md)의 `.mcp.json`으로
> TRACE를 연결한 뒤 Hero 프롬프트("이 프로젝트를 분석해줘" → "충돌을 보여줘" → "SMS 인증 추가 영향은?")를
> 실행한 화면을 `screenshots/`에 추가하면 됩니다.

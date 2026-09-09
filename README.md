# TRACE — 개발자 지식 인텔리전스

> 프로젝트 산출물(요구사항·OpenAPI·소스·DB·설정·테스트·문서)을 **기능 단위 지식**으로 재구성하고,
> 문서와 구현이 **어긋난 지점(충돌)을 근거와 함께** 드러내는 로컬 MCP 서버입니다.
> Claude Code 같은 MCP 클라이언트가 코드를 만들기 **직전에** 호출해, 낡은 명세 위에서 자신 있게
> 잘못 구현하는 것을 막습니다.

**상태**: 🚧 개발 중 (AI-DLC Construction 단계). 현재 UOW-0F(Foundation) 계층 구현 완료.
전체 사용법·`.mcp.json` 스니펫·페르소나별 사용 여정·시연 스크린샷은 통합 단위(UOW-06)에서 완성됩니다.

---

## 개발 환경 준비

```bash
# 1) 가상환경 + 의존성 (Python 3.11+)
python -m venv .venv
source .venv/Scripts/activate        # Windows(Git Bash) / macOS·Linux: source .venv/bin/activate
pip install -e ".[dev]"

# 2) API 키 (값은 커밋 금지 — .env 또는 셸 환경변수)
cp .env.example .env                  # 그리고 ANTHROPIC_API_KEY 채우기

# 3) 테스트
pytest
```

## 현재 제공 계층 (UOW-0F Foundation)

| 모듈 | 역할 |
|---|---|
| `trace.models.domain` | C4 도메인 모델(Feature/Claim/Evidence/Conflict/FeatureKnowledge) |
| `trace.models.result` | 공통 Result envelope + `build_result` |
| `trace.models.serialize` | 지식 파일 MD+YAML 결정적 직렬화/역직렬화 |
| `trace.common` | 오류 계층·Warning 누적기·구조화 로깅 |
| `trace.config` | 설정·LLM 세팅(키는 환경변수 이름만) |
| `trace.prompts` | 프롬프트 템플릿 로더 |
| `trace.llm` | LLMClient(Protocol)·LLMService(구조화 출력·재시도) |

## 설계 문서

`aidlc-docs/` — AI-DLC 단계별 산출물. 용어는 `aidlc-docs/GLOSSARY.md` 참고.

## 라이선스

MIT

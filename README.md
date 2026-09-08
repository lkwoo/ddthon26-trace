# Agentic Knowledge Base (MCP-based)

로컬 프로젝트의 소스 코드와 Markdown을 **구조화된 지식**으로 변환해, LLM 에이전트에게는 MCP 인터페이스로, 사람에게는 경량 웹 뷰어로 제공하는 듀얼 인터페이스 지식 베이스.

- **엔진은 LLM을 호출하지 않는다.** 결정적 구조 추출(시그니처/docstring/주석/헤딩)만 수행하며, 심화 자연어 요약은 소비 에이전트가 작성해 Update Tool로 저장한다.
- 파일 기반(Markdown + JSON) Git 친화 저장.
- stdio MCP 전송, 단일 개발자 로컬 환경.

## 아키텍처 (헥사고날)

```
src/agentic_kb/
  domain/       # 순수 도메인 (모델, 그래프, 추출, 청킹, 검색) — I/O 없음, 결정적
  ports/        # 추상 포트 (source / parser / store)
  application/  # 유즈케이스 서비스 (sync / read / query / snippet / update)
  adapters/
    outbound/   # 파일시스템 소스, 파서 레지스트리, 파일시스템 저장소
    inbound/    # mcp / web / cli (U2/U3/U4)
  testing/      # 공용 Hypothesis 제너레이터 (PBT)
```

## 개발 설치

```bash
pip install -e ".[dev]"
pytest
```

## 유닛 (Units of Work)

| Unit | 범위 | 상태 |
|---|---|---|
| U1 Engine Core | domain/ports/application/outbound + testing | 구현 |
| U2 MCP Server | adapters/inbound/mcp | 예정 |
| U3 Web Viewer | adapters/inbound/web | 예정 |
| U4 CLI & Assembly | cli/config/__main__ | 예정 |

자세한 설계는 `aidlc-docs/` 참조.

# Code Generation Summary — U2 MCP Server

> **단계**: CONSTRUCTION – Code Generation · **Unit: U2 MCP Server** · 2026-09-08
> **결과**: `pytest` **37 passed** (U1 28 + U2 9). U2는 얇은 인바운드 어댑터로 U1 서비스에 위임.

## 생성/수정 파일

### 애플리케이션 코드 (`src/agentic_kb/adapters/inbound/mcp/`)
- `resources.py` — **ResourcesProvider**: `agentic-kb://` URI 파싱(BR-M5) → U1 `KnowledgeReadService` 위임 → `to_dict`. 미존재/오류 URI는 `ResourceNotFound`(서버 미중단, US-A1 AC-4). SDK 독립.
- `tools.py` — **ToolsProvider** + `ToolResult`: `query`/`snippet`/`update_note`/`sync` 디스패치. 인자 형식 검증(BR-M6), 하위 예외→`isError` 변환(BR-M8), 각 핸들러 `measure()` 계측(US-N1). SDK 독립.
- `prompts.py` — **PromptsProvider**: `onboarding`/`task` 정적 템플릿(순수 조합, LLM 미호출, BR-M12).
- `server.py` — **StdioServer** + **ProviderBundle**: 유일한 `mcp` SDK 바인딩(지연 import, 미설치 시 안내). `ProviderBundle.from_services(...)`로 U1 서비스에서 provider 조립(U4가 주입).
- `__init__.py` — 공개 심볼 export.

### 수정 (U1)
- `application/payloads.py` — `UpdateResult.to_dict()` 추가(MCP 직렬화 일관, BR-M9).

### 테스트 (`tests/unit/mcp/test_providers.py`)
- Resources: structure/summary/relationships 해석, 미존재·잘못된 스킴·미지원 kind → `ResourceNotFound`.
- Tools: query(키워드/빈결과), snippet(예산 준수), update_note(검증 실패/성공·영속), 잘못된 mode/음수 예산/미지원 tool → `isError`, sync 리포트.
- Prompts: onboarding/task 렌더, 미지원 → `PromptNotFound`.
- `ToolResult.to_dict` 형태(`isError`/`content`).

## 설계 준수
- **로직 미보유·위임만**(BR-M1), **엔진 LLM 미호출**(BR-M2, NFR-C3), **SDK 격리**(Humble Object — provider는 SDK 독립·테스트 가능, NFR-U2-M1), **장애 격리**(서버 미중단, NFR-U2-A1), **표면 계측**(US-N1).

## PBT 컴플라이언스 (U2)
- U2는 순수 매핑 계층 → 신규 PBT 대상 얕음. round-trip(PBT-02)/invariant(PBT-03)는 U1이 보증. U2는 **PBT-10 예제 테스트**로 URI 파싱·디스패치·오류 매핑을 커버(NFR-U2-T1/T2). PBT Partial 차단 위반 없음.

## 스토리 커버리지
US-A1(Resources), US-A2(query), US-A3(snippet), US-A4(update_note), US-A5(Prompts), US-A6(ProviderBundle/StdioServer stdio 기동), US-N1(계측), US-N7(sync report 노출).

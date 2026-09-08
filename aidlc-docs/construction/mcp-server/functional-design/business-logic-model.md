# Business Logic Model — U2 MCP Server

> **핵심 원칙**: U2는 로직을 보유하지 않는다. 모든 요청은 URI/페이로드를 파싱·검증한 뒤 **U1 Application 서비스로 위임**하고, 결과를 직렬화해 반환한다. 계측만 표면에서 추가한다(US-N1).

## 1. 논리 컴포넌트 (SDK 독립, Q6=A)

```
adapters/inbound/mcp/
├── resources.py   # ResourcesProvider — URI → U1 read 서비스 위임 (순수 매핑)
├── tools.py       # ToolsProvider     — query/snippet/update_note/sync 위임 (순수 매핑)
├── prompts.py     # PromptsProvider   — onboarding/task 템플릿 조합 (순수 함수)
├── serialization  # (models.to_dict 재사용 — 별도 모듈 불필요)
└── server.py      # StdioServer       — 공식 mcp SDK 바인딩 + stdio 전송 (얇은 껍데기)
```

- **provider 3종**은 SDK에 의존하지 않는 순수 매핑 함수/클래스 → 단위 테스트 가능(목 서비스 주입).
- **server.py**만 `mcp` SDK를 import하여 provider를 등록하고 stdio 전송을 기동. 조립 시 U4 `config.py`가 U1 서비스 구현을 주입.

## 2. 위임 흐름

### 2.1 Resource 조회 (US-A1)
```
client → server.read_resource(uri)
       → ResourcesProvider.resolve(uri)
            parse uri → (kind, target?)
            switch kind:
              structure     → read.get_structure()
              summary/{t}    → read.get_summary(t)
              relationships  → read.get_relationships(t?)
            if None → raise ResourceNotFound (서버 미중단)  [BR-M4]
            else    → obj.to_dict() → JSON 텍스트
       ← measure("mcp.resource.<kind>") 로 감싼 elapsed_ms 로깅  [US-N1]
```

### 2.2 Tool 호출 (US-A2/A3/A4 + sync)
```
client → server.call_tool(name, args)
       → ToolsProvider.dispatch(name, args)
            validate args shape (필수 키/타입)  [BR-M5]
            switch name:
              query        → QueryService.query(...)         → {results:[...]}
              snippet      → SnippetService.snippet(...)      → Snippet.to_dict()
              update_note  → UpdateService.apply_note(...)    → UpdateResult.to_dict()
              sync         → SyncService.run(...)             → SyncReport.to_dict()
            검증 실패 → {isError:true, message}  (엔진 미변경)  [BR-M6]
       ← measure("mcp.tool.<name>") 로 계측  [US-N1]
```

### 2.3 Prompt 획득 (US-A5)
```
client → server.get_prompt(name, args)
       → PromptsProvider.render(name, args)
            onboarding → 정적 온보딩 템플릿
            task       → task_kind 삽입한 작업 템플릿
            unknown    → PromptNotFound
       ← 조합된 메시지(정적 텍스트, LLM 미호출)
```

### 2.4 기동/핸드셰이크 (US-A6)
```
python -m agentic_kb serve-mcp  (U4 진입점)
  → config.assemble()  # U1 서비스 구현 주입
  → StdioServer(providers).run()
       stdio 핸드셰이크 → Resources/Tools/Prompts 목록 노출  [US-A6 AC-1]
       외부 서비스 의존 없음(파서/LLM 제외)                    [US-A6 AC-2]
```

## 3. 계측 모델 (US-N1)
- 모든 핸들러는 U1 `application.measurement.measure(name)` 컨텍스트로 감싼다.
- 계측은 elapsed_ms를 로깅할 뿐 응답 페이로드/로직에 영향 없음(표면 관심사).

## 4. 오류 처리 요약
| 계층 | 실패 | 처리 |
|---|---|---|
| Resource | 미존재/미인제스천 | not-found 신호, 서버 계속 (US-A1 AC-4) |
| Tool | 인자 형식/검증 | `isError` 결과, 엔진 미변경 |
| Tool | 하위 서비스 예외 | 포착 → `isError` 결과로 변환(서버 미중단) |
| Prompt | 미지원 name | prompt not-found |

## 5. 스토리 커버리지
US-A1(Resources), US-A2(query tool), US-A3(snippet tool), US-A4(update_note tool), US-A5(Prompts), US-A6(stdio serve), US-N1(표면 계측), US-N7(sync report 노출).

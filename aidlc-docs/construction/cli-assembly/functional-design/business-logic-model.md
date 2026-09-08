# Business Logic Model — U4 CLI & Assembly

> **핵심 원칙**: U4는 유일한 **조립 루트(Composition Root)**. 구현체 선택·주입은 여기서만. CLI는 인자를 파싱해 조립된 서비스에 위임. 도메인/유즈케이스 로직 미보유.

## 1. 논리 컴포넌트

```
src/agentic_kb/
├── config.py     # AppConfig + assemble(config) -> AssembledApp  (DI 루트)
├── __main__.py   # main(argv) : argparse -> config -> assemble -> dispatch
└── adapters/inbound/cli/
    └── commands.py  # 서브커맨드 핸들러 (cmd_ingest/sync/serve_mcp/serve_web)
```

## 2. 조립 흐름 (config.assemble, Q2=A)

```
assemble(config) -> AssembledApp:
    store    = FileSystemKnowledgeStore(config.store_dir)
    source   = FileSystemSource(config.project_root)
    registry = default_registry()                      # U1 ParserRegistry
    sync     = SyncService(source, registry, store)
    read     = KnowledgeReadService(store)
    query    = QueryService(store)
    snippet  = SnippetService(store, source)
    update   = UpdateService(store)
    # U2 providers (지연 조립 — serve-mcp에서만 필요)
    mcp_bundle = ProviderBundle.from_services(read, query, snippet, update, sync)
    # U3 web app
    web_app  = WebApp(read)
    return AssembledApp(sync, read, query, snippet, update, mcp_bundle, web_app, config)
```

- 모든 서비스는 **포트 추상**에만 의존. 구현 바인딩은 이 함수에 격리(BR-CA1).

## 3. CLI dispatch 흐름 (__main__.main)

```
main(argv):
    parser = build_parser()          # argparse 서브커맨드
    args = parser.parse_args(argv)
    config = AppConfig.from_args(args)
    app = assemble(config)
    return dispatch(args.command, app, args)   # -> exit code
```

### 커맨드 핸들러
```
cmd_ingest(app, args): report = app.sync.run(root, "full");   print_report(report, args.json); return 0
cmd_sync(app, args):   mode = "full" if args.full else "resync"
                       report = app.sync.run(root, mode);      print_report(report, args.json); return 0
cmd_serve_mcp(app,_):  StdioServer(app.mcp_bundle).run();      return 0
cmd_serve_web(app,a):  WebServer(app.web_app, a.host, a.port).serve_forever(); return 0
```

## 4. 출력 (US-N7)
```
print_report(report, as_json):
    if as_json: stdout(json.dumps(report.to_dict(), sort_keys=True))
    else:       stdout(f"files={report.files_total} symbols={report.symbols_total} "
                       f"skipped={len(report.skipped)} failures={len(report.failures)} "
                       f"elapsed={report.duration_ms}ms")
                for line in report.skipped:  stdout("  skip: " + line)
                for line in report.failures: stderr("  fail: " + line)
```

## 5. 오류/종료 코드 (Q6=A)
- 치명 실패(경로 없음 등)는 예외 포착 → stderr 메시지 + exit 1.
- 파일 단위 부분 실패는 SyncReport.failures로 보고하되 exit 0(격리, BR-3).
- argparse 사용법 오류는 exit 2(기본 동작).

## 6. 스토리 커버리지
US-E1(ingest full), US-E5(sync resync/--full, 명시적 실행), US-A6(serve-mcp stdio), US-H*(serve-web), US-N7(규모·소요 출력).

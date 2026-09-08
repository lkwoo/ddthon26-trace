# Domain Entities — U4 CLI & Assembly (Surface Model)

> U4는 자체 도메인 엔티티가 없다. 아래는 CLI 표면 + 조립 설정 모델이다.

## 1. AppConfig (조립 설정)
| 필드 | 기본값 | 의미 |
|---|---|---|
| `project_root` | cwd | 소스 프로젝트 경로(FileSystemSource) |
| `store_dir` | `.agentic_kb` | KB 저장 디렉토리(FileSystemKnowledgeStore) |
| `host` | `127.0.0.1` | serve-web 바인드 호스트 |
| `port` | `8080` | serve-web 포트 |

## 2. 서브커맨드 (Q1/Q3=A)
| 커맨드 | 인자 | 위임 | 스토리 |
|---|---|---|---|
| `ingest` | `--project`, `--store`, `--json` | `SyncService.run(root, "full")` | US-E1 |
| `sync` | `--project`, `--store`, `--full`, `--json` | `SyncService.run(root, "resync"\|"full")` | US-E5 |
| `serve-mcp` | `--project`, `--store` | `StdioServer(bundle).run()` | US-A6 |
| `serve-web` | `--project`, `--store`, `--host`, `--port` | `WebServer(WebApp(read)).serve_forever()` | US-H* |

## 3. 출력 모델 (US-N7, Q4=A)
- 사람용 요약: `files=<n> symbols=<n> skipped=<n> failures=<n> elapsed=<ms>ms` + skip/실패 상세 라인.
- `--json`: `SyncReport.to_dict()` 그대로 stdout(JSON).

## 4. 종료 코드 (Q6=A)
| 코드 | 조건 |
|---|---|
| 0 | 성공(파일 단위 부분 실패 포함 — 격리·보고) |
| 1 | 치명 실패(예: 경로 없음) |
| 2 | 사용법 오류(argparse) |

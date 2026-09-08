# Tech Stack Decisions — U4 CLI & Assembly

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U4 CLI & Assembly** · 2026-09-08

## 1. CLI
- **stdlib `argparse`** 서브커맨드(`ingest`/`sync`/`serve-mcp`/`serve-web`). 외부 CLI 라이브러리 미도입(최소 의존).
- 콘솔 진입점: `pyproject.toml [project.scripts] agentic-kb = "agentic_kb.__main__:main"` (기존 선언 활용).

## 2. 조립(DI)
- **수동 조립(Composition Root)**: `config.assemble(config)`가 구현체를 생성·주입. DI 프레임워크 미사용(명시적·단순·테스트 가능).

## 3. 서버 기동
- `serve-mcp` → U2 `StdioServer`(mcp SDK 지연 import, `[mcp]` extra).
- `serve-web` → U3 `WebServer`(stdlib http.server).

## 4. 출력/직렬화
- 사람용 요약 텍스트 + `--json`(stdlib `json`, U1 `SyncReport.to_dict()`).

## 5. 테스트
- **pytest** — `main(argv)` 종료 코드/출력(capsys) + `assemble()` 배선 예제 테스트.

## 6. 의존성 (pyproject.toml)
| 의존성 | 범위 | 용도 |
|---|---|---|
| (stdlib) argparse, json | runtime | CLI + 출력 |
| U1/U2/U3 컴포넌트 | runtime | 조립·위임 |
| mcp | optional `[mcp]` | serve-mcp에서만 |
| pytest | dev | CLI/assemble 테스트 |

> pyproject의 `[project.scripts]`·optional-extras는 U1 단계에 이미 선언됨. U4는 추가 필수 의존 없음.

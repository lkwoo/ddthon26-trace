# Build Instructions — TRACE

> CONSTRUCTION / Build and Test. 8개 단위(UOW-0F~06) 완료 후 전체 빌드·설치 절차.
> 앞 단계 반영: units-generation의 위상 순서로 구현된 `traceki` 단일 패키지를 한 번에 설치한다.

## 사전 요건

| 항목 | 값 |
|---|---|
| Python | 3.10 이상 (개발/검증 환경 3.10.6) |
| 빌드 백엔드 | hatchling (`pyproject.toml`) |
| 진입점(console script) | `trace` = `traceki.cli:main`, `trace-mcp` = `traceki.mcp_server:main` |
| import 패키지 | `traceki` (파이썬 stdlib `trace` 충돌 회피용 개명) |
| API 키 | **replay 모드는 불필요.** live 모드만 `ANTHROPIC_API_KEY`(env) 필요 |

## 설치

```bash
# 저장소 루트에서
python3 -m venv .venv && source .venv/bin/activate   # 권장(선택)
pip install -e .
```

설치 검증:

```bash
which trace trace-mcp          # 두 명령이 PATH에 노출되어야 함
trace --help                   # 서브커맨드 목록 출력
python3 -c "import traceki; print('ok')"
```

## 의존성

`pyproject.toml`의 `dependencies`에 핀 고정:

- `anthropic` — live 백엔드 Claude 호출 (replay에서는 미사용)
- `mcp>=2.0.0,<3` — MCP 서버(stdio)
- `pypdf` — PDF 자산 파싱
- `pyyaml` — OpenAPI/설정 파싱
- 테스트: `pytest`, `hypothesis` (`[project.optional-dependencies].dev` 또는 개발 설치 시)

```bash
pip install -e ".[dev]"        # 테스트 의존성 포함 설치
```

## 시크릿 취급 (NFR-SEC-001)

- 키는 **환경변수 `ANTHROPIC_API_KEY`로만** 주입. 코드/로그/커밋에 평문 금지.
- `.env`는 `.gitignore`로 제외, `.env.example`만 커밋.
- 로그는 `mask_secrets`로 `sk-ant-***` 마스킹.

## 트러블슈팅

| 증상 | 원인 / 조치 |
|---|---|
| `ModuleNotFoundError: No module named 'trace.cli'` | 구버전. import 패키지는 `traceki`. `pip install -e .` 재실행 |
| `trace` 명령이 저장소 안에서만 동작 | 해소됨(traceki 개명). 저장소 밖에서도 동작 확인 |
| MCP 관련 import 오류 | `mcp>=2,<3` 설치 확인. 코어 로직은 mcp 비의존이라 CLI는 영향 없음 |

# Build Instructions — TRACE

**단계**: CONSTRUCTION / Build and Test
**작성일**: 2026-09-09
**대상**: 전체 유닛(UOW-0F ~ UOW-06) 통합 빌드.

---

## 1. 사전 요구
- Python **3.11+** (`requires-python = ">=3.11"`).
- OS: Windows / macOS / Linux (개발은 Windows 11 + Git Bash 기준 검증).
- (선택) 실 LLM 사용 시 Anthropic API 키.

## 2. 환경 구성
```bash
# 1) 가상환경
python -m venv .venv
source .venv/Scripts/activate        # Windows(Git Bash) / *nix: source .venv/bin/activate

# 2) 의존성(개발 포함) — editable 설치
pip install -e ".[dev]"
```

### 선언된 의존성 (pyproject.toml)
| 런타임 | 용도 |
|---|---|
| `mcp>=2.0` | MCP 서버(MCPServer, stdio) |
| `anthropic>=0.40.0` | Claude 클라이언트(지연 임포트) |
| `pydantic>=2.6` | 도메인·Result 모델 |
| `PyYAML>=6.0` | 지식 파일 MD+YAML 직렬화 |
| `pypdf>=4.0` | PDF 파싱(P0) |

| 개발 | 용도 |
|---|---|
| `pytest>=8.0` / `hypothesis>=6.100` | 단위·속성 기반 테스트 |
| `mypy>=1.9` / `types-PyYAML` | 정적 타입 체크 |

## 3. 콘솔 스크립트(엔트리포인트)
`pip install` 후 등록:
- `trace-mcp` → `trace.mcp_server.__main__:main` (MCP stdio 서버, C1)
- `trace` → `trace.cli.__main__:main` (폴백 CLI, C9)

## 4. 빌드 검증(스모크)
```bash
python -c "import trace, trace.engine, trace.mcp_server.server, trace.cli.__main__; print('import OK')"
trace --help
python demo/run_demo.py         # 무키 결정적 Hero 데모
```

## 5. 시크릿/설정
- `cp .env.example .env` 후 `ANTHROPIC_API_KEY` 설정(커밋 금지 — `.gitignore` 처리).
- `TRACE_PROJECT_ROOT`(선택): 분석 루트. 미지정 시 실행 디렉터리.
- 키 값은 소스·로그·저장소에 저장하지 않음(late lookup, NFR-SEC-001/002).

## 6. 패키징(선택)
```bash
pip install build && python -m build      # hatchling 백엔드, wheel/sdist
```

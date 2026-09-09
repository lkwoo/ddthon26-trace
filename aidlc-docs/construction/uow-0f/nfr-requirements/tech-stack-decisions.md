# UOW-0F — 기술 스택 결정 (Tech Stack Decisions)

**단계**: CONSTRUCTION / NFR Requirements — UOW-0F (Foundation)
**작성일**: 2026-09-09
**상위 확정(요구사항 Q1~Q7)**: Python + 공식 Python MCP SDK(`mcp`) · Anthropic Claude · 단일 설치형 패키지

> 요구사항 단계에서 언어·프로토콜·LLM은 확정됐다. 이 문서는 **UOW-0F가 도입하는 구체 라이브러리**와
> 그 근거를 동결한다. 이 선택은 이후 전 단위가 공유한다.

---

## 결정 표

| # | 영역 | 선택 | 대안 | 근거 |
|---|---|---|---|---|
| Q1 | 도메인 모델·검증 | **Pydantic v2** | dataclasses, attrs | 필드 검증 + `model_dump`/`model_validate` 직렬화 + `model_json_schema()`가 LLM 구조화 출력 검증(`complete_structured`의 schema)과 MCP 입력스키마에 그대로 재사용됨 → 한 정의로 3용도 |
| Q2 | YAML 처리 | **PyYAML** (`safe_load`/`safe_dump`) | ruamel.yaml, python-frontmatter | 표준·경량, `safe_load`로 임의 객체 역직렬화 차단(NFR-0F-SEC-4). Front Matter 분리는 직접(`---` 경계) |
| Q3 | 재현성 | **순서 고정 + `sort_keys=True`** | 논리 동등만 | 바이트 동일 산출 → Hero 데모 재현성(NFR-0F-DET-1) |
| Q4 | LLM 재시도 | **max_retries=2, 제약 교정 재프롬프트** | 재시도 없음, 3회+백오프 | 구조화 실패 회복과 결정성/속도 균형(NFR-0F-REL-3) |
| Q5 | 로깅 | **표준 `logging`** (구조화 키=값) | structlog, 커스텀 | 의존성 0, 레벨 env 조정으로 충분(NFR-0F-OBS-1) |
| Q6 | 시크릿 | **env-only**(이름만 보관, 소비 직전 조회) | 코드/설정 저장 | NFR-0F-SEC-1. `.env` 개발 편의 로드는 UOW-06에서 선택 검토 |
| Q7 | PBT | **Hypothesis** | 예시 기반 수동 | 멱등·round-trip 속성 자동 탐색(PBT 확장, NFR-0F-TST-2) |
| Q8 | Python 하한 | **3.11+** | 3.10, 3.12 | `tomllib` 내장(설정), 최신 typing, MCP SDK 호환 |

---

## 의존성 (pyproject 반영 예정 — UOW-0F가 최초 선언)

**런타임**
- `mcp` — 공식 Python MCP SDK (서버는 UOW-05, 계약 참조는 0F)
- `anthropic` — Claude 클라이언트(LLMService 실제 호출은 Code Generation)
- `pydantic>=2` — 모델·검증·스키마
- `PyYAML` — 지식 파일 직렬화

**개발/테스트**
- `pytest` — 테스트 러너
- `hypothesis` — 속성 기반 테스트
- 타입 체크: `mypy` 또는 `pyright`(NFR-0F-MNT-1)

**빌드/패키징**
- `pyproject.toml` (PEP 621) 단일 배포물, 진입점 `trace-mcp`·`trace`
- 락파일(`uv.lock` 또는 동등) — 빌드 재현성(평가: 완성도)

> 표준 라이브러리 사용: `logging`(관측성), `os.environ`(시크릿), `tomllib`(설정), `pathlib`(경로/검증).

---

## 결정이 하위 단위에 주는 계약
- 모든 도메인 객체는 **Pydantic 모델** → UOW-01~06은 `.model_validate`/`.model_dump`로 일관 처리.
- LLM 구조화 출력 검증은 각 AI 단위가 **Pydantic 모델의 JSON 스키마**를 `complete_structured(schema=...)`에 전달.
- 지식 파일 I/O는 UOW-02가 0F의 `serialize/deserialize`(PyYAML 기반)를 그대로 호출.
- 이 결정은 NFR Design(UOW-0F)에서 패턴(팩토리·주입 경계·로깅 데코 등)으로 구체화된다.

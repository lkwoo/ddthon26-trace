# Tech Stack Decisions — U1 Engine Core

> **단계**: CONSTRUCTION – NFR Requirements · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08

---

## 1. 언어 / 런타임
- **Python ≥ 3.11** (요구사항 Q1). 표준 라이브러리 우선, 외부 의존 최소화(엔진 로컬성/결정성 NFR-C3).
- dataclasses(frozen) 기반 불변 도메인 모델. `hashlib`(sha256), `json`(정렬 직렬화) 표준 라이브러리 사용.

## 2. 파싱 (Graph Construction)
- **tree-sitter** 기반 파서(다국어 확장, NFR-C2). MVP 파서: Python(`tree-sitter-python`), Markdown은 경량 헤딩/구조 파서(표준 라이브러리 + 정규식 기반, tree-sitter-markdown 선택).
- **플러그인 구조**: `LanguageParserPort` 구현을 `ParserRegistry`에 등록. 코어 무수정 확장(US-N4).
- 파서 부재/실패는 skip·기록(BR-2/3).

## 3. 저장 (Persistence)
- **파일 기반**: 구조/그래프는 JSON(정렬 키·결정적), 요약/노트는 Markdown. Git 친화(US-E4/N5, NFR-D1).
- 외부 DB 없음. 저장 루트는 config로 지정(기본 `.agentic_kb/`).

## 4. 테스트 (Testability — PBT Partial)
- **pytest** — 테스트 러너.
- **Hypothesis** — Property-Based Testing 프레임워크 (**PBT-09**). 선정 근거:
  - 커스텀 strategy(도메인 제너레이터, PBT-07) 지원
  - 자동 shrinking(PBT-08) — 실패 입력 최소화
  - 시드 기반 재현성(`--hypothesis-seed`, DB) — 실패 재현(PBT-08)
  - pytest 통합(기존 러너 연동, PBT-09 요건)
- 공용 도메인 제너레이터는 `src/agentic_kb/testing/`에 배치(Q6=A, 재사용).

## 5. 의존성 (pyproject.toml 예정)
| 의존성 | 범위 | 용도 |
|---|---|---|
| tree-sitter, tree-sitter-python | runtime | 코드 파싱(그래프) |
| (표준) json, hashlib, pathlib, dataclasses | runtime | 도메인/직렬화/파일 |
| pytest | dev | 테스트 러너 |
| hypothesis | dev | PBT (PBT-09) |

> Web(U3)·MCP(U2) 관련 의존성은 각 Unit의 NFR/Code Generation에서 확정. U1은 코어 최소 의존.

## 6. 빌드 / 패키징
- **src-layout**(`src/agentic_kb/`), `pyproject.toml`(hatchling 등 PEP 517 백엔드). 단일 배포 패키지.

## 7. PBT-09 컴플라이언스 체크
- [x] 프레임워크 선정·문서화: **Hypothesis**
- [x] 프로젝트 의존성 포함 예정(pyproject dev deps)
- [x] 커스텀 제너레이터·shrinking·시드 재현 지원 확인
- [x] pytest 러너 통합

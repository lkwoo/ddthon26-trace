# Code Generation Plan — U1 Engine Core

> **단계**: CONSTRUCTION – Code Generation (per-unit) · **Unit: U1 Engine Core**
> **작성일**: 2026-09-08 · **자동 진행**: 사용자가 계획 승인 자동 위임.
> **워크스페이스 루트(실제)**: `/home/infin/workspace/ddthon26-trace`
> **코드 위치**: `src/agentic_kb/` + `tests/` (src-layout, Q7=A). 문서 요약은 `aidlc-docs/construction/engine-core/code/`.
> **단일 진실 원천**: 본 계획이 Code Generation의 단일 진실 원천이다.

---

## Unit 컨텍스트
- **구현 스토리**: US-E1~E5, US-A2/A3/A4(서비스 로직), US-N2~N7
- **의존**: 없음(leaf). U2/U3/U4가 본 Unit에 의존.
- **인터페이스/계약**: `ports/*`(추상), `application/*` 서비스가 인바운드 어댑터에 노출할 API.
- **엔티티 소유**: domain.models 전체(U1 소유).

## MVP 파서 결정 (실용 정제)
- MVP 구체 파서 = **Python stdlib `ast`** 기반 `PythonAstParser` + 정규식 기반 `MarkdownParser`. 네이티브 빌드/외부 의존 없이 결정적·로컬(NFR-C3) 보장, 즉시 설치·테스트 가능.
- **tree-sitter**는 `LanguageParserPort` 플러그인으로 후속 편입(NFR-C2 확장 구조 유지). tech-stack-decisions.md의 tree-sitter는 향후 옵션 의존으로 재분류.

---

## 생성 단계 (Numbered Steps)

- [x] **Step 1 — 프로젝트 구조 셋업(greenfield)**: `pyproject.toml`, `src/agentic_kb/__init__.py`, 서브패키지 `__init__.py`, `tests/conftest.py`, `README.md`. (US-N5)
- [x] **Step 2 — Business Logic: domain.models**: 15개 불변 dataclass + `to_dict/from_dict`(round-trip), sha, id 스킴, 정렬. (US-E4, US-N6 PBT-02)
- [x] **Step 3 — Business Logic: domain 순수 로직**: graph_builder, extractor, chunking, query. (US-E2/E3, US-A2/A3, US-N2)
- [x] **Step 4 — Ports**: source_port, parser_port, store_port(ABC). (헥사고날)
- [x] **Step 5 — Outbound Adapters**: filesystem_source(경로 confinement), parsers(PythonAstParser, MarkdownParser, ParserRegistry), filesystem_store(JSON/Markdown, sha 인덱스, 노트 네임스페이스). (US-E1/E4, US-N4/N7)
- [x] **Step 6 — Application Services**: sync/read/query/snippet/update + measurement 훅. (US-E1/E5, US-A1/A2/A3/A4, US-N1/N7)
- [x] **Step 7 — Testing 지원**: `src/agentic_kb/testing/` Hypothesis strategies(도메인 제너레이터, PBT-07).
- [x] **Step 8 — Unit Tests(예제 + PBT)**: tests/unit/domain(round-trip PBT-02, invariant PBT-03), tests/unit/application(서비스, 포트 스텁), 예제 기반 테스트(PBT-10). 시드/셔링킹(PBT-08).
- [x] **Step 9 — 문서 요약**: `aidlc-docs/construction/engine-core/code/` 코드 요약 md.

## 스토리 추적
| Step | 스토리 |
|---|---|
| 2 | US-E4, US-N5, US-N6 |
| 3 | US-E2, US-E3, US-A2, US-A3, US-N2 |
| 4 | 헥사고날(NFR-C1/C2) |
| 5 | US-E1, US-E4, US-N4, US-N7 |
| 6 | US-E1, US-E5, US-A1~A4, US-N1, US-N7 |
| 7-8 | US-N6 (PBT-02/03/07/08/10) |

## PBT 컴플라이언스 (Code Generation 적용: PBT-01~10)
- PBT-01: functional-design에 Testable Properties 명세됨(domain-entities §4). ✔
- PBT-02: 모든 엔티티 round-trip 테스트. ✔ (Step 8)
- PBT-03: graph_builder/chunking/estimate_tokens 불변식. ✔ (Step 8)
- PBT-07: 도메인 strategy는 `testing/`에 중앙화. ✔ (Step 7)
- PBT-08: Hypothesis 기본 shrinking·시드(비활성화 금지). ✔
- PBT-09: Hypothesis 의존성 pyproject. ✔ (Step 1)
- PBT-10: 예제 기반 테스트 병행(핵심 경로). ✔ (Step 8)
- PBT-04/05/06: 부분 모드 advisory. 04(idempotence: `build(build)`≈, resync 스킵) 일부 커버, 05/06 N/A(오라클/스테이트풀 대상 제한적).

## 진행 절차
- [x] Part 1 Step 1-9(planning) 완료·승인(자동)
- [x] Part 2 Step 10-13: 코드 생성·체크박스 갱신
- [x] Step 14-16: 완료 → 승인(자동) → state 갱신

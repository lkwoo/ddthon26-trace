# Code Generation Summary — U1 Engine Core

> **단계**: CONSTRUCTION – Code Generation · **Unit: U1 Engine Core** · 2026-09-08
> **결과**: `pytest` **28 passed** (PBT + 예제 기반). 코드는 `src/agentic_kb/`, 테스트는 `tests/`.

---

## 생성 파일 (Created)

### 프로젝트 루트
- `pyproject.toml` — 패키징(hatchling, src-layout), dev 의존성 **pytest + hypothesis(PBT-09)**, tree-sitter/mcp는 optional-extras.
- `README.md`, `.gitignore`

### 애플리케이션 코드 (`src/agentic_kb/`)
- `__init__.py`
- **domain/** (순수·결정적·I/O 없음)
  - `models.py` — 15개 불변 dataclass + `to_dict/from_dict`(round-trip, PBT-02), sha, 결정적 id 스킴, 열거값 검증(BR-25), 그래프 무결성(BR-26)
  - `graph_builder.py` — 결정적 심볼/엣지 그래프(dedup·정렬), 미해결 참조 드롭
  - `extractor.py` — 결정적 구조 추출(시그니처/docstring/헤딩/주석)
  - `chunking.py` — `estimate_tokens`(로컬 휴리스틱, 단조·비음수), `select_snippet`(예산 준수·절단 표시)
  - `query.py` — 가중 키워드 검색 + 그래프 인접 탐색(결정적 정렬)
  - `structure.py` — 결정적 디렉토리/파일 트리 빌드
- **ports/** — `source_port.py`, `parser_port.py`, `store_port.py` (ABC 계약)
- **application/**
  - `sync_service.py` — 파이프라인 조율, 실패 격리(BR-3), sha 스킵(BR-12), 노트 보존(BR-9), SyncReport(US-N7)
  - `read_service.py` — 구조/병합 요약(MergedSummary, 엔진 우선)/관계, 미존재 None(BR-13)
  - `query_service.py` — keyword/graph/auto 위임
  - `snippet_service.py` — 대상 해석 + 예산 스니펫
  - `update_service.py` — 노트 검증(BR-21)·원자적 실패(BR-22)·별도 네임스페이스 저장(BR-23)
  - `measurement.py` — 지연 계측 훅(US-N1 AC-2), `payloads.py`
- **adapters/outbound/**
  - `filesystem_source.py` — 로컬 순회/읽기 + 경로 confinement(BR-4)
  - `parsers.py` — **PythonAstParser(stdlib ast)** + **MarkdownParser** + **ParserRegistry**(플러그인, NFR-C2)
  - `filesystem_store.py` — JSON+Markdown 결정적 저장, sha manifest, 노트 네임스페이스
- **testing/** — `strategies.py` (재사용 Hypothesis 제너레이터, PBT-07)

### 테스트 (`tests/`)
- `conftest.py` — Hypothesis 프로파일(dev/ci), shrinking 유지·시드 재현(PBT-08)
- `unit/domain/test_models_roundtrip.py` — 전 엔티티 round-trip(PBT-02) + JSON 왕복
- `unit/domain/test_invariants.py` — estimate_tokens/select_snippet/graph 불변식(PBT-03) + 예제(PBT-10)
- `unit/domain/test_parser_extractor.py` — 파서/추출/검색 결정성·정확성(예제, PBT-10)
- `unit/application/test_services.py` — sync/resync/read-merge/query/snippet/update, 노트 보존

## MVP 파서 결정
- 구체 파서는 **stdlib `ast`(Python) + 정규식(Markdown)** — 네이티브 빌드/외부 의존 없이 결정적·즉시 설치(NFR-C3). tree-sitter는 `LanguageParserPort` 플러그인으로 후속 편입(NFR-C2, optional-extra).

## PBT 컴플라이언스 (Code Generation)
| Rule | 상태 |
|---|---|
| PBT-01 (설계 속성 식별) | Compliant (functional-design §4) |
| PBT-02 (round-trip) | Compliant — 10개 엔티티 property test |
| PBT-03 (invariant) | Compliant — tokens/snippet/graph |
| PBT-07 (제너레이터 품질) | Compliant — `testing/strategies.py` 중앙화·도메인 제약 준수 |
| PBT-08 (shrinking/재현성) | Compliant — 기본 shrinking, print_blob, ci 프로파일 derandomize |
| PBT-09 (프레임워크) | Compliant — Hypothesis 의존성 |
| PBT-10 (예제 병행) | Compliant — 핵심 경로 예제 테스트 |
| PBT-04/05/06 | Advisory(부분 모드) — 04 부분 커버(그래프 결정성/resync 스킵), 05/06 N/A |

## 스토리 커버리지
US-E1~E5, US-A2/A3/A4(서비스 로직), US-N1~N7 구현. 테스트 28건 통과.

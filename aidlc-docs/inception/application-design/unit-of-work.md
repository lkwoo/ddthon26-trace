# TRACE — 개발 단위 (Units of Work)

**단계**: INCEPTION / Units Generation (Part 2)
**작성일**: 2026-09-08
**결정 반영**: Q1=A(UOW-0F 신설), Q2=A(02/03 분리+단일담당), Q3=A(3-웨이브 병렬), Q4=A(단일 패키지), Q5=A(스토리 유지, 0F=enabler)

> 단위(Unit of Work)는 개발용 논리 묶음이다. TRACE는 **단일 설치형 패키지 `trace/`** 하나로
> 배포되며(로컬 stdio 단일 프로세스), 각 단위는 그 안의 계층별 서브모듈 경계에 대응한다.

---

## 코드 구성 전략 (Greenfield, Q4=A)

```text
ddthon26-trace/
├── pyproject.toml            # 단일 배포물, 의존성/진입점(mcp_server, cli) 선언
├── uv.lock (또는 lock)       # 락파일 (평가: 빌드 재현성)
├── trace/                    # 애플리케이션 패키지 (단위=서브모듈)
│   ├── models/    C4 도메인 모델·직렬화        ← UOW-0F
│   ├── common/    Result envelope·오류·로깅     ← UOW-0F
│   ├── config/    C7 설정·제외규칙·시크릿(env)  ← UOW-0F
│   ├── prompts/   C8 템플릿 + 로더              ← UOW-0F(로더)/UOW-02·03·04(내용)
│   ├── llm/       S4 LLMService(Claude 클라이언트) ← UOW-0F(스켈레톤)
│   ├── engine/    C2 스캔·파싱·오케스트레이션    ← UOW-01(+S1/S2/S3 배선)
│   ├── workflow/  C3 AI step                    ← UOW-02·03·04
│   ├── knowledge/ C4 저장소 I/O(.trace)         ← UOW-02
│   ├── conflict/  C5 충돌 검출                   ← UOW-03
│   ├── impact/    C6 Task Impact                 ← UOW-04
│   ├── mcp_server/ C1 MCP 어댑터                 ← UOW-05
│   └── cli/       C9 폴백 CLI                    ← UOW-06(or 05)
├── demo/                     # 데모 데이터셋·픽스처      ← UOW-00
├── tests/                    # 단위/속성/통합 테스트
├── result/ (screenshots/)    # 시연 스크린샷            ← UOW-06
└── README.md                 # .mcp.json 스니펫·예제 프롬프트 ← UOW-06
```

- 서브모듈 = 단위 경계. 단위 간 통신은 **동기 in-process 함수 호출**(원격 없음).
- 진입점 2개: `trace-mcp`(MCP stdio 서버, C1), `trace`(폴백 CLI, C9).

---

## 단위 정의

### UOW-0F — Foundation (공유 계약) 〔enabler, 신설〕
- **책임**: 이후 모든 단위가 기대는 **계약을 동결**한다.
  - C4 도메인 모델: `Feature, Claim(subject/predicate/value), Evidence(source/type/location/extracted_value/relation), Confidence(HIGH/MEDIUM/LOW), Conflict(type/claim/values/interpretation), FeatureKnowledge`
  - MD+YAML Front Matter 직렬화 스키마(구조=YAML, 설명=Markdown; 단일 진실원)
  - 공통 `Result` envelope (summary→data→conflicts→impact→evidence→warnings→meta)
  - C7 `config`: `load_config / get_exclusions / get_llm_settings`(모델·키 env, 결정성 파라미터)
  - C8 프롬프트 **로더** `get_prompt(name, **vars)` (템플릿 내용은 각 AI 단위가 채움)
  - S4 `LLMService` 스켈레톤: Claude 호출·구조화(JSON) 출력 검증·제약교정 재시도·결정성 고정
  - 공통 로깅(NFR-LOG-001)·오류 타입
- **컴포넌트**: C4(모델), C7, C8(로더), S4 스켈레톤, common
- **인터페이스(제공)**: 위 모델/함수/Result — **이것이 병렬 트랙들의 이음새**
- **의존**: 없음 (leaf)
- **스토리**: 직접 대응 없음(enabler). US-02.3/03.1/03.2(모델), US-06.4(시크릿)를 **뒷받침**
- **완료조건**: 모델·Result·config·프롬프트 로더·LLM 스켈레톤이 임포트 가능하고 계약이 고정됨

### UOW-00 — 데모 데이터셋 〔독립〕
- **책임**: `demo/` 하이브리드 픽스처 — Spring Petclinic Owner 조각 발췌 + 합성 PDF 요구사항 +
  **의도적 value_mismatch**(전화번호 max_length: 요구 20 / OpenAPI 10 / 코드 10) 구성.
- **컴포넌트**: 코드 아님(데이터). C2의 분석 대상 입력.
- **의존**: 없음 (완전 독립, 즉시 착수 가능)
- **스토리**: US-06.1의 데이터 전제(Hero 시나리오), US-02.2/03.3의 검증 입력
- **완료조건**: analyze_project가 소비 가능한 고정 데이터셋 + 최소 1개 Hero Feature·1개 의도적 충돌 포함

### UOW-01 — 스캐너 & 파서 (엔진 기반)
- **책임**: 로컬 스캔·자산 분류·콘텐츠 파싱(소스/MD/텍스트/**PDF**/OpenAPI/SQL/설정/테스트),
  제외규칙, **경로 검증(NFR-SEC-004)**, 부분 실패 허용, 코어 함수 진입점(`scan_project`) 및
  오케스트레이션 골격(S1 파이프라인 스텁 포함).
- **컴포넌트**: C2, (C7 소비)
- **의존**: UOW-0F(Result, config)
- **스토리**: US-01.1, US-01.2, US-01.3
- **완료조건**: `scan_project(path)`가 assets+parse_status 반환, 무효경로 오류처리, 부분실패=warning

### UOW-02 — Feature & Knowledge 생성 (AI 파이프라인 前반부)
- **책임**: `identify_features`(자동), `generate_feature_knowledge`, C4 저장소 I/O
  (`save/load/list/read_resource`, `.trace/knowledge/features/<id>.md`), 캐시.
- **컴포넌트**: C3(identify/generate), C4(저장소), C8 프롬프트(내용)
- **의존**: UOW-0F(모델·LLM·프롬프트 로더), UOW-01(assets)
- **스토리**: US-02.1, US-02.2, US-02.3
- **완료조건**: 데모에서 ≥1 Hero Feature 식별·지식뷰 저장·재실행 시 캐시 활용

### UOW-03 — Claims / Evidence / Conflict (AI 파이프라인 後반부)
- **책임**: `extract_claims`(원자적), `group_evidence`, `assign_confidence`(근거 일치도),
  C5 `detect_conflicts`(value_mismatch P0)·`summarize_conflicts`, `get_conflicts` 조회.
- **컴포넌트**: C3(extract/group/confidence), C5, C4 활용
- **의존**: UOW-0F, UOW-02(Feature/Knowledge 셸) — **Q2=A: 02와 같은 담당, 순차 02→03**
- **스토리**: US-03.1, US-03.2, US-03.3, US-03.4
- **완료조건**: 데모에서 원자 Claim·Evidence·value_mismatch 1건 검출·`get_conflicts` 상세 반환

### UOW-04 — Task Impact Analysis
- **책임**: `analyze_task_impact` — 지식 그라운딩 → Must/Likely/Review(+이유·근거),
  충돌 인지 경고(P1), 순서형 Change Plan. `analyze_task`(C3) step.
- **컴포넌트**: C6, C3(analyze_task), C8 프롬프트
- **의존**: UOW-0F, UOW-02, UOW-03 (지식·충돌 소비)
- **스토리**: US-04.1, US-04.2, US-04.3, US-04.4
- **완료조건**: Hero Task에서 3범주 분류+근거+충돌경고+Change Plan, 소스 자동수정 없음

### UOW-05 — MCP 서버 인터페이스 (얇은 어댑터)
- **책임**: 5개 MCP 도구=코어함수 1:1, 입력스키마 검증, Result 직렬화(핵심 우선 순서),
  지식 리소스(`.trace/knowledge/*.md`) 노출, stdio 전송, (P1)프롬프트 템플릿. S1~S3 배선.
- **컴포넌트**: C1
- **의존**: UOW-0F(Result). **코어 함수 시그니처(component-methods.md)가 UOW-0F에서 고정되므로
  스텁 대비 선개발 가능**; 최종 통합은 UOW-01·02·03·04 필요.
- **스토리**: US-05.1, US-05.2, US-05.3, US-05.4(P1)
- **완료조건**: Claude Code에 5도구 노출·구조화 결과·리소스 조회·stdio 기동

### UOW-06 — 통합 · 신뢰성 · 시연 〔수렴〕
- **책임**: Hero E2E(DoD 앵커), 실패처리·캐시/CLI 폴백(C9), 보안 위생 점검, README(.mcp.json
  스니펫·예제 프롬프트), `result/` 시연 스크린샷.
- **컴포넌트**: 횡단 + C9(CLI)
- **의존**: 전체(UOW-0F~05)
- **스토리**: US-06.1, US-06.2, US-06.3, US-06.4
- **완료조건**: Hero 시나리오 무편집 E2E 통과 + 스크린샷 존재 + 시크릿 위생 확인

---

## 병렬 개발 계획 (Q3=A, 최대 4트랙)

| Wave | 트랙 | 단위 | 병렬 근거 |
|---|---|---|---|
| **0** | 트랙1 | UOW-0F Foundation | 이후 전부의 계약. 짧고 집중. |
| **0** | 트랙2 | UOW-00 데모 데이터셋 | 완전 독립 → 0F와 동시 진행 |
| **1** | 트랙A | UOW-01 스캐너/파서 | 계약 후 독립 |
| **1** | 트랙B | UOW-02 → UOW-03 AI 파이프라인 | **임계경로**, 밀결합 → 단일 담당(억지 병렬 안 함) |
| **1** | 트랙C | UOW-05 MCP 어댑터 | 코어 시그니처 스텁 대비 선개발 |
| **1** | 트랙D | UOW-04 스캐폴딩/프롬프트 or 트랙B 지원 | 계약 대비 선작업, 이후 수렴에서 마감 |
| **2** | — | UOW-04 마감 → UOW-06 통합·시연 | 전체 산출 필요 → 마지막 수렴 |

**병렬화 원칙(사용자 제약)**: Wave 1의 4트랙(A~D)이 실질 병렬 → AI 임계경로 대기 시간에
스캐너·어댑터·데모를 겹쳐 벽시계 시간 단축. 밀결합(02↔03)·수렴(04·06)은 병렬화하지 않는다.

**AI-DLC 진행 순서(per-unit 설계 루프)**: 트랙과 무관하게, 단위별 Functional/NFR/Code 설계는
**0F → 00 → 01 → 02 → 03 → 04 → 05 → 06** 순으로 진행한다(의존성 위상순). 팀은 이 산출된
설계 계약을 근거로 위 웨이브대로 병렬 구현한다.

---

## 검증
- **순환 의존 없음**: 0F(leaf) ← 01 ← 02 ← 03 ← 04; 05·06은 소비측. (상세: unit-of-work-dependency.md)
- **모든 스토리 배정 완료**: 22개 전부 UOW-01~06에 매핑, 0F는 enabler. (상세: unit-of-work-story-map.md)

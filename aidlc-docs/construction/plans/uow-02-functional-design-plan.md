# UOW-02 (Feature & Knowledge 생성) — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (per-unit: UOW-02)
**작성일**: 2026-09-09
**앞 단계 반영**:
- UOW-01 `scan_project_assets(path) -> (list[Asset], warnings)`가 입력 소스(content 포함).
- UOW-0F 계약 소비: `LLMService.complete_structured(prompt, schema)`, `get_prompt(name, **vars)`,
  도메인 모델(Feature/FeatureKnowledge/Claim/Evidence/Conflict), `serialize/deserialize`(MD+YAML), `config`.
- component-methods: `identify_features(assets)->list[FeatureCandidate]`,
  `generate_feature_knowledge(...)`, C4 `save_feature/load_feature/list_feature_summaries/read_resource`.
- 스토리: US-02.1(자동 Feature 식별), US-02.2(지식 뷰), US-02.3(저장/직렬화). NFR-PERF-003(캐시).

> **단위 경계(Q2=A, 02→03 순차·단일 담당)**: UOW-02는 **Feature 식별 + 지식 뷰 셸 저장 + 캐시**까지.
> Claim/Evidence/Confidence/Conflict 채움은 UOW-03. 즉 UOW-02가 만드는 FeatureKnowledge는
> feature+description+related_sources+본문 요약 중심이며, claims/evidence/conflicts는 (이 단계에선)
> 비어 있거나 최소일 수 있고 UOW-03이 보강한다.

---

## 계획 스텝 (체크박스)
- [ ] S1. `FeatureCandidate` 모델 정의(id/title/description/related_sources/rationale)
- [ ] S2. `identify_features(assets)` 알고리즘 — LLM 입력 구성(자산 카탈로그) + 구조화 출력 스키마 + 자동 식별
- [ ] S3. LLM 입력 전략 — 토큰 예산 내에서 자산 content를 어떻게 요약/발췌해 넣을지
- [ ] S4. `generate_feature_knowledge(feature, ...)` — 지식 뷰 본문(body_markdown) 생성 범위(셸 vs 완본)
- [ ] S5. C4 지식 저장소 — `save_feature/load_feature/list_feature_summaries/read_resource` I/O 계약(.trace/knowledge)
- [ ] S6. 캐시(NFR-PERF-003) — 키/무효화/저장 위치(.trace/cache) 정의
- [ ] S7. 저장 위치 기준(.trace 루트) 및 결정성·부분실패(LLM 단계 warning 강등) 규칙
- [ ] S8. business-logic-model / business-rules / domain-entities 산출물 작성

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. Feature 식별 범위/개수 — identify_features를 어떻게 제한할까?
- **A. 자동 식별하되 상한 없음(모델 판단). demo에선 Owner Management(+Pet 등) 자연 도출** — 유연, 결과 수 예측 어려움
- **B. 자동 식별 + 상한(예: 최대 N개, 관련 자산 수 기준 우선순위)** (권장) — 결과 안정·MCP 응답 예측 가능, 데모/성능 친화
- **C. 기타(직접 지정)**

[Answer]:

### Q2. UOW-02의 generate_feature_knowledge 산출 범위 (Q2=A 경계 확인)
- **A. 지식 뷰 '셸' 생성** — feature 요약·related_sources·개요 본문만. claims/evidence/conflicts는 UOW-03이 채워 재저장 (권장) — 단위 경계 명확, 임계경로 단계 분리
- **B. UOW-02에서 claims/evidence까지 한 번에 생성** — 단계 감소, 그러나 UOW-03과 책임 중첩·재작업
- **C. 기타(직접 지정)**

[Answer]:

### Q3. LLM 입력 구성 — 자산 content를 프롬프트에 어떻게 넣을까? (토큰 예산)
- **A. 자산 '카탈로그'(경로+유형+선두 발췌 N줄/문자)를 만들어 식별에 사용, 필요 시 특정 자산 전문은 후속 단계에서** (권장) — 토큰 절약·결정적·확장 가능
- **B. 모든 자산 전문을 그대로 연결해 투입** — 단순하나 토큰 초과·비용·비결정 위험
- **C. 기타(직접 지정)**

[Answer]:

### Q4. 캐시 키/무효화 — 재실행 시 무엇을 기준으로 재사용/무효화할까? (NFR-PERF-003)
- **A. 자산 집합의 콘텐츠 해시(정렬된 rel_path+size+content 해시)를 키로, 변경 시 무효화. .trace/cache에 저장** (권장) — 결정적·정확한 무효화
- **B. mtime/타임스탬프 기반** — 단순하나 결정성·이식성 약함(Q5=A 정신과 상충)
- **C. 캐시 없이 매번 재분석** — 단순하나 NFR-PERF-003 미충족

[Answer]:

### Q5. `.trace` 산출물 루트 위치 기준
- **A. 분석 대상 프로젝트 루트 하위에 `.trace/`(knowledge·cache) 생성** (권장) — 대상별 지식 격리, 재현·정리 쉬움. 스캔 제외규칙에 이미 `.trace` 포함
- **B. TRACE 실행 CWD 또는 사용자 홈 하위** — 중앙 관리, 그러나 프로젝트별 혼선 위험

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-02/functional-design/business-logic-model.md` — 식별→지식생성→저장→캐시 데이터 흐름·알고리즘
- `aidlc-docs/construction/uow-02/functional-design/business-rules.md` — 식별/저장/캐시/부분실패/결정성 규칙
- `aidlc-docs/construction/uow-02/functional-design/domain-entities.md` — FeatureCandidate 등 신규 모델 + 저장소 계약 + 기존 모델 매핑

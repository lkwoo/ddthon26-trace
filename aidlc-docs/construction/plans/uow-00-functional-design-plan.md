# UOW-00 (데모 데이터셋) — Functional Design 계획

**단계**: CONSTRUCTION / Functional Design (per-unit: UOW-00)
**작성일**: 2026-09-09
**앞 단계 반영**: UOW-0F에서 동결한 C4 도메인 모델·직렬화 스키마(Feature/Claim/Evidence/Confidence/Conflict/FeatureKnowledge)를 데이터가 실제로 채울 수 있는지 검증하는 "골든" 입력을 설계한다. Units Generation(UOW-00 §범위 2026-09-09) 결정 = **3 페르소나 흐름 모두 재현**.

> **성격 명시**: UOW-00은 코드가 아닌 **픽스처 데이터**다. 따라서 이 Functional Design은
> "비즈니스 로직"이 아니라 **데이터셋의 논리 구조 = 다운스트림(UOW-01 스캔 / UOW-02·03 AI /
> UOW-04 영향)이 소비하는 입력 계약**을 설계한다. 도메인 엔티티는 UOW-0F에서 이미 동결됐으므로
> 여기서는 (a) 어떤 소스 파일들을 넣을지, (b) 의도적 불일치를 어떻게 심을지, (c) 세 페르소나
> 시나리오 각각을 무엇이 뒷받침하는지를 확정한다.

---

## 설계 목표 (다운스트림 계약)
- analyze_project가 소비 가능한 **고정·결정적** 데이터셋(재실행 시 동일 결과 지향).
- 최소 1개 **Hero Feature** + 최소 1개 **의도적 충돌(value_mismatch, P0)**.
- **P1/P2/P3 각 흐름을 최소 1개 대표 시나리오**로 뒷받침(Units Generation 결정).
- 소스 다양성: Markdown 요구사항, **PDF 요구사항(P0 파서 검증)**, OpenAPI, SQL(DDL), 소스코드, 설정, 테스트.

---

## 계획 스텝 (체크박스)

- [ ] S1. 데이터셋 디렉터리 레이아웃 확정 (`demo/` 하위: `requirements/`, `openapi/`, `db/`, `src/`, `config/`, `tests/`)
- [ ] S2. Hero Feature 확정 및 해당 Feature를 구성하는 소스 자산 목록 정의
- [ ] S3. 의도적 충돌 세트 정의 — value_mismatch(전화번호 max_length) + 페르소나별 추가 충돌/낡은 지식
- [ ] S4. P1/P2/P3 페르소나별 대표 시나리오 ↔ 데이터 자산 매핑표 작성
- [ ] S5. 합성 PDF 생성 방식 확정(리포 커밋 vs 빌드시 생성) 및 PDF 내용 개요
- [ ] S6. Petclinic 발췌 범위·라이선스 표기 방침 확정
- [ ] S7. 데이터셋 매니페스트/README(각 파일이 무엇을 위한 픽스처인지) 설계
- [ ] S8. Functional Design 산출물 3종 작성(business-logic-model=데이터흐름, business-rules=충돌불변식, domain-entities=자산↔모델 매핑)

---

## 확정 필요 질문 (답변은 각 [Answer]: 태그에 기입)

### Q1. 의도적 충돌의 개수/종류 — 세 페르소나를 모두 뒷받침하려면 충돌 1건으로 충분한가?
현재 확정된 것은 **전화번호 max_length value_mismatch**(요구 20 / OpenAPI 10 / 코드 10) 1건이다.
- P1(데브)은 "어디를 바꾸나" → Feature/Impact 중심이라 충돌 1건으로도 흐름 성립.
- P2(마이라)는 "왜 문제가 났나 + 낡은 지식" → 충돌 + **stale knowledge(문서-구현 드리프트)** 사례가 필요.
- P3(피엠)는 "요구사항 바뀌면 파급" → 정책/제약 충돌이 하나 더 있으면 파급 시나리오가 풍부해짐.

- **A. 충돌 1건만(전화번호) 유지, 세 흐름은 같은 충돌을 다른 각도로 사용** — 가장 단순·결정적, 데모 시간 짧음
- **B. 충돌 2건 — 전화번호 value_mismatch + 추가 1건(예: 이메일 필수 여부 요구/코드 불일치)** (권장) — P2/P3 흐름이 각자 대표 충돌을 가짐, 여전히 관리 가능
- **C. 충돌 3건 — 페르소나별 1건씩** — 가장 풍부하나 데이터·검증 부담 큼

[Answer]:

### Q2. 합성 PDF 요구사항 문서를 리포지토리에 어떻게 둘 것인가? (PDF는 P0 파서 대상)
- **A. 완성된 .pdf 바이너리를 `demo/requirements/`에 커밋** (권장) — 데모 재현성 최고, 별도 생성 단계 불필요. (바이너리라 diff 안 됨은 감수)
- **B. Markdown 원본 + 빌드시 PDF 생성 스크립트(reportlab 등)** — diff 가능하나 의존성·생성 단계 추가, 결정성 관리 필요
- **C. 둘 다 — md 원본 보관 + 생성 .pdf도 커밋** — 투명성+재현성, 약간의 중복

[Answer]:

### Q3. Hero Feature를 무엇으로 고정할까? (Petclinic Owner 중심 기결정)
- **A. "Owner 관리"(반려동물 주인 등록/조회) — 전화번호 필드가 자연스럽게 등장** (권장) — 확정된 전화번호 충돌과 정확히 맞물림
- **B. "Pet/Visit 예약"** — 더 복잡하나 전화번호 충돌과 연결이 약함
- **C. 기타(직접 지정)**

[Answer]:

### Q4. Petclinic 코드 발췌 범위 — 실제 spring-petclinic-rest 조각을 얼마나 넣을까?
- **A. Owner 관련 최소 조각만**(REST 컨트롤러 1 + 엔티티/DTO + 매핑 + OpenAPI 일부 + schema.sql 일부) (권장) — 결정적·경량, Hero에 집중
- **B. Owner+Pet 등 인접 도메인까지 확장** — 스캔 다양성↑, 노이즈·용량↑
- **C. 발췌 대신 요구사항에 맞춘 자체 합성 소스** — 라이선스 부담 없음, 그러나 "실제 프로젝트" 설득력↓

[Answer]:

### Q5. 데이터셋 결정성 수준 — 파일 내용을 완전히 고정할까?
- **A. 완전 고정(정적 파일만, 타임스탬프·난수 없음)** (권장) — 데모/테스트 재현성, 캐시 검증 용이
- **B. 일부 동적 생성 허용** — 유연하나 결정성 약화

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-00/functional-design/business-logic-model.md` — 데이터 흐름(자산 → analyze_project → Feature/Claim/Conflict) 및 페르소나 시나리오 경로
- `aidlc-docs/construction/uow-00/functional-design/business-rules.md` — 의도적 충돌 불변식(어떤 값이 어디서 어긋나는지, 검출 기대치)
- `aidlc-docs/construction/uow-00/functional-design/domain-entities.md` — 데모 자산 ↔ UOW-0F 동결 모델 매핑표

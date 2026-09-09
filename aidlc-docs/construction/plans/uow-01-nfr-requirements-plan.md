# UOW-01 (스캐너 & 파서) — NFR Requirements 계획

**단계**: CONSTRUCTION / NFR Requirements (UOW-01)
**작성일**: 2026-09-09
**앞 단계 반영**: Functional Design(BR-PATH/EXCLUDE/CLASSIFY/PARSE/SIZE/FAIL/DET/SEC). 파서 라이브러리는
Q1=A로 이미 확정(pypdf/PyYAML/텍스트). 여기서는 성능 상한·보안·신뢰성·**PBT 속성**을 확정한다.
활성 확장: **Resiliency Baseline**(Blocking, 전면), **Property-Based Testing**(Blocking, 전면).

---

## 계획 스텝 (체크박스)
- [ ] S1. 성능/규모 NFR — 스캔 대상 규모 가정, 상한값(파일당·총량), 동시성 필요 여부
- [ ] S2. 신뢰성 NFR (Resiliency 확장) — 부분 실패/폴백 정책을 FR-ANALYSIS-003과 정합화
- [ ] S3. 보안 NFR — NFR-SEC-004(경로검증) 외 심볼릭/트래버설/메시지 위생 요구 확정
- [ ] S4. 유지보수 NFR — 파서 확장성(새 유형 추가 지점), 상수/설정 분리
- [ ] S5. **PBT 속성(Property-Based Testing) 대상** 확정 — 어떤 불변식을 속성으로 검증할지
- [ ] S6. nfr-requirements.md / tech-stack-decisions.md 작성 + 확장 컴플라이언스 요약

---

## 확정 필요 질문 (답변은 [Answer]: 태그에 기입)

### Q1. 스캔 규모/성능 목표 — 어느 정도 규모를 상정하고 최적화할까?
- **A. 로컬 소·중 프로젝트(수천 파일 이내) 단일 스레드 순차 스캔으로 충분. 명시적 성능 SLA 없음(합리적 시간)** (권장) — 데모/로컬 도구 성격, 단순·결정적. 병렬화는 과설계
- **B. 대규모 대비 동시/병렬 파싱 도입** — 처리량↑, 결정성·복잡도·디버깅 비용↑
- **C. 기타(직접 지정)**

[Answer]:

### Q2. 파일당/총량 크기 상한 기본값
- **A. 파일당 1MB(초과 truncate+partial), 총량 상한 없음(제외규칙으로 충분)** (권장) — 데모 규모에 안전, 메모리 예측 가능
- **B. 파일당 5MB / 총량 200MB 등 더 큰 상한** — 큰 문서 수용, 메모리↑
- **C. 기타(직접 지정)**

[Answer]:

### Q3. PBT(속성 기반 테스트) 대상 속성 — 무엇을 불변식으로 검증할까? (복수 선택 가능)
활성 PBT 확장(전면)에 따라 스캐너/파서 핵심 불변식을 hypothesis로 검증한다. 아래 후보:
- **A. 분류 전결정성**: 임의 파일명/확장자 입력에 대해 classify가 항상 유효한 AssetType 하나를 반환(예외/None 없음)
- **B. 경로 안전성**: 루트 밖 경로/트래버설(`../`)·심볼릭 탈출 입력이 결과 자산에 절대 포함되지 않음 (NFR-SEC-004)
- **C. 부분 실패 격리**: 임의로 일부 파일을 깨뜨려도 scan은 예외 없이 완료하고, 깨진 파일만 failed로 표시(전체 중단 없음)
- **D. 결정성/멱등**: 동일 디렉터리를 2회 스캔하면 assets(순서 포함)가 동일

선택(권장: **A,B,C,D 전부** — 스캐너 핵심 계약을 모두 커버):

[Answer]:

### Q4. 크기 상한 등 스캔 설정을 어디서 관리할까?
- **A. `config`(C7, UOW-0F)에 스캔 설정 항목 추가(get_scan_settings 또는 상수 모듈)** (권장) — 설정 분리(유지보수성), 기존 config 계층 재사용
- **B. engine 내부 상수로 하드코딩** — 단순하나 설정 분리 원칙 약화

[Answer]:

---

## 산출물(승인 후 생성)
- `aidlc-docs/construction/uow-01/nfr-requirements/nfr-requirements.md`
- `aidlc-docs/construction/uow-01/nfr-requirements/tech-stack-decisions.md`

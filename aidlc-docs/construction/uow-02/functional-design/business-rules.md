# UOW-02 (Feature & Knowledge) — 비즈니스 규칙 (business-rules)

**단계**: CONSTRUCTION / Functional Design (UOW-02)
**작성일**: 2026-09-09
**출처**: US-02.1/02.2/02.3, FR-KNOWLEDGE-001/002/003, FR-STORAGE-001, NFR-PERF-003, §17.4(부분실패)

---

## BR-IDF — Feature 식별 (US-02.1, Q1=B, Q3=A)
- **BR-IDF-001**: identify_features는 **자동**. 사람이 목록을 주지 않는다(FR-KNOWLEDGE-001).
- **BR-IDF-002 (입력, Q3=A)**: LLM 입력은 자산 **카탈로그**(rel_path+asset_type+선두 발췌). 발췌 길이 상한
  (기본 1200자)으로 토큰 예산 관리. content 없는 자산(skipped/failed)은 카탈로그에서 제외.
- **BR-IDF-003 (상한, Q1=B)**: 결과 Feature 수 상한 `max_features`(기본 예: 12). 초과 시 관련 자산 수가 많은
  순으로 우선. 상한은 config/scan과 별개의 UOW-02 설정 또는 인자.
- **BR-IDF-004 (id 안전)**: FeatureCandidate.id는 파일/URI 안전(케밥, `/\..` 금지). LLM이 위반하면
  title로부터 slug 재생성(소문자·공백→-·비허용문자 제거).
- **BR-IDF-005 (중복 제거·정렬)**: 동일 id 후보는 병합/제거. 최종 목록은 id 사전순(결정성).

## BR-KN — 지식 뷰 생성 (US-02.2, Q2=A 셸)
- **BR-KN-001**: UOW-02의 generate_feature_knowledge는 **셸**을 만든다 —
  Feature(id/title/description/related_sources) + `body_markdown`(개요). claims/evidence/conflicts=[].
- **BR-KN-002**: body_markdown은 사람이 읽는 개요(기능 요약·관련 자산·"상세 근거는 분석 진행 중" 안내).
  LLM 생성 실패 시 템플릿 기반 최소 본문으로 폴백(+warning) — 저장은 계속(BR-FAIL 참조).
- **BR-KN-003**: meta에 `{model, sources: len(related_sources), stage: "knowledge-shell"}` 기록.

## BR-STORE — 저장소 I/O (US-02.3, FR-STORAGE-001)
- **BR-STORE-001**: 저장 경로 `<project_root>/.trace/knowledge/features/<feature_id>.md`(Q5=A). 디렉터리
  없으면 생성하되 항상 루트 하위(트래버설 금지, UOW-01 is_within_root 정합).
- **BR-STORE-002**: 저장 포맷은 UOW-0F `serialize`(YAML front matter + Markdown 본문, 단일 진실원).
  로드는 `deserialize`. 역직렬화 실패(손상)는 StorageError(로드 거부).
- **BR-STORE-003**: list_feature_summaries는 features/*.md 를 로드해 FeatureSummary(id/title/confidence/
  conflicts_count/related_sources) 생성. 손상 파일 1개가 전체 목록을 막지 않음(해당 파일 skip+warning).
- **BR-STORE-004 (리소스)**: read_resource("trace://feature/<id>")는 body_markdown 반환. 미존재→StorageError.
- **BR-STORE-005 (멱등 저장)**: 동일 id 재저장은 덮어쓰기. serialize는 round-trip 멱등(UOW-0F 보장).

## BR-CACHE — 캐시 (NFR-PERF-003, Q4=A)
- **BR-CACHE-001**: 캐시 키 = 자산 집합 콘텐츠 해시 `compute_assets_hash`(정렬된 rel_path+size+content sha256).
  타임스탬프/절대경로 미사용(결정성, Q5=A 정신).
- **BR-CACHE-002**: analyze 진입 시 현재 자산 해시로 캐시 조회 → 히트면 LLM 재호출 없이 저장된 Feature/지식
  재사용. 미스면 식별·생성 후 캐시에 기록.
- **BR-CACHE-003**: 자산이 바뀌면 해시가 달라져 자동 무효화(부분 무효화는 하지 않음 — 전체 재분석).
- **BR-CACHE-004**: 캐시 저장 위치 `<project_root>/.trace/cache/<hash>.json`. 손상/파싱 실패 시 미스로 간주(재분석).

## BR-FAIL — 부분 실패 (§17.4, FR-ANALYSIS-003 정신)
- **BR-FAIL-001**: 특정 Feature의 지식 생성 LLM 단계 실패(LLMValidationError 등)는 **그 Feature만** warning으로
  강등하고 나머지는 계속. 전체 파이프라인 중단 없음.
- **BR-FAIL-002**: identify_features 자체가 실패하면(구조화 검증 소진) 빈 목록 + warning으로 강등(analyze는 계속,
  단 결과 features=0). 예외를 상위로 던지지 않는다(어댑터가 Result로 표현).
- **BR-FAIL-003**: 모든 실패는 `Warning(code, message, source=feature_id 또는 catalog)`로 수집.

## BR-DET — 결정성
- **BR-DET-001**: LLM 결정성 파라미터(temperature=0, seed)는 settings에서만(UOW-0F). 프롬프트도 자산 정렬 순서로
  구성해 동일 입력→동일 프롬프트.
- **BR-DET-002**: 저장/목록/캐시의 순서·키는 정렬 기반(재현성).

## BR-SEC — 보안 위생
- **BR-SEC-001**: 경고/오류·로그에 자산 원문·시크릿을 노출하지 않는다(rel_path·feature_id·코드만).
- **BR-SEC-002**: 프롬프트에 넣는 발췌는 카탈로그 상한 내로 제한(대량 원문 유출/토큰 폭증 방지).

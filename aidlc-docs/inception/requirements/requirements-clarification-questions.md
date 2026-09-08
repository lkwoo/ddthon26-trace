# Requirements Clarification Questions — Dual-Interface Knowledge Store

답변을 분석한 결과, 아키텍처를 확정하기 위해 해소가 필요한 **모순/모호함**이 발견되었습니다.
각 `[Answer]:` 태그 뒤에 알파벳을 적어 주시고, 끝나면 "완료"라고 알려 주세요.

---

## 모순 1: 임베딩 벡터의 생성 주체 (Q2 / 요구사항 2.3 vs Q3)

Q2에서 **SQLite + 벡터 확장(sqlite-vec)으로 벡터 유사도**를 선택하셨고, 요구사항 2.3/3.3.2는 **코드(함수/클래스)-문서 청크 간 임베딩/벡터 유사도 기반 관계 연결**을 명시합니다. 이는 **실제 임베딩 벡터(숫자 배열)** 가 저장되어 있어야 동작합니다.
(참고: Q9는 A→B로 변경되어 청크 버전 매칭은 해시/텍스트 유사도 기반이 되었으므로, 버전 매칭 자체는 임베딩을 요구하지 않습니다. 다만 Q2와 2.3의 벡터 유사도 관계 연결은 여전히 임베딩이 필요합니다.)

그런데 Q3에서는 **"별도 LLM을 호출하지 않고, 대상 프로젝트의 Agent가 직접 임베딩·요약을 수행"** 하도록 선택하셨습니다. 여기서 기술적 쟁점이 있습니다: LLM Agent(예: Claude)는 **요약(텍스트 생성)** 은 잘 수행하지만, **임베딩 벡터 자체를 직접 산출하지는 못하는 것**이 일반적입니다(임베딩은 보통 별도의 임베딩 모델/함수가 필요). 따라서 "Agent가 직접 임베딩"의 구체적 구현 방식을 확정해야 합니다.

### Clarification Question 1
임베딩 벡터는 어떻게 확보하시겠습니까?

A) 서버에 **경량 로컬 임베딩 모델**을 내장(예: sentence-transformers/fastembed 등 소형·오프라인)하여 벡터 생성 — "별도 LLM API 호출은 없음" 유지하되 임베딩은 로컬 함수로 수행 (sqlite-vec와 정합)

B) **벡터 임베딩을 아예 사용하지 않고**, 관계 연결·검색·버전 매칭을 **Agent의 판단(요약/의미 비교) + 텍스트 유사도(해시/편집거리)** 로 대체 — 이 경우 Q2의 sqlite-vec 벡터 유사도와 Q9의 임베딩 매칭은 각각 "텍스트 유사도"로 변경됨

C) MCP 도구로 **Agent가 임베딩 값을 제공**(Agent 환경에 임베딩 수단이 있다고 가정)하면 서버는 저장·유사도 계산만 담당 — Agent가 임베딩을 제공하지 못하면 (A)의 로컬 임베딩으로 폴백

X) Other (please describe after [Answer]: tag below)

[Answer]: 서버에 **경량 로컬 임베딩 모델**을 내장(예: sentence-transformers/fastembed 등 소형·오프라인)하여 벡터 생성 — "별도 LLM API 호출은 없음" 유지하되 임베딩은 로컬 함수로 수행 (sqlite-vec와 정합)

---

## 모호함 2: 요약(Summarization) 및 인제스천(Ingestion) 트리거 방식 (Q3 파생)

Q3에 따라 서버가 LLM을 직접 호출하지 않는다면, **요약 생성**과 **인제스천(수집→청킹→관계구축→요약)** 을 누가 언제 촉발하는지 확정이 필요합니다.

### Clarification Question 2
인제스천/요약 파이프라인의 실행 방식은 무엇으로 하시겠습니까?

A) **Agent 주도(interactive)**: 서버는 청킹·파싱·저장·검색 등 결정론적 작업을 MCP 도구로 제공하고, 요약 텍스트는 Agent가 도구 결과를 받아 생성한 뒤 다시 도구로 저장 (LLM-free 서버 원칙에 부합)

B) **하이브리드**: 코드 파싱·청킹·관계구축(결정론적)은 서버가 자동 수행하고, 요약만 Agent가 필요 시 생성·저장

C) 요약은 MVP에서 **선택적/후순위**로 두고, 우선 구조·청크·관계·검색만 제공

X) Other (please describe after [Answer]: tag below)

[Answer]: **Agent 주도(interactive)**: 서버는 청킹·파싱·저장·검색 등 결정론적 작업을 MCP 도구로 제공하고, 요약 텍스트는 Agent가 도구 결과를 받아 생성한 뒤 다시 도구로 저장 (LLM-free 서버 원칙에 부합)

---

## 모호함 3: 설치 스크립트의 세부 동작 (Q6)

Q6에서 "만들어진 시스템 구조를 대상 프로젝트 폴더에 복사 후, 환경에 맞는 MCP 설정을 자동 추가하는 스크립트 + Agent가 읽을 수 있는 README.md"를 요청하셨습니다. 아래 세부 사항을 확정해 주세요.

### Clarification Question 3-1
지식 저장소 데이터(그래프/청크/인덱스 DB 파일)는 어디에 위치시키겠습니까?

A) 대상 프로젝트 내부 숨김 디렉토리 (예: `.knowledge-store/` 또는 `.aidlc-knowledge/`)

B) 대상 프로젝트 내부 일반 디렉토리 (예: `knowledge-store/`)

C) 사용자 홈/전역 위치에 프로젝트별로 분리 저장

X) Other (please describe after [Answer]: tag below)

[Answer]: 대상 프로젝트 내부 숨김 디렉토리 (예: `.knowledge-store/` 또는 `.aidlc-knowledge/`)

### Clarification Question 3-2
설치 스크립트가 자동 설정할 **MCP 클라이언트 대상**은 무엇입니까? (복수 선택은 X에 기재)

A) Claude Code (프로젝트 루트 `.mcp.json`)

B) Claude Desktop (`claude_desktop_config.json`)

C) 범용: MCP 설정 스니펫을 생성해 README에 안내하고, 감지되는 클라이언트가 있으면 자동 반영

X) Other (please describe after [Answer]: tag below)

[Answer]: Claude Code (프로젝트 루트 `.mcp.json`) 또는 opencode

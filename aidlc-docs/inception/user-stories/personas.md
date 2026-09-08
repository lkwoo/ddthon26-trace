# 페르소나 — Dual-Interface Knowledge Store

**출처**: `aidlc-docs/inception/requirements/requirements.md`
**스토리 매핑**: `aidlc-docs/inception/user-stories/stories.md`

본 시스템은 하나의 지식 저장소를 공유하되, 서로 다른 방식으로 상호작용하는 세 종류의 사용자를 대상으로 한다.

---

## P1. Agent (자율 LLM 소비자)

- **대표 대상**: Claude Code, opencode 등 MCP 클라이언트로 동작하는 자율 LLM 에이전트.
- **접점**: MCP over **stdio** — Resources(Structure/Summary/Relationship)와 Tools(Semantic Query, Smart Snippet, Ingestion/Update).
- **목표(Goals)**:
  - 최소 토큰으로 작업에 필요한 정확한 컨텍스트(코드 범위·요약·관계)를 얻는다.
  - 시스템의 존재와 도구 사용법을 **스스로 발견**하여 적절한 시점에 자율 호출한다.
  - 문서/코드 수집·청킹 결과를 받아 요약을 생성하고 다시 저장한다(interactive ingestion).
- **불편(Pains)**:
  - 파일 전체를 읽어 컨텍스트 윈도를 낭비하는 것.
  - 도구 설명이 모호해 언제·어떻게 쓸지 알 수 없는 것.
  - 조회 지연으로 에이전트 루프가 끊기는 것.
- **기술적 맥락**: 임베딩 벡터를 자체 생성하지 못함(서버 내장 로컬 임베딩에 의존). 결정론적 결과와 명확한 입출력 스키마를 선호.
- **성공 신호(Success Signals)**: 핵심 조회 1초 이내 응답, 토큰 예산에 맞춘 스니펫, 별도 안내 없이 도구 발견·활용.
- **관련 Epic**: E1, E3, E4, E5, E6, E9.

---

## P2. Developer / Knowledge Reviewer (사람 검토자)

- **대표 대상**: 대상 프로젝트를 이해·검토하려는 개발자/지식 관리자.
- **접점**: 정적 **HTML + D3** Web Viewer (file:// 또는 로컬 서빙).
- **목표(Goals)**:
  - 디렉토리 및 논리적 의존 구조를 시각적으로 탐색한다.
  - 코드 간 관계를 그래프로 파악한다.
  - 마크다운 기반 위키 콘텐츠를 읽고, 엔진/Agent가 자동 생성·갱신한 내용을 검토·확인한다.
- **불편(Pains)**:
  - 텍스트만으로 대규모 코드베이스 구조를 파악하기 어려움.
  - 자동 생성 내용의 최신성/정확성을 신뢰하기 어려움.
- **기술적 맥락**: 빌드 도구 없이 브라우저로 바로 열람. 오프라인/로컬 환경.
- **성공 신호(Success Signals)**: 접이식 트리·의존 그래프·위키 뷰어로 구조를 빠르게 이해하고, 갱신 결과를 검토할 수 있음.
- **관련 Epic**: E7.

---

## P3. Installer / Maintainer (설치·유지보수자)

- **대표 대상**: 시스템을 대상 프로젝트에 도입·운영하는 개발자/DevOps.
- **접점**: 복사형 설치 스크립트, `README.md`, `.knowledge-store/`, MCP 설정 파일(`.mcp.json`/opencode).
- **목표(Goals)**:
  - 최소한의 사전 요구사항으로 시스템을 대상 프로젝트에 복사·설치한다.
  - Claude Code/opencode에 MCP 설정이 자동으로 추가되게 한다.
  - 대규모 리팩토링 후 재인덱싱으로 지식 저장소를 최신 상태로 유지한다.
- **불편(Pains)**:
  - 복잡한 수동 설정, 불명확한 사전 요구사항.
  - 지식 데이터가 프로젝트를 오염시키는 것(위치/가시성 문제).
- **기술적 맥락**: 파일시스템 기반 로컬/네트워크 드라이브, Git 사용 환경. 감지 실패 시 README 수동 스니펫으로 대체.
- **성공 신호(Success Signals)**: 스크립트 실행 수준의 설치, 자동 MCP 설정, `.knowledge-store/` 숨김 디렉토리에 데이터 격리.
- **관련 Epic**: E8, E9.

---

## 페르소나 ↔ Epic 요약 매핑

| Epic | P1 Agent | P2 Reviewer | P3 Installer |
|---|:---:|:---:|:---:|
| E1 Ingestion & Chunking | ● | | |
| E2 Code Structure | ○(간접) | ○(간접) | |
| E3 Relationships | ● | ○(간접) | |
| E4 Versioning | ● | ○(검토) | |
| E5 Summarization | ● | ○(검토) | |
| E6 MCP Interface | ● | | |
| E7 Web Viewer | | ● | |
| E8 Installation | ○(호출) | | ● |
| E9 User-observable NFRs | ● | ○ | ● |

● 주요 대상 · ○ 부차/간접 대상

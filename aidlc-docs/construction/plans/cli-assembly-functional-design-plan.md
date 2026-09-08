# Functional Design Plan — U4 CLI & Assembly

> **Unit**: U4 CLI & Assembly (조립 루트/진입점) · **Depends on**: U1, U2, U3
> **Stories**: US-A6(serve-mcp), US-E1(ingest), US-E5(sync), US-N7(규모·소요 출력), serve-web(US-H*)
> **Principle**: 구현체 선택·주입은 **오직 여기서**. CLI는 서브커맨드→조립된 서비스 호출. 로직 미보유(위임).

## Steps
- [x] S1. Unit/스토리 분석
- [x] S2. 설계 질문 + 권장안 채택(자동)
- [x] S3. domain-entities.md — CLI 서브커맨드/인자 모델
- [x] S4. business-logic-model.md — config DI 조립 + CLI dispatch 흐름
- [x] S5. business-rules.md — 조립 격리·종료코드·출력 규칙
- [x] S6. 완료 + 승인(자동 채택)

## 설계 질문 및 채택 답변 (권장안 자동 채택)

### Q1. CLI 파서
- A. stdlib `argparse` 서브커맨드(`ingest`/`sync`/`serve-mcp`/`serve-web`) **(권장)**
- B. 외부 CLI 라이브러리(click/typer)
- **[Answer]: A** — 최소 의존성. 엔진 무외부호출 원칙과 정합.

### Q2. 조립 루트 위치
- A. `config.py`에 `AppConfig`(경로/포트 등) + `assemble(config)`가 구현체 바인딩·주입, `__main__.py`는 argparse→config→assemble→dispatch만 **(권장)**
- B. `__main__`에서 직접 조립
- **[Answer]: A** — 컴포넌트 직접 결합 방지, 단위 테스트 가능(조립 함수 검증).

### Q3. ingest vs sync 구분 (US-E1/E5)
- A. `ingest`=최초 full 동기화, `sync`=증분 resync(기본), `--full` 플래그로 강제 full **(권장)**
- B. 단일 명령
- **[Answer]: A** — 둘 다 `SyncService.run`에 mode 매핑. US-E5 명시적 실행.

### Q4. 출력 형식 (US-N7)
- A. SyncReport를 사람이 읽는 요약(파일/심볼 수·skip/실패·소요 ms) + `--json` 시 JSON 출력 **(권장)**
- **[Answer]: A** — 규모·소요 가시성(US-N7). 스크립트 연동은 --json.

### Q5. 저장/소스 경로 설정
- A. `--project`(소스 루트, 기본 cwd), `--store`(KB 디렉토리, 기본 `.agentic_kb`) 인자 **(권장)**
- **[Answer]: A**

### Q6. 종료 코드
- A. 성공 0, 사용법 오류 2(argparse), 실행 실패(치명) 1. sync 부분 실패(파일 단위)는 0 유지하되 실패 목록 출력 **(권장)**
- **[Answer]: A** — 부분 실패는 격리(US-E/BR-3)라 전체 실패 아님.

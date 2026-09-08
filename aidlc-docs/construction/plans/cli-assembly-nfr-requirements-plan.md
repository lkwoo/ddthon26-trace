# NFR Requirements Plan — U4 CLI & Assembly

## Steps
- [x] S1. Functional Design 분석
- [x] S2. NFR 질문 + 권장안 채택(자동)
- [x] S3. nfr-requirements.md
- [x] S4. tech-stack-decisions.md
- [x] S5. 완료 + 승인(자동)

## 질문 및 채택 답변 (권장안 자동 채택)
### Q1. CLI 프레임워크
- A. stdlib `argparse` (최소 의존) **(권장)** — **[Answer]: A**
### Q2. 테스트
- A. main(argv) 종료 코드/출력 + assemble() 배선 예제 테스트(capsys). PBT는 U1 집중 **(권장)** — **[Answer]: A**
### Q3. 선택 의존성 격리
- A. mcp/web 서버 기동은 커맨드 실행 시 지연 import(미설치 시 안내) **(권장)** — **[Answer]: A**
### Q4. 성능
- A. 조립·CLI 오버헤드 무시 수준. 동기화 시간은 U1이 지배 **(권장)** — **[Answer]: A**

# NFR Design Patterns — U2 MCP Server

> **단계**: CONSTRUCTION – NFR Design · **Unit: U2 MCP Server** · 2026-09-08

## 1. Inbound Adapter (Hexagonal)
- U2는 헥사고날의 **인바운드 어댑터**. 도메인/유즈케이스는 U1이 소유하고, U2는 프로토콜(MCP) ↔ U1 서비스 경계를 번역.
- **패턴**: Adapter + Delegation. provider는 U1 Application 서비스 인터페이스에만 결합(NFR-U2-M1).

## 2. SDK 격리 (Ports & Bindings)
- **패턴**: Humble Object. `resources/tools/prompts` provider는 SDK 독립 순수 매핑 함수(테스트 가능). `server.py`가 유일한 `mcp` SDK 바인딩(얇은 껍데기).
- 효과: MCP SDK 버전/변경이 매핑 로직으로 새지 않음(NFR-C2, NFR-U2-M1/M2).

## 3. 오류 격리 (Fault Isolation)
- **패턴**: Boundary error translation. 각 핸들러는 try/except 경계로 하위 예외를 포착 → Resource는 not-found 신호, Tool은 `isError` 결과로 변환.
- **불변식**: 어떤 단일 요청도 서버 프로세스를 종료시키지 않음(NFR-U2-A1, BR-M4/M8).
- Null-object 승계: U1 read 서비스가 None 반환 → U2가 not-found로 매핑(US-A1 AC-4).

## 4. 표면 계측 (Observability)
- **패턴**: Decorator(Context manager). 각 핸들러를 U1 `measure(name)`로 감싸 elapsed_ms 로깅. 응답에 영향 없음(NFR-U2-P2, US-N1).
- 계측 이름: `mcp.resource.<kind>`, `mcp.tool.<name>`.

## 5. 무상태 동시성
- **패턴**: Stateless handler. provider는 가변 공유 상태 없이 요청별 U1 서비스에 위임 → stdio 순차 처리에서 경합 없음(NFR-U2-C1).

## 6. 직렬화 일관성
- U1 `to_dict()`(결정적, sort_keys 정합) 재사용 → 저장/전송 표현 일관(BR-M9).

## 7. 보안 위생 (Baseline OFF)
- 경로 confinement는 U1 어댑터(BR-4)가 최종 보증. U2는 target 전달만. 인증/시크릿 없음(로컬 stdio). Security/Resiliency 확장 N/A.

## 8. 테스트 설계
- provider 단위 테스트: 목 U1 서비스 주입, URI 파싱·디스패치·오류 매핑 예제 검증(PBT-10).
- SDK 바인딩(server.py)은 조립/스모크 수준으로 Build & Test 단계에서 통합 검증.

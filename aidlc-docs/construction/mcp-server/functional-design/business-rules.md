# Business Rules — U2 MCP Server

> U2 규칙은 **위임 어댑터**로서의 계약을 규정한다. 모든 규칙은 "로직 미보유·위임·서버 미중단"이라는 상위 원칙에 종속된다. (U1 BR-* 를 이어 BR-M* 로 번호화)

## 위임/경계 규칙
- **BR-M1 (로직 미보유)**: U2는 검색/추출/저장/병합 로직을 구현하지 않는다. 오직 U1 Application 서비스에 위임한다.
- **BR-M2 (엔진 LLM 미호출)**: U2는 LLM/외부 API를 호출하지 않는다. 자연어 심화 요약은 에이전트가 `update_note`로 제출한다(NFR-C3, US-A4).
- **BR-M3 (포트 의존)**: provider는 U1 서비스 인터페이스에만 결합한다. 구현 선택/주입은 U4 조립 루트에서만 이뤄진다.

## URI/입력 규칙
- **BR-M4 (Resource 미존재)**: 알 수 없는 URI, 미인제스천/미존재 `{target}`은 not-found 신호를 반환하고 **서버는 중단되지 않는다**(US-A1 AC-4).
- **BR-M5 (URI 파싱)**: URI는 스킴 `agentic-kb://` 접두 후 `structure` / `summary/{target}` / `relationships[/{target}]` 로만 해석한다. `{target}`은 URL-decode 후 그대로 서비스에 전달(경로 confinement는 U1 어댑터 BR-4가 최종 보증).
- **BR-M6 (Tool 인자 검증)**: 필수 키 누락·타입 불일치 시 `isError` 결과를 반환하고 하위 서비스를 호출하지 않는다. `update_note`의 페이로드 유효성 최종 판정은 U1 `UpdateService`(BR-21)가 수행하며, KB는 검증 실패 시 변경되지 않는다(US-A4 AC-3).

## 응답/오류 규칙
- **BR-M7 (결과 없음 무오류)**: `query` 매칭 없음은 오류가 아니라 `{results: []}` 로 반환한다(US-A2 AC-3).
- **BR-M8 (예외 격리)**: 하위 서비스에서 발생한 예외는 핸들러가 포착하여 `isError` 결과(또는 Resource not-found)로 변환한다. 어떤 단일 요청 실패도 서버 프로세스를 종료시키지 않는다.
- **BR-M9 (직렬화 일관성)**: 모든 반환 페이로드는 U1 도메인 모델의 `to_dict()`(결정적, sort_keys 저장 규칙과 정합)를 사용한다.

## 계측/운영 규칙
- **BR-M10 (표면 계측)**: 각 Resource/Tool 핸들러는 `measure()`로 감싸 elapsed_ms를 로깅한다. 계측은 응답 내용에 영향을 주지 않는다(US-N1).
- **BR-M11 (로컬 stdio)**: 서버는 stdio 전송으로만 기동하며 외부 네트워크 서비스에 의존하지 않는다(파서/LLM 호출 제외 — 본 아키텍처에선 LLM도 미호출)(US-A6 AC-2, NFR-E1).

## Prompt 규칙
- **BR-M12 (정적 프롬프트)**: Prompt 템플릿은 인자를 텍스트에 삽입하는 순수 조합이며 외부/LLM 호출이 없다. 미지원 name은 prompt not-found.

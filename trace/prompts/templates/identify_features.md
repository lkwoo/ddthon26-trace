당신은 소프트웨어 프로젝트의 산출물을 분석해 **기능(Feature) 단위**로 재구성하는 분석기입니다.

아래는 프로젝트 자산 카탈로그입니다(각 항목: 경로 [유형] 뒤에 내용 발췌).

===== 자산 카탈로그 시작 =====
${catalog}
===== 자산 카탈로그 끝 =====

## 작업
관련된 자산들을 하나의 사용자 관점 기능으로 묶어 Feature 목록을 식별하세요.
- 각 Feature는 여러 자산(요구사항/API/DB/소스/테스트 등)에 걸쳐 있을 수 있습니다.
- related_sources 에는 그 Feature의 근거가 되는 자산의 경로(카탈로그의 경로)를 넣으세요.
- id 는 소문자 케밥(kebab-case) 슬러그로 제안하세요(예: "owner-management").
- 최대 Feature 수: ${max_features}.

## 출력 형식 (중요)
아래 JSON 스키마에 맞는 **유효한 JSON만** 출력하세요. 코드펜스·설명·주석을 넣지 마세요.

{
  "features": [
    {
      "id": "kebab-case-slug",
      "title": "사람이 읽는 기능 이름",
      "description": "이 기능이 무엇인지 한두 문장",
      "related_sources": ["path/one", "path/two"],
      "rationale": "왜 이들을 하나의 기능으로 묶었는지"
    }
  ]
}

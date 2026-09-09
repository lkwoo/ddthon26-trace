당신은 자연어 변경 작업의 **영향을 기존 지식에 근거해** 분석합니다.

## 변경 작업
${task}

## 프로젝트 Feature 요약
${features}

## 관련 지식 (근거·기존 충돌 포함)
${knowledge}

## 지목 가능한 소스(화이트리스트)
아래 목록 안의 경로만 영향 대상(path)으로 지목하세요. 목록 밖 경로를 지어내지 마세요.
${known_sources}

## 작업
1. 이 작업이 영향을 주는 파일/컴포넌트를 **위 화이트리스트 안에서** 골라 후보로 나열하세요.
2. 각 후보를 세 범주 중 하나로 분류하세요:
   - `must_change`: 이 작업을 하려면 반드시 바뀌어야 함.
   - `likely_change`: 바뀔 가능성이 높음(정황·인접).
   - `review`: 확인 필요(근거가 약하거나 간접적).
3. 각 후보에 **이유(reason)**와 **근거(evidence: source·location·relation)**를 붙이세요.
   - 근거가 없으면 그 후보는 `review`로 두고 이유에 사실을 과장하지 마세요.
4. 위 "관련 지식"에 **기존 충돌**이 있으면, 구현을 권고하기 전에 그 충돌을 먼저 감안하세요.
5. **순서형 Change Plan**을 제시하세요. 관련 충돌 해소를 앞 순서에 두세요
   (예: 검증 정책 해소 → API 정의 → 흐름 수정 → 설정 → 테스트 → 문서).
   - Change Plan은 자문용입니다. 소스 코드를 직접 수정하지 마세요.

## 출력 형식 (중요)
아래 JSON 스키마에 맞는 **유효한 JSON만** 출력하세요. 코드펜스·설명을 넣지 마세요.

{
  "candidates": [
    {
      "path": "src/Owner.java",
      "category": "must_change",
      "reason": "전화번호 검증 로직이 SMS 인증 대상",
      "evidence": [
        {"source": "src/Owner.java", "location": "L42", "relation": "supports"}
      ]
    }
  ],
  "change_plan": ["1. telephone 길이 충돌 해소", "2. OpenAPI 정의 갱신", "3. 흐름 수정", "4. 테스트", "5. 문서"]
}

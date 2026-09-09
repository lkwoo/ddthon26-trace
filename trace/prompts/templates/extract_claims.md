당신은 하나의 소프트웨어 기능에 대한 **원자 Claim과 근거(Evidence)**를 추출합니다.

## 대상 기능
- 이름: ${feature_title}
- 설명: ${feature_description}

## 관련 자산(발췌)
${sources}

## 작업
관련 자산을 근거로, 이 기능에 대한 **원자적 사실(Claim)**을 추출하세요.
- Claim은 **원자적**이어야 합니다: `subject`(무엇의) + `predicate`(어떤 속성) 하나.
  - 복합 문장은 분리하세요. 예: "telephone은 20자이고 필수" → (telephone, max_length), (telephone, required) 2개.
- 각 Claim에는 그 값을 관측한 **모든 소스별 Evidence**를 붙이세요.
  - `source`: 반드시 위 발췌에 나온 자산의 경로(rel_path). 존재하지 않는 소스를 지어내지 마세요.
  - `type`: source / openapi / sql / config / test / markdown / pdf / text 중 하나.
  - `location`: 파일 내 위치 표기(예: "L42", "p.3", "paths./owners"). 원문을 길게 복사하지 마세요.
  - `extracted_value`: 그 소스에서 관측된 값(예: "20", "10"). 요구되는 대상이 **소스에 없으면** "absent".
  - `relation`: supports(값 지지) / contradicts(값 상충·부재) / mentions(값 없이 언급).
- 서로 다른 소스가 다른 값을 말하면(예: 문서 20 vs 코드 10) 그대로 각각의 Evidence로 남기세요 — 판단은 시스템이 합니다.

## 출력 형식 (중요)
아래 JSON 스키마에 맞는 **유효한 JSON만** 출력하세요. 코드펜스·설명을 넣지 마세요.

{
  "claims": [
    {
      "subject": "owner.telephone",
      "predicate": "max_length",
      "evidence": [
        {"source": "docs/spec.pdf", "type": "pdf", "location": "p.3", "extracted_value": "20", "relation": "supports"},
        {"source": "src/Owner.java", "type": "source", "location": "L42", "extracted_value": "10", "relation": "contradicts"}
      ]
    }
  ]
}

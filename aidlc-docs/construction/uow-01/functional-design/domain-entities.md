# UOW-01 (스캐너 & 파서) — 도메인 엔티티 (domain-entities)

**단계**: CONSTRUCTION / Functional Design (UOW-01)
**작성일**: 2026-09-09
**결정 반영**: Q1=A(pypdf/PyYAML/텍스트), Q2=A(텍스트 추출까지), Q3=A(확장자+내용 판별), Q4=A(eager+상한), Q5=A(Result엔 메타만)

> UOW-0F가 동결한 `Result`/`Warning`/`EvidenceType`을 재사용한다. UOW-01은 새 모델 `Asset`,
> `AssetType`, `ParseStatus`를 `trace/models/`에 추가한다. `AssetType` 값은 기존 `EvidenceType`
> (source/openapi/sql/config/test/markdown/pdf/text)과 **동일 문자열**로 맞춰 하위 단위 매핑을 단순화한다.

---

## 1. AssetType (Enum) — 자산 유형
`EvidenceType`과 정렬. 분류 규칙은 business-rules.md BR-CLASSIFY.

| 값 | 의미 | 대표 확장자/판별 |
|---|---|---|
| `source` | 소스코드 | .java/.py/.js/.ts/.go/.kt/.rb/.cs/.cpp/.c/.rs 등 |
| `openapi` | API 명세 | .yaml/.yml/.json 중 `openapi:`/`swagger:` 키 포함 |
| `sql` | DB 스키마/쿼리 | .sql |
| `config` | 설정 | .properties/.toml/.ini/.env, 위 openapi 아닌 .yaml/.yml/.json |
| `test` | 테스트 | 경로에 `/test/`·`/tests/` 또는 파일명 `*Test*`·`*Tests*`·`test_*`·`*_test.*` |
| `markdown` | 마크다운 | .md/.markdown |
| `pdf` | PDF 문서 | .pdf |
| `text` | 일반 텍스트 | .txt 및 기타 텍스트로 판정된 파일 |

- **분류 우선순위**: test 판별(경로/파일명)이 source보다 우선(테스트 소스는 test로). 그다음 확장자,
  마지막으로 내용 판별(openapi). (상세: BR-CLASSIFY-001~003)

## 2. ParseStatus (Enum) — 파싱 결과
| 값 | 의미 |
|---|---|
| `parsed` | 텍스트 추출 성공 |
| `partial` | 일부 추출(예: PDF 일부 페이지 실패, truncate 발생) |
| `skipped` | 제외 규칙/바이너리/유형 미지원으로 건너뜀 |
| `failed` | 추출 시도 중 오류(파일 단위 실패, 전체는 계속 — FR-ANALYSIS-003) |

## 3. Asset (모델) — `trace/models/asset.py`
```text
Asset:
  path: str            # 절대 경로(정규화)
  rel_path: str        # 프로젝트 루트 기준 상대 경로(결정적 정렬·표시용)
  filename: str
  asset_type: AssetType
  parse_status: ParseStatus
  size_bytes: int
  content: str | None  # 추출 텍스트(Q4=A eager). skipped/failed면 None
  truncated: bool = False   # 크기 상한 초과로 잘렸는지
  error: str | None = None  # failed 시 오류 요약(민감정보 제외)
```
- **content 노출 정책(Q5=A)**: `scan_project`의 `Result.data.assets`에는 content를 넣지 않는다.
  오케스트레이션(analyze_project, UOW-02+)은 in-process로 `list[Asset]`(content 포함)을 직접 받는다.

## 4. `scan_project(path) -> Result` 데이터 계약
```text
Result.summary : "N개 자산 스캔 (parsed A / partial B / skipped C / failed D)"  (+ warnings 합본)
Result.data = {
    "project_name": <디렉터리명>,
    "root": <정규화 절대경로>,
    "assets": [
        {"rel_path","filename","asset_type","parse_status","size_bytes","truncated"}  # content 제외(Q5=A)
        ...  # rel_path 사전순 정렬(결정적)
    ],
    "counts": {"total","parsed","partial","skipped","failed", "by_type": {...}}
}
Result.warnings = [Warning(code, message, source=rel_path), ...]  # 파일 단위 실패/트렁케이션
Result.meta = {"scanned_at": <생략 or 고정>, "max_file_bytes": <상한>}
```
- 내부 API(엔진용): `scan_project_assets(path) -> tuple[list[Asset], list[Warning]]` 로 content 포함
  전체 자산을 반환하고, `scan_project`는 이를 감싸 Result(메타만)로 변환한다.

## 5. 하위 단위로의 매핑
- UOW-02 `identify_features(assets)` 는 `list[Asset]`(content 포함)을 입력으로 받는다.
- `Asset.asset_type` → 근거 생성 시 `EvidenceType` 로 1:1 매핑(동일 문자열).
- `Asset.rel_path` → Evidence.source / ImpactItem.path 의 표시 경로로 사용.

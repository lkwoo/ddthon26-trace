# UOW-01 (스캐너 & 파서) — 비즈니스 로직 모델 (business-logic-model)

**단계**: CONSTRUCTION / Functional Design (UOW-01)
**작성일**: 2026-09-09

> 기술 비종속 알고리즘. 구현 기술은 NFR 단계에서 확정하되, 파서 라이브러리는 Q1=A로 이미 고정
> (pypdf/PyYAML/표준 텍스트). 여기서는 흐름과 규칙 적용 순서를 정의한다.

---

## 1. 컴포넌트 배치 (engine/, C2)
```text
trace/
├── models/
│   └── asset.py            # Asset, AssetType, ParseStatus  ← UOW-01 신설
└── engine/                 # C2 (UOW-01 착수)
    ├── scanner.py          # 디렉터리 순회·제외·경로검증
    ├── classifier.py       # AssetType 분류(BR-CLASSIFY)
    ├── parsers.py          # 유형별 텍스트 추출(BR-PARSE)
    └── scan.py             # scan_project / scan_project_assets 진입점 (오케스트레이션 골격)
```
- `config.get_exclusions()`, `Result`/`Warning`/`build_result`(UOW-0F)를 소비.
- UOW-01은 S1 오케스트레이션의 **스캔 구간**만 실 구현하고, Feature/AI 구간은 후속 단위 스텁으로 남긴다.

## 2. 핵심 알고리즘 — scan_project_assets(path)
```text
1. validate_path(path)                                   # BR-PATH-001/002
      실패 → return ([], [Warning(path_invalid ...)])     # 상위 scan_project가 오류 Result로 변환
2. root = realpath(path);  exclusions = get_exclusions()
3. assets = [];  warnings = []
4. for dirpath, dirnames, filenames in walk(root):        # 결정적 순회
      dirnames -= exclusions                               # BR-EXCLUDE-001 (하위 순회 생략)
      skip symlinked dirs escaping root                    # BR-PATH-002/003
      for fname in sorted(filenames):
          full = join(dirpath, fname)
          try:
              if is_symlink_escaping(full): skip+warn; continue     # BR-PATH-003
              size = stat(full).st_size
              if is_binary(full) and ext != .pdf: skip; continue     # BR-EXCLUDE-002
              atype = classify(full, root)                            # BR-CLASSIFY
              content, status, truncated, err = parse(full, atype, size)  # BR-PARSE/SIZE/FAIL
              assets.append(Asset(...))
              if status in (partial, failed): warnings.append(Warning(..., source=rel))
          except Exception as e:
              assets.append(Asset(parse_status=failed, error=sanitize(e)))   # BR-FAIL-001
              warnings.append(Warning(code=parse_failed, source=rel))
5. assets.sort(key=rel_path)                              # BR-DET-001
6. return assets, warnings
```

## 3. classify(full, root)  (BR-CLASSIFY, Q3=A)
```text
rel = relpath(full, root)
if is_test_path(rel) or is_test_filename(fname):  return test        # BR-CLASSIFY-002 (최우선)
ext = suffix.lower()
if ext in SOURCE_EXTS:      return source
if ext == ".sql":           return sql
if ext in (".md",".markdown"): return markdown
if ext == ".pdf":           return pdf
if ext in (".yaml",".yml",".json"):
     doc = try_parse_structured(full)                                # BR-CLASSIFY-003
     return openapi if has_key(doc, "openapi"|"swagger") else config
if ext in CONFIG_EXTS:      return config       # .properties/.toml/.ini/.env
return text
```

## 4. parse(full, atype, size)  (BR-PARSE, BR-SIZE, BR-FAIL)
```text
if size > MAX_FILE_BYTES:  read up to cap; truncated=True; status=partial
if atype == pdf:
     text, ok_pages, total = pypdf_extract(full)
     status = parsed if ok_pages==total else partial
else:
     text = read_text_utf8_or_latin1(full)      # 텍스트류 그대로 (Q2=A)
normalize newlines -> "\n"                        # BR-PARSE-004
return text, status, truncated, error?
```

## 5. scan_project(path) 래핑 (Q5=A)
```text
assets, warnings = scan_project_assets(path)
if path invalid:  return build_result(summary="경로 오류: ...", data={}, warnings=[...], meta={error_code})
counts = tally(assets)                            # total/parsed/partial/skipped/failed/by_type
data = {project_name, root(rel 표시), assets:[meta만], counts}   # content 제외
summary = f"{counts.total}개 자산 스캔 (parsed {p} / partial {pa} / skipped {s} / failed {f})"
return build_result(summary, data, warnings=warnings, meta={max_file_bytes})
```
- 충돌/영향 없음(이 단위는 스캔만) → Result.conflicts/impact/evidence 비움.

## 6. 데모(UOW-00) 기준 기대 동작
- `scan_project("demo")` → assets에 owner-management-spec.pdf(pdf, parsed),
  petclinic-rest.yaml(openapi), schema.sql(sql), *.java(source), OwnerControllerTests.java(test),
  application.properties(config), maintenance-notes.md·README.md(markdown) 포함.
- 모든 파일 parsed(또는 대용량 없으니 truncated 없음), failed 0 기대. counts.by_type가 6종 이상 커버.

## 7. 완료조건 (DoD)
- [ ] `scan_project(path)`가 assets + parse_status + counts 반환.
- [ ] 무효/비디렉터리 경로 → 오류 Result(스캔 안 함), NFR-SEC-004 충족.
- [ ] 제외 규칙 적용(.git 등 순회 생략), 심볼릭 탈출 차단.
- [ ] 파일 단위 실패가 전체를 중단시키지 않음(warning으로 계속) — FR-ANALYSIS-003.
- [ ] demo/에서 6종 이상 자산 유형 분류, PDF 텍스트 추출 성공.
- [ ] 결정적: 동일 입력 재실행 시 동일 assets 순서/분류.

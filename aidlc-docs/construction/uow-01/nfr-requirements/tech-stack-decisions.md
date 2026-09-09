# UOW-01 (스캐너 & 파서) — Tech Stack Decisions

**단계**: CONSTRUCTION / NFR Requirements (UOW-01)
**작성일**: 2026-09-09

## 확정된 기술 선택
| 항목 | 결정 | 근거 |
|---|---|---|
| 언어/런타임 | Python ≥ 3.11 (프로젝트 전역) | Requirements Q1, UOW-0F |
| 디렉터리 순회 | 표준 라이브러리 `os.walk` / `pathlib` | 결정적·무의존, Q1=A 순차 |
| PDF 추출 | **pypdf** (이미 dev 의존성 → **런타임 의존성으로 승격**) | Q1=A. 순수 파이썬·결정적. UOW-00 검증에서 추출 확인됨 |
| YAML/JSON 판별 | **PyYAML**(이미 런타임 의존성) + 표준 `json` | Q1=A. openapi/config 구분(BR-CLASSIFY-003) |
| 텍스트류 | 표준 파일 IO(UTF-8→latin-1 폴백) | Q2=A 텍스트 추출까지 |
| PBT | **hypothesis**(이미 dev 의존성) | PBT 확장, §5 4속성 |
| 설정 배치 | `trace/config`(C7)에 스캔 설정 추가 | Q4=A |

## 의존성 변경
- **`pypdf>=4.0`를 [project.dependencies](런타임)로 이동**(현재는 [dev]에만 존재).
  이유: UOW-01 스캐너가 런타임에 PDF 텍스트를 추출하므로 배포물에 필요.
  → Code Generation(UOW-01)에서 pyproject.toml 수정.
- 그 외 신규 의존성 없음(reportlab은 UOW-00 PDF 저작 도구였고 런타임/의존성 아님 — 추가하지 않음).

## 상한/설정 기본값 (config 배치, Q2=B/Q4=A)
| 설정 | 기본값 |
|---|---|
| `MAX_FILE_BYTES` | 5_000_000 (5MB) |
| `MAX_TOTAL_BYTES` | 200_000_000 (200MB) |
| 추가 제외 디렉터리 | get_exclusions() 기본 집합(UOW-0F) 재사용 |

## 미결(후속 단위)
- 소스코드 언어별 세부 파싱/심볼 추출은 범위 밖(Q2=A). 필요 시 UOW-02/03의 LLM 그라운딩이 담당.

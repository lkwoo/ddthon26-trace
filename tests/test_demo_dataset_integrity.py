"""UOW-00 데모 데이터셋 무결성 테스트.

정적 픽스처에는 실행 코드가 없으므로 속성 기반 테스트(PBT) 대신, 데이터셋이
'설계된 대로'의 의도적 충돌과 무결성 규칙을 보존하는지 검증한다.
(근거: aidlc-docs/construction/uow-00/functional-design/business-rules.md,
 nfr-requirements.md §3 — PBT 전면 정책의 데이터 단위 대체 검증)

의도적 충돌 3건이 실수로 정합화(충돌 소멸)되지 않도록 회귀를 막는 안전망이다.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from pypdf import PdfReader

DEMO = Path(__file__).resolve().parents[1] / "demo"

SPEC_PDF = DEMO / "requirements" / "owner-management-spec.pdf"
NOTES_MD = DEMO / "requirements" / "maintenance-notes.md"
OPENAPI = DEMO / "openapi" / "petclinic-rest.yaml"
SCHEMA_SQL = DEMO / "db" / "schema.sql"
OWNER_JAVA = DEMO / "src/main/java/org/springframework/samples/petclinic/owner/Owner.java"
PET_JAVA = DEMO / "src/main/java/org/springframework/samples/petclinic/pet/Pet.java"
APP_PROPS = DEMO / "config" / "application.properties"
README = DEMO / "README.md"


@pytest.fixture(scope="module")
def pdf_text() -> str:
    reader = PdfReader(str(SPEC_PDF))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


# ---------------------------------------------------------------------------
# 존재 / 자산 다양성 (R4)
# ---------------------------------------------------------------------------

def test_all_fixture_files_exist() -> None:
    for path in [SPEC_PDF, NOTES_MD, OPENAPI, SCHEMA_SQL, OWNER_JAVA, PET_JAVA, APP_PROPS, README]:
        assert path.exists(), f"누락된 데모 픽스처: {path}"


def test_asset_type_diversity_r4() -> None:
    # requirement(pdf), design_note(md), api_spec(yaml), db_schema(sql),
    # source_code(java), config(properties), test(java) 각 1개 이상
    suffixes = {p.suffix.lower() for p in DEMO.rglob("*") if p.is_file()}
    for expected in {".pdf", ".md", ".yaml", ".sql", ".java", ".properties"}:
        assert expected in suffixes, f"자산 유형 누락: {expected}"


# ---------------------------------------------------------------------------
# 충돌 C-1 — Owner.telephone max_length value_mismatch (P0)
# ---------------------------------------------------------------------------

def test_c1_pdf_requires_telephone_20(pdf_text: str) -> None:
    assert "20 characters" in pdf_text
    assert "telephone" in pdf_text.lower()


def test_c1_openapi_telephone_maxlength_10() -> None:
    text = OPENAPI.read_text(encoding="utf-8")
    # telephone 블록 안의 maxLength: 10 를 확인
    m = re.search(r"telephone:\s*\n(?:.*\n)*?\s*maxLength:\s*(\d+)", text)
    assert m and m.group(1) == "10", "OpenAPI telephone.maxLength 가 10 이 아님 (C-1 소멸 위험)"


def test_c1_source_and_db_telephone_10() -> None:
    assert "@Size(max = 10)" in OWNER_JAVA.read_text(encoding="utf-8")
    assert re.search(r"telephone\s+VARCHAR\(10\)", SCHEMA_SQL.read_text(encoding="utf-8"))


def test_c1_is_a_real_mismatch(pdf_text: str) -> None:
    # 요구(20) != 구현(10) 이어야 충돌이 성립
    assert "20" in pdf_text
    assert "@Size(max = 10)" in OWNER_JAVA.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# 충돌 C-2 — Pet.birthDate 미래일자 검증 드리프트 (stale_knowledge)
# ---------------------------------------------------------------------------

def test_c2_notes_claim_validation_exists() -> None:
    notes = NOTES_MD.read_text(encoding="utf-8")
    assert "birthDate" in notes and "미래" in notes and "검증" in notes


def test_c2_code_has_no_future_date_validation() -> None:
    pet = PET_JAVA.read_text(encoding="utf-8")
    assert "birthDate" in pet
    # 미래일자 검증 애너테이션이 '없어야' 드리프트가 성립
    for annotation in ("@PastOrPresent", "@Past"):
        assert annotation not in pet, f"{annotation} 존재 → C-2 드리프트 소멸"


# ---------------------------------------------------------------------------
# 충돌 C-3 — Owner.email 신규 필수 정책 부재 (policy_conflict)
# ---------------------------------------------------------------------------

def test_c3_pdf_requires_email(pdf_text: str) -> None:
    lowered = pdf_text.lower()
    assert "email" in lowered
    assert "must have an email" in lowered or "required" in lowered


def test_c3_email_absent_everywhere() -> None:
    # 설명용 주석에는 'email' 이 등장하므로, 실제 '선언'만 검사한다(주석 안전).
    owner = OWNER_JAVA.read_text(encoding="utf-8")
    assert not re.search(r"\bString\s+email\b", owner), "Owner.java 에 email 필드 선언 존재 → C-3 소멸"
    assert "getEmail(" not in owner, "Owner.java 에 email 접근자 존재 → C-3 소멸"

    openapi = OPENAPI.read_text(encoding="utf-8")
    assert not re.search(r"^\s+email:", openapi, re.MULTILINE), "OpenAPI 에 email 속성 존재 → C-3 소멸"

    schema = SCHEMA_SQL.read_text(encoding="utf-8")
    # SQL 주석(--)이 아닌, 컬럼 정의로서의 email 이 없어야 한다.
    assert not re.search(r"^\s*email\s+\w+", schema, re.MULTILINE | re.IGNORECASE), \
        "schema.sql 에 email 컬럼 정의 존재 → C-3 소멸"


# ---------------------------------------------------------------------------
# 무결성 규칙 R2(시크릿), R5(README 동기화)
# ---------------------------------------------------------------------------

def test_r2_no_real_secrets_in_config() -> None:
    props = APP_PROPS.read_text(encoding="utf-8")
    # 비밀번호는 명시적 플레이스홀더여야 한다
    m = re.search(r"spring\.datasource\.password=(.+)", props)
    assert m, "datasource.password 항목 없음"
    value = m.group(1).strip()
    assert "PLACEHOLDER" in value or "CHANGE_ME" in value, \
        f"실제 비밀번호로 보이는 값: {value!r}"


def test_r5_readme_lists_three_conflicts() -> None:
    readme = README.read_text(encoding="utf-8")
    for marker in ("C-1", "C-2", "C-3"):
        assert marker in readme, f"README 충돌표에 {marker} 누락"
    for ctype in ("value_mismatch", "stale_knowledge", "policy_conflict"):
        assert ctype in readme, f"README 에 충돌 유형 {ctype} 누락"

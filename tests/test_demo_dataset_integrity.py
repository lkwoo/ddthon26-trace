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
VET_SPEC_PDF = DEMO / "requirements" / "vet-directory-spec.pdf"
VISIT_SPEC_PDF = DEMO / "requirements" / "visit-scheduling-spec.pdf"
BILLING_SPEC_PDF = DEMO / "requirements" / "billing-spec.pdf"
NOTES_MD = DEMO / "requirements" / "maintenance-notes.md"
OPENAPI = DEMO / "openapi" / "petclinic-rest.yaml"
SCHEMA_SQL = DEMO / "db" / "schema.sql"
SRC = DEMO / "src/main/java/org/springframework/samples/petclinic"
OWNER_JAVA = SRC / "owner/Owner.java"
PET_JAVA = SRC / "pet/Pet.java"
VET_JAVA = SRC / "vet/Vet.java"
VISIT_JAVA = SRC / "visit/Visit.java"
INVOICE_JAVA = SRC / "billing/Invoice.java"
APP_PROPS = DEMO / "config" / "application.properties"
README = DEMO / "README.md"


def _pdf(path: Path) -> str:
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)


@pytest.fixture(scope="module")
def pdf_text() -> str:
    return _pdf(SPEC_PDF)


@pytest.fixture(scope="module")
def vet_pdf_text() -> str:
    return _pdf(VET_SPEC_PDF)


@pytest.fixture(scope="module")
def visit_pdf_text() -> str:
    return _pdf(VISIT_SPEC_PDF)


@pytest.fixture(scope="module")
def billing_pdf_text() -> str:
    return _pdf(BILLING_SPEC_PDF)


# ---------------------------------------------------------------------------
# 존재 / 자산 다양성 (R4)
# ---------------------------------------------------------------------------

def test_all_fixture_files_exist() -> None:
    for path in [SPEC_PDF, VET_SPEC_PDF, VISIT_SPEC_PDF, BILLING_SPEC_PDF, NOTES_MD,
                 OPENAPI, SCHEMA_SQL, OWNER_JAVA, PET_JAVA, VET_JAVA, VISIT_JAVA,
                 INVOICE_JAVA, APP_PROPS, README]:
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


def test_r5_readme_lists_all_conflicts() -> None:
    readme = README.read_text(encoding="utf-8")
    for i in range(1, 10):  # C-1 ~ C-9
        marker = f"C-{i}"
        assert marker in readme, f"README 충돌표에 {marker} 누락"
    for ctype in ("value_mismatch", "stale_knowledge", "policy_conflict"):
        assert ctype in readme, f"README 에 충돌 유형 {ctype} 누락"


# ---------------------------------------------------------------------------
# 충돌 C-4 — Visit.description max_length value_mismatch (255 vs 8192)
# ---------------------------------------------------------------------------

def test_c4_visit_spec_requires_255(visit_pdf_text: str) -> None:
    assert "255 characters" in visit_pdf_text and "description" in visit_pdf_text.lower()


def test_c4_impl_allows_8192() -> None:
    assert "@Size(max = 8192)" in VISIT_JAVA.read_text(encoding="utf-8")
    assert re.search(r"description\s+VARCHAR\(8192\)", SCHEMA_SQL.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 충돌 C-5 — Vet.specialties 최소 1개 정책 미강제 (policy_conflict)
# ---------------------------------------------------------------------------

def test_c5_vet_spec_requires_specialty(vet_pdf_text: str) -> None:
    lowered = vet_pdf_text.lower()
    assert "specialty" in lowered or "specialt" in lowered
    assert "at least one" in lowered

def test_c5_impl_has_no_min_constraint() -> None:
    vet = VET_JAVA.read_text(encoding="utf-8")
    assert "specialties" in vet
    # 최소 개수 제약(@Size(min=...))이 '없어야' 정책 미강제가 성립
    assert not re.search(r"@Size\s*\(\s*min", vet), "@Size(min=..) 존재 → C-5 소멸"


# ---------------------------------------------------------------------------
# 충돌 C-6 — Visit.date 과거일자 예약 금지 드리프트 (stale_knowledge)
# ---------------------------------------------------------------------------

def test_c6_notes_claim_past_date_rule() -> None:
    notes = NOTES_MD.read_text(encoding="utf-8")
    assert "VISIT-RULE-1" in notes and "과거" in notes

def test_c6_impl_has_no_date_validation() -> None:
    visit = VISIT_JAVA.read_text(encoding="utf-8")
    assert "date" in visit.lower()
    for annotation in ("@PastOrPresent", "@Future", "@Past"):
        assert annotation not in visit, f"{annotation} 존재 → C-6 드리프트 소멸"


# ---------------------------------------------------------------------------
# 충돌 C-7 — Invoice.amount precision value_mismatch (10,2 vs 8,2)
# ---------------------------------------------------------------------------

def test_c7_billing_spec_requires_10_2(billing_pdf_text: str) -> None:
    assert "DECIMAL(10,2)" in billing_pdf_text

def test_c7_impl_uses_8_2() -> None:
    assert re.search(r"precision\s*=\s*8", INVOICE_JAVA.read_text(encoding="utf-8"))
    assert re.search(r"amount\s+DECIMAL\(8,2\)", SCHEMA_SQL.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# 충돌 C-8 — Owner.address 필수 정책 부재 (policy_conflict)
# ---------------------------------------------------------------------------

def test_c8_owner_spec_requires_address(pdf_text: str) -> None:
    lowered = pdf_text.lower()
    assert "address" in lowered and "required" in lowered

def test_c8_impl_address_optional() -> None:
    owner = OWNER_JAVA.read_text(encoding="utf-8")
    # address 필드에 @NotBlank/@NotNull(필수)가 '없어야' 정책 부재가 성립
    m = re.search(r"private\s+String\s+address", owner)
    assert m, "Owner.java 에 address 필드 없음"
    preceding = owner[:m.start()].rsplit(";", 1)[-1]
    assert "@NotBlank" not in preceding and "@NotNull" not in preceding, \
        "address 에 필수 제약 존재 → C-8 소멸"


# ---------------------------------------------------------------------------
# 충돌 C-9 — billing.tax 기본 적용 문서/설정 드리프트 (stale_knowledge)
# ---------------------------------------------------------------------------

def test_c9_notes_claim_tax_enforced() -> None:
    notes = NOTES_MD.read_text(encoding="utf-8")
    assert "BILLING-RULE-1" in notes and "enforced" in notes

def test_c9_config_disables_tax() -> None:
    props = APP_PROPS.read_text(encoding="utf-8")
    assert re.search(r"billing\.tax\.enforcement\s*=\s*disabled", props), \
        "config 의 billing.tax.enforcement 가 disabled 가 아님 → C-9 소멸"

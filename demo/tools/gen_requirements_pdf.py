"""데모용 합성 요구사항 PDF 생성기 (일회성 저작 도구, 런타임 의존 아님).

의도적 충돌을 심는다: Owner 전화번호 **최대 길이 20자리** 요구.
(구현/OpenAPI/SQL 은 10자리 → value_mismatch 발생 지점.)

사용: `python demo/tools/gen_requirements_pdf.py`  (fpdf2 필요, dev 전용)
"""

from pathlib import Path

from fpdf import FPDF

OUT = Path(__file__).resolve().parents[1] / "requirements" / "owner-registration-spec.pdf"

LINES = [
    ("H1", "Owner Registration - Product Requirements (v2)"),
    ("P", "Document owner: Product / PM. Status: Approved."),
    ("H2", "1. Scope"),
    ("P", "This document specifies the customer (Owner) registration capability for the"),
    ("P", "PetClinic platform, including contact details and phone verification."),
    ("H2", "2. Contact Information Requirements"),
    ("P", "R-2.1  Each Owner MUST provide a contact telephone number."),
    ("P", "R-2.2  The telephone number field MUST allow a maximum length of 20"),
    ("P", "       characters to support international numbers with country codes"),
    ("P", "       and extensions (e.g. +82-10-1234-5678 ext. 123)."),
    ("P", "R-2.3  The telephone number MUST be validated for digits and separators."),
    ("H2", "3. Phone Verification (SMS)"),
    ("P", "R-3.1  Owner registration MUST include an SMS verification step: a one-time"),
    ("P", "       code is sent to the provided telephone number and must be confirmed"),
    ("P", "       before the Owner account is activated."),
    ("P", "R-3.2  Registration is not considered complete until SMS verification passes."),
    ("H2", "4. Acceptance"),
    ("P", "A-4.1  An Owner can register with a 20-character international phone number."),
    ("P", "A-4.2  An unverified Owner cannot be activated."),
]


def build() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    for kind, text in LINES:
        if kind == "H1":
            pdf.set_font("Helvetica", "B", 16)
            pdf.multi_cell(pdf.epw, 10, text)
            pdf.ln(2)
        elif kind == "H2":
            pdf.set_font("Helvetica", "B", 13)
            pdf.ln(2)
            pdf.multi_cell(pdf.epw, 8, text)
        else:
            pdf.set_font("Helvetica", "", 11)
            pdf.multi_cell(pdf.epw, 6, text)
    pdf.output(str(OUT))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    build()

"""데모용 요구사항 스펙 PDF 생성기 (TRACE demo, 재현 가능).

TRACE는 PDF(P0 파서)를 실제 요구사항 소스로 다룬다. 데모 데이터셋의 스펙 PDF들은
바이너리라 손으로 편집하기 어렵고, 리뷰어가 내용을 재현/검증할 수 있어야 하므로
이 스크립트로 결정적으로 생성한다.

의존성: reportlab (개발/데모 자산 생성용 — 런타임 의존성 아님).
실행:   .venv/Scripts/python.exe demo/tools/generate_specs.py

생성물(요구 값은 db/schema.sql·openapi·source의 구현 값과 의도적으로 어긋난다):
  requirements/owner-management-spec.pdf   — telephone ≤ 20 characters, email 필수, address 필수 (C-1/C-3/C-8)
  requirements/vet-directory-spec.pdf      — 수의사당 최소 1개 specialty 필수 (C-5)
  requirements/visit-scheduling-spec.pdf   — description ≤ 255 characters (C-4)
  requirements/billing-spec.pdf            — 금액은 DECIMAL(10,2) (C-7)
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

_REQ_DIR = Path(__file__).resolve().parents[1] / "requirements"


def _write_pdf(filename: str, title: str, sections: list[tuple[str, list[str]]]) -> None:
    path = _REQ_DIR / filename
    # invariant=True → 생성 시각/난수 고정으로 재실행 시 동일 바이트(결정적).
    c = canvas.Canvas(str(path), pagesize=A4, invariant=True)
    c.setTitle(title)
    width, height = A4
    left = 60
    y = height - 70

    c.setFont("Helvetica-Bold", 16)
    c.drawString(left, y, title)
    y -= 34

    for heading, lines in sections:
        c.setFont("Helvetica-Bold", 12)
        c.drawString(left, y, heading)
        y -= 20
        c.setFont("Helvetica", 10.5)
        for line in lines:
            c.drawString(left + 12, y, line)
            y -= 16
        y -= 8
        if y < 90:  # 페이지 넘김
            c.showPage()
            y = height - 70

    c.showPage()
    c.save()
    print(f"generated: requirements/{filename}")


def main() -> None:
    _REQ_DIR.mkdir(parents=True, exist_ok=True)

    _write_pdf(
        "owner-management-spec.pdf",
        "Owner Management - Functional Specification (TRACE demo)",
        [
            ("REQ-1  Contact number", [
                "The owner telephone must accept international formats.",
                "The telephone field length MUST allow up to 20 characters.",
            ]),
            ("REQ-2  Email (new policy)", [
                "Every owner must have an email address on file.",
                "The email field is required and must be validated for format.",
            ]),
            ("REQ-3  Address", [
                "The owner postal address is required for billing and correspondence.",
                "The address field must not be empty when an owner is registered.",
            ]),
        ],
    )

    _write_pdf(
        "vet-directory-spec.pdf",
        "Veterinarian Directory - Functional Specification (TRACE demo)",
        [
            ("REQ-1  Specialties", [
                "Every veterinarian must have at least one specialty assigned.",
                "A vet with an empty specialty list is not a valid directory entry.",
                "At least one specialty is required before a vet can be published.",
            ]),
            ("REQ-2  Naming", [
                "First name and last name are required, up to 30 characters each.",
            ]),
        ],
    )

    _write_pdf(
        "visit-scheduling-spec.pdf",
        "Visit Scheduling - Functional Specification (TRACE demo)",
        [
            ("REQ-1  Description", [
                "The visit description is a short free-text note.",
                "The description field length MUST NOT exceed 255 characters.",
            ]),
            ("REQ-2  Date", [
                "A visit date is required.",
                "Visits cannot be scheduled for a date in the past.",
            ]),
        ],
    )

    _write_pdf(
        "billing-spec.pdf",
        "Billing & Invoicing - Functional Specification (TRACE demo)",
        [
            ("REQ-1  Monetary amount", [
                "Invoice amounts are stored as fixed-point currency values.",
                "The amount column MUST use DECIMAL(10,2) to support large invoices.",
            ]),
            ("REQ-2  Tax", [
                "Value-added tax is enforced by default on every invoice.",
            ]),
        ],
    )


if __name__ == "__main__":
    main()

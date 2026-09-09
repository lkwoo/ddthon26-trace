"""페르소나 시나리오의 '실제 작업 화면'을 터미널 스타일 PNG로 렌더링한다.

Claude Code GUI 캡처가 아니라, TRACE 코어/CLI가 실제로 출력한 콘솔 트랜스크립트를
읽기 쉬운 터미널 창 이미지로 렌더링해 screenshots/ 에 저장한다.
입력 텍스트는 아래 SCREENS 상수(실제 실행 출력 원문)이며, 키 없이 재현 가능하다.

실행:  python demo/tools/render_screens.py   → screenshots/*.png
필요:  Pillow, Windows GulimChe 폰트(gulim.ttc, ASCII+한글 고정폭).
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
except Exception:  # pragma: no cover
    pass

from PIL import Image, ImageDraw, ImageFont

_REPO = Path(__file__).resolve().parents[2]
_OUT = _REPO / "screenshots"

# ── 테마(어두운 터미널) ──────────────────────────────────────────────────────
BG = (22, 24, 29)
BAR = (38, 41, 48)
FG = (208, 212, 218)
DIM = (128, 134, 145)
AMBER = (229, 192, 123)   # ⚠ 경고
CYAN = (86, 182, 194)     # 헤더/STEP
GREEN = (152, 195, 121)   # 섹션 라벨
RED = (224, 108, 117)     # policy_conflict
ORANGE = (209, 154, 102)  # value_mismatch
PURPLE = (198, 120, 221)  # stale_knowledge
DOTS = [(255, 95, 86), (255, 189, 46), (39, 201, 63)]

# GulimChe: ASCII+한글을 모두 커버하는 고정폭 폰트(한글=ASCII 2칸). 터미널 정렬 유지.
FONT_PATH = r"C:\Windows\Fonts\gulim.ttc"
FONT_INDEX = 1
SIZE = 20
LH = 30
PAD = 24
BAR_H = 40
MAX_W = 1700  # 이 픽셀 폭을 넘으면 접어 렌더링(행 넘침 방지)


def _color_for(line: str) -> tuple[int, int, int]:
    s = line.lstrip()
    if s.startswith("[!]"):
        return AMBER
    if s.startswith("===") or s.startswith("STEP") or s.startswith("#") or s.startswith("$"):
        return CYAN
    if any(s.startswith(k) for k in ("Must Change", "Likely Change", "Review:", "Change Plan",
                                     "Claims", "관련 자산", "유형 분포", "Feature:", "설명:")):
        return GREEN
    return FG


def _wrap(line: str, font, draw) -> list[str]:
    """픽셀 폭 MAX_W 기준으로 접는다(고정폭+한글 2칸 대응)."""
    if draw.textlength(line, font=font) <= MAX_W:
        return [line]
    indent = " " * (len(line) - len(line.lstrip()) + 4)
    words = line.split(" ")
    out, cur = [], ""
    for w in words:
        trial = w if not cur else cur + " " + w
        if draw.textlength(trial, font=font) > MAX_W and cur:
            out.append(cur)
            cur = indent + w
        else:
            cur = trial
    if cur:
        out.append(cur)
    return out


def _bold(draw, x, y, s, font, fill):
    """별도 bold face가 없으므로 1px 겹쳐 그려 굵게 흉내."""
    draw.text((x, y), s, font=font, fill=fill)
    draw.text((x + 1, y), s, font=font, fill=fill)


def _draw_tokens(draw, x, y, line, base, font):
    """[type] 토큰과 값@출처를 강조하며 한 줄 렌더."""
    tokens = {"[value_mismatch]": ORANGE, "[policy_conflict]": RED, "[stale_knowledge]": PURPLE}
    for tok, col in tokens.items():
        if tok in line:
            pre, _, post = line.partition(tok)
            draw.text((x, y), pre, font=font, fill=base)
            x2 = x + draw.textlength(pre, font=font)
            _bold(draw, x2, y, tok, font, col)
            x3 = x2 + draw.textlength(tok, font=font)
            draw.text((x3, y), post, font=font, fill=base)
            return
    draw.text((x, y), line, font=font, fill=base)


def render(text: str, out_path: Path, title: str) -> None:
    font = ImageFont.truetype(FONT_PATH, SIZE, index=FONT_INDEX)

    probe = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    raw = text.rstrip("\n").split("\n")
    lines: list[str] = []
    for ln in raw:
        lines.extend(_wrap(ln, font, probe))

    width = PAD * 2 + max((probe.textlength(l, font=font) for l in lines), default=200)
    width = int(max(width, probe.textlength(title, font=font) + 150))
    height = BAR_H + PAD * 2 + LH * len(lines)

    img = Image.new("RGB", (int(width), int(height)), BG)
    draw = ImageDraw.Draw(img)
    # 타이틀 바 + 신호등 + 타이틀
    draw.rectangle([0, 0, width, BAR_H], fill=BAR)
    for i, c in enumerate(DOTS):
        cx = 20 + i * 22
        draw.ellipse([cx, BAR_H // 2 - 7, cx + 14, BAR_H // 2 + 7], fill=c)
    _bold(draw, 110, BAR_H // 2 - SIZE // 2, title, font, DIM)

    y = BAR_H + PAD
    for ln in lines:
        _draw_tokens(draw, PAD, y, ln, _color_for(ln), font)
        y += LH
    img.save(out_path)
    print(f"[ok] {out_path.relative_to(_REPO)}  ({img.width}x{img.height})")


# ── 실제 실행 출력(원문) — 각 페르소나 대표 화면 ─────────────────────────────
DEV = """\
STEP 3 · trace_get_feature_knowledge("owner-registration")
Feature: 소유자 등록 및 관리 (owner-registration)
설명: 반려동물 소유자(Owner)의 등록/조회/연락처·이메일·주소 관리. 요구-구현 불일치(C-1,C-3,C-8) 집중.
관련 자산 11개: owner-management-spec.pdf · petclinic-rest.yaml · schema.sql ·
  Owner/OwnerDto/OwnerMapper/OwnerRepository/OwnerRestController/OwnerService.java · Person.java · OwnerControllerTests.java

Claims 15건 (subject.predicate = value):
  - owner.create_endpoint = POST /owners
  - owner.telephone.max_length = 20        owner.telephone.international_format = required
  - owner.email.required = required         owner.email.format_validation = required
  - owner.address.required = required       owner.address.max_length = 255
  - owner.firstName.required = required     owner.lastName.required = required

이 Feature 충돌 6건:
  - [value_mismatch]  owner.telephone.max_length : 10@schema.sql  vs  20@owner-management-spec.pdf
  - [policy_conflict] owner.email.required        : absent@schema.sql  vs  required@spec.pdf
  - [policy_conflict] owner.email.format_validation : absent@OwnerDto.java  vs  required@spec.pdf
  - [policy_conflict] owner.address.required      : nullable@schema.sql  vs  required@spec.pdf
  - [value_mismatch]  owner.firstName.required    : NOT NULL@schema.sql  vs  required@openapi
  - [value_mismatch]  owner.lastName.required     : NOT NULL@schema.sql  vs  required@openapi

resource_uri: trace://feature/owner-registration
"""

MAIRA = """\
STEP 1~3 · trace_get_conflicts → 세금 이슈 근본 원인
[!] 충돌 39건이 감지되었습니다 (아래 우선 확인).
유형 분포: value_mismatch 20 · policy_conflict 15 · stale_knowledge 4

=== clinic-configuration (충돌 1건) ===
  - [stale_knowledge] billing.tax.enforcement.default_policy
      · disabled  @ config/application.properties  (billing.tax.enforcement)
      · enforced   @ requirements/billing-spec.pdf   (REQ-2)

=== billing-invoicing (세금 관련) ===
  - [policy_conflict] invoice.tax.vat_enforced_by_default : absent@BillingService.java vs enforced@billing-spec.pdf
  - [value_mismatch]  invoices.amount.decimal_precision   : 10@billing-spec.pdf vs 8@schema.sql

→ 원인: 설정이 꺼져 있고(disabled) + 코드도 VAT를 강제하지 않음(absent). 스펙은 enforced.
  고칠 곳: application.properties 전환 · BillingService 강제 로직 · notes/spec 동기화 · 회귀 테스트.
"""

PM = """\
STEP 1 · trace_analyze_task_impact("Add SMS verification to Owner registration", "owner-registration")
영향 후보 11건 (must 5 / likely 4 / review 2), 관련 충돌 6건

[!] 착수 전 확인할 기존 충돌:
  - [value_mismatch]  owner.telephone.max_length   : 10(schema.sql) vs 20(spec.pdf)   ← SMS 인증의 전제
  - [policy_conflict] owner.email.required          : required(spec) vs absent(schema.sql)
  - [policy_conflict] owner.address.required        : required(spec) vs absent/nullable(code/db)

Must Change:
  - openapi/petclinic-rest.yaml        : SMS 발송/검증 엔드포인트·인증 필드 정의, telephone maxLength 정리
  - requirements/owner-management-spec.pdf : SMS 인증 절차·전화번호 검증 명세화(REQ-1과 정합)
  - OwnerRestController.java / OwnerService.java : 등록 흐름에 인증 게이트 통합
  - tests/OwnerControllerTests.java     : 인증 흐름 테스트 추가, telephoneMaxLengthIsTen 수정

Likely Change:  db/schema.sql · Owner.java · OwnerDto.java · OwnerMapper.java
Review:         model/Person.java · OwnerRepository.java

Change Plan (충돌 선결):
  1. C-1(telephone 10 vs 20, 국제형식) 정책 확정  ← SMS 인증 전제
  2. SMS 인증 요구사항 명세화 → 3. OpenAPI 정의 → 4. schema(phone_verified/길이) 반영
  5. Owner/DTO/Mapper 정합화 → 6. Service/Controller 통합 → 7. 테스트 → 8. 문서 최종 정합
"""

SCREENS = [
    (DEV,   "dev-owner-knowledge.png",   "trace — 데브 · get_feature_knowledge (MCP)"),
    (MAIRA, "maira-tax-rootcause.png",   "trace — 마이라 · get_conflicts (MCP)"),
    (PM,    "pm-impact-plan.png",        "trace — 피엠 · analyze_task_impact (MCP)"),
]


def main() -> int:
    _OUT.mkdir(exist_ok=True)
    for text, name, title in SCREENS:
        render(text, _OUT / name, title)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

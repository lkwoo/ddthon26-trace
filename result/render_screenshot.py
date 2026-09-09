#!/usr/bin/env python3
"""터미널 전사(transcript)를 '터미널 창' 스타일 PNG 스크린샷으로 렌더링한다.

TRACE CLI는 ANSI 색을 쓰지 않는 평문 출력이라, 여기서 라인 종류(프롬프트/로그/충돌/헤더)를
가벼운 휴리스틱으로 구분해 색을 입힌다. 한글 출력이 있으므로 한글 모노스페이스 폰트를 쓴다.

사용:
    python3 result/render_screenshot.py <title> <input.txt> <output.png>
"""

from __future__ import annotations

import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

# 한글 지원 모노스페이스 폰트 (없으면 DejaVu로 폴백 — 한글은 깨질 수 있음)
FONT_CANDIDATES = [
    "/home/wsl/.fonts/KRmono.ttf",
    "/usr/share/fonts/truetype/nanum/NanumGothicCoding.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
]

FONT_SIZE = 17
LINE_H = 26
PAD = 26
TITLEBAR_H = 44
MAX_COLS = 96  # 이보다 긴 줄은 접는다

# 카탈로그: 다크 터미널 팔레트
BG = (30, 30, 46)
TITLEBAR = (43, 43, 60)
FG = (205, 214, 244)          # 기본 텍스트
GREEN = (166, 227, 161)       # 프롬프트($)
DIM = (108, 112, 134)         # 로그 라인
AMBER = (250, 179, 135)       # 충돌/경고
CYAN = (137, 220, 235)        # 섹션 헤더
BULLET = (203, 166, 247)      # Feature 목록
RED_DOT, YEL_DOT, GRN_DOT = (237, 106, 94), (245, 191, 79), (98, 197, 84)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    for path in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def sanitize(text: str) -> str:
    # 변이 선택자 제거 + 폰트에 없는 경고 이모지를 ASCII 마커로 치환(tofu 방지)
    text = text.replace("⚠️", "[!]").replace("⚠", "[!]")
    return "".join(c for c in text if unicodedata.category(c) != "Cf")


def dwidth(text: str) -> int:
    # 표시 폭: 동아시아 Wide/Fullwidth 글자는 2칸으로 센다
    return sum(2 if unicodedata.east_asian_width(c) in ("W", "F") else 1 for c in text)


def color_for(line: str) -> tuple:
    s = line.strip()
    if s.startswith("$ ") or s.startswith("### CMD") or s.startswith("# "):
        return GREEN
    if "[INFO]" in line or "[DEBUG]" in line or "[WARNING]" in line:
        return DIM
    if s.startswith(("[반드시", "[변경", "[검토]", "[Change Plan]")):
        return CYAN
    if "value_mismatch" in line or "충돌" in line or "⚠" in line or "불일치" in line:
        return AMBER
    if s.startswith("•"):
        return BULLET
    return FG


def wrap(line: str, cols: int) -> list[str]:
    # 표시 폭 기준으로 접는다 (한글=2칸)
    if dwidth(line) <= cols:
        return [line]
    out: list[str] = []
    cur, w = "", 0
    for ch in line:
        cw = dwidth(ch)
        if w + cw > cols:
            out.append(cur)
            cur, w = "  " + ch, 2 + cw  # 접힌 줄 들여쓰기
        else:
            cur += ch
            w += cw
    if cur:
        out.append(cur)
    return out


def render(title: str, text: str, out_path: str) -> None:
    font = load_font(FONT_SIZE)
    title_font = load_font(FONT_SIZE - 2)

    raw_lines = sanitize(text).replace("\t", "    ").split("\n")
    lines: list[str] = []
    for ln in raw_lines:
        lines.extend(wrap(ln, MAX_COLS))

    # 폭: 가장 긴 줄의 표시 폭 기준 (한글=2칸)
    char_w = font.getlength("M")
    max_dw = max((dwidth(l) for l in lines), default=40)
    width = int(PAD * 2 + char_w * min(MAX_COLS, max_dw))
    width = max(width, 720)
    height = TITLEBAR_H + PAD * 2 + LINE_H * len(lines)

    img = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(img)

    # 타이틀바 + 신호등 점
    d.rectangle([0, 0, width, TITLEBAR_H], fill=TITLEBAR)
    cy = TITLEBAR_H // 2
    for i, col in enumerate((RED_DOT, YEL_DOT, GRN_DOT)):
        cx = 20 + i * 22
        d.ellipse([cx - 7, cy - 7, cx + 7, cy + 7], fill=col)
    d.text((110, cy - (FONT_SIZE - 2) // 2 - 2), title, font=title_font, fill=FG)

    # 본문
    y = TITLEBAR_H + PAD
    for ln in lines:
        d.text((PAD, y), ln, font=font, fill=color_for(ln))
        y += LINE_H

    img.save(out_path)
    print(f"저장: {out_path} ({width}x{height})")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("usage: render_screenshot.py <title> <input.txt> <output.png>", file=sys.stderr)
        sys.exit(2)
    _title, _inp, _out = sys.argv[1], sys.argv[2], sys.argv[3]
    with open(_inp, encoding="utf-8") as f:
        render(_title, f.read(), _out)

#!/usr/bin/env python3
"""Render the same zh-HK infographic cards as SVG (text stays as text)."""

from __future__ import annotations

import importlib.util
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parents[1]
IMG = ROOT / "images"
FOOT = "衞生署家庭健康服務網頁文字摘要　·　唔構成醫療建議"
FONTS = '"PingFang HK","Heiti TC","Noto Sans TC","Hiragino Sans CNS",sans-serif'

BG = "#f7f4ee"
HEADER = "#0b5e60"
TEXT = "#1c2a3a"
WHITE = "#ffffff"
LINE = "#dcd6cc"
WARN = "#9a302a"
OK = "#246e56"
NOTE_BG = "#ffece6"
GOLD = "#e8a858"
SUB = "#d2e8e4"


def load_cards() -> tuple[list, list]:
    path = ROOT / "scripts" / "render_infographics.py"
    spec = importlib.util.spec_from_file_location("png_cards", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.CARDS, mod.MORE


def wrap(text: str, max_units: float) -> list[str]:
    lines, cur, width = [], "", 0.0
    for ch in text:
        cw = 0.55 if ord(ch) < 128 else 1.0
        if cur and width + cw > max_units:
            lines.append(cur)
            cur, width = ch, cw
        else:
            cur += ch
            width += cw
    if cur:
        lines.append(cur)
    return lines or [""]


def text_el(
    x: float,
    cy: float,
    content: str,
    *,
    size: int,
    fill: str,
    weight: str | None = None,
    anchor: str | None = None,
) -> str:
    """`cy` is the optical centre. Pixel dy is more stable than em in <img> SVG."""
    dy = round(size * 0.36)
    attrs = [
        f'x="{x}"',
        f'y="{cy}"',
        f'dy="{dy}"',
        f'fill="{fill}"',
        f'font-size="{size}"',
    ]
    if weight:
        attrs.append(f'font-weight="{weight}"')
    if anchor:
        attrs.append(f'text-anchor="{anchor}"')
    return f"  <text {' '.join(attrs)}>{escape(content)}</text>\n"


def svg_doc(w: int, h: int, title: str, body: str) -> str:
    return (
        f'<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
        f'width="100%" role="img" xml:lang="zh-Hant-HK">\n'
        f"  <title>{escape(title)}</title>\n"
        f"  <desc>{escape(FOOT)}</desc>\n"
        f"  <style>text{{font-family:{FONTS}}}</style>\n"
        f'  <rect width="{w}" height="{h}" fill="{BG}"/>\n'
        f"{body}"
        f"</svg>\n"
    )


def header_svg(w: int, title: str, subtitle: str) -> str:
    return (
        f'  <rect width="{w}" height="168" fill="{HEADER}"/>\n'
        f'  <rect y="168" width="{w}" height="8" fill="{GOLD}"/>\n'
        + text_el(48, 70, title, size=42, fill=WHITE, weight="600")
        + text_el(48, 118, subtitle, size=22, fill=SUB)
    )


def footer_svg(w: int, h: int) -> str:
    return (
        f'  <rect y="{h - 64}" width="{w}" height="64" fill="{HEADER}"/>\n'
        + text_el(48, h - 32, FOOT, size=18, fill=SUB)
    )


def save(rel_png: str, markup: str) -> Path:
    dest = IMG / Path(rel_png).with_suffix(".svg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding="utf-8")
    return dest


def save_card(rel: str, title: str, subtitle: str, items: list[str], note: str | None) -> Path:
    w = 1080
    y = 208
    rows: list[tuple[int, list[str]]] = []
    for i, item in enumerate(items, 1):
        lines = wrap(item, 31)
        rows.append((i, lines))
        y += max(58, 22 + 40 * len(lines))
    note_lines = wrap(note, 34) if note else []
    if note:
        y += 20 + 36 + 32 * len(note_lines)
    h = max(720, y + 100)

    parts = [header_svg(w, title, subtitle)]
    y = 208
    for i, lines in rows:
        cy = y + 22
        parts.append(f'  <circle cx="66" cy="{cy}" r="18" fill="{HEADER}"/>\n')
        parts.append(text_el(66, cy, str(i), size=22, fill=WHITE, anchor="middle"))
        for j, line in enumerate(lines):
            parts.append(text_el(104, cy + j * 40, line, size=28, fill=TEXT))
        y += max(58, 22 + 40 * len(lines))
    if note:
        box_h = 36 + 32 * max(0, len(note_lines) - 1) + 28
        parts.append(
            f'  <rect x="40" y="{y + 8}" width="{w - 80}" height="{box_h}" '
            f'rx="16" fill="{NOTE_BG}"/>\n'
        )
        box_mid = y + 8 + box_h / 2
        first_cy = box_mid - 16 * (len(note_lines) - 1)
        for j, line in enumerate(note_lines):
            parts.append(text_el(64, first_cy + j * 32, line, size=24, fill=WARN))
    parts.append(footer_svg(w, h))
    return save(rel, svg_doc(w, h, title, "".join(parts)))


def save_split(
    rel: str,
    title: str,
    subtitle: str,
    left_h: str,
    left: list[str],
    right_h: str,
    right: list[str],
) -> Path:
    w = 1080
    mid = w // 2
    top = 208

    left_blocks = [wrap("• " + t, 17) for t in left]
    right_blocks = [wrap("• " + t, 17) for t in right]
    n_rows = max(len(left_blocks), len(right_blocks))
    box_h = 112 + 56 * n_rows
    box_bottom = top + box_h
    h = max(780, box_bottom + 88)

    parts = [header_svg(w, title, subtitle)]
    parts.append(
        f'  <rect x="36" y="{top}" width="{mid - 52}" height="{box_h}" '
        f'rx="20" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>\n'
    )
    parts.append(
        f'  <rect x="{mid + 16}" y="{top}" width="{mid - 52}" height="{box_h}" '
        f'rx="20" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>\n'
    )
    parts.append(
        f'  <rect x="52" y="{top + 20}" width="{mid - 84}" height="52" rx="12" fill="{OK}"/>\n'
    )
    parts.append(
        f'  <rect x="{mid + 32}" y="{top + 20}" width="{mid - 84}" height="52" '
        f'rx="12" fill="{WARN}"/>\n'
    )
    pill_cy = top + 46
    parts.append(text_el(72, pill_cy, left_h, size=26, fill=WHITE, weight="600"))
    parts.append(text_el(mid + 52, pill_cy, right_h, size=26, fill=WHITE, weight="600"))

    yy = top + 108
    for block in left_blocks:
        for j, line in enumerate(block):
            parts.append(text_el(72, yy + j * 32, line, size=24, fill=TEXT))
        yy += 56
    yy = top + 108
    for block in right_blocks:
        for j, line in enumerate(block):
            parts.append(text_el(mid + 52, yy + j * 32, line, size=24, fill=TEXT))
        yy += 56
    parts.append(footer_svg(w, h))
    return save(rel, svg_doc(w, h, title, "".join(parts)))


def point_md_to_svg() -> int:
    n = 0
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        new = re.sub(r"(\]\(\.\./images/[^)\s]+)\.png\)", r"\1.svg)", text)
        if new != text:
            path.write_text(new, encoding="utf-8")
            n += 1
    return n


def main() -> None:
    cards, more = load_cards()
    written = 0
    for _md, img, title, sub, items, note in cards + more:
        save_card(img, title, sub, items, note)
        written += 1
        print("wrote", Path(img).with_suffix(".svg"))
    save_split(
        "00-0-to-1-month/hunger-cues.png",
        "肚餓信號",
        "先安撫，後餵哺",
        "早期（宜餵）",
        ["轉頭覓食", "嘴巴張開", "身體躍躍欲動", "伸手入口"],
        "較遲（先安撫）",
        ["大聲哭鬧", "煩躁扭動", "滿面通紅", "安撫後再餵"],
    )
    save_split(
        "mother/postnatal-exercise-dont.png",
        "產後運動：做同唔好做",
        "量力、循序漸進",
        "可以",
        ["深層收腹同盆骨底", "腰背左右擺膝", "由步行 10 分鐘開始", "抱 BB 時收腹"],
        "未適宜",
        ["仰臥起坐", "仰臥抬腿", "抬頭時肚隆起仍加難", "手術產未問醫生就練"],
    )
    written += 2
    n = point_md_to_svg()
    print(f"svg={written} md_updated={n}")


if __name__ == "__main__":
    main()

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
        f'  <text x="48" y="78" fill="{WHITE}" font-size="42" font-weight="600">'
        f"{escape(title)}</text>\n"
        f'  <text x="48" y="124" fill="{SUB}" font-size="22">{escape(subtitle)}</text>\n'
    )


def footer_svg(w: int, h: int) -> str:
    return (
        f'  <rect y="{h - 64}" width="{w}" height="64" fill="{HEADER}"/>\n'
        f'  <text x="48" y="{h - 26}" fill="{SUB}" font-size="18">{escape(FOOT)}</text>\n'
    )


def save(rel_png: str, markup: str) -> Path:
    dest = IMG / Path(rel_png).with_suffix(".svg")
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(markup, encoding="utf-8")
    return dest


def save_card(rel: str, title: str, subtitle: str, items: list[str], note: str | None) -> Path:
    w = 1080
    y = 208
    rows: list[tuple[int, str, list[str]]] = []
    for i, item in enumerate(items, 1):
        lines = wrap(item, 30)
        rows.append((i, item, lines))
        y += max(52, 16 + 38 * len(lines))
    note_lines = wrap(note, 32) if note else []
    if note:
        y += 24 + 28 + 32 * len(note_lines)
    h = max(720, y + 100)

    parts = [header_svg(w, title, subtitle)]
    y = 208
    for i, _item, lines in rows:
        cy = y + 24
        parts.append(f'  <circle cx="66" cy="{cy}" r="18" fill="{HEADER}"/>\n')
        parts.append(
            f'  <text x="66" y="{cy + 1}" fill="{WHITE}" font-size="22" '
            f'text-anchor="middle" dominant-baseline="middle">{i}</text>\n'
        )
        for j, line in enumerate(lines):
            parts.append(
                f'  <text x="104" y="{y + 10 + j * 38}" fill="{TEXT}" font-size="28">'
                f"{escape(line)}</text>\n"
            )
        y += max(52, 16 + 38 * len(lines))
    if note:
        box_h = 28 + 32 * len(note_lines)
        parts.append(
            f'  <rect x="40" y="{y + 8}" width="{w - 80}" height="{box_h}" '
            f'rx="16" fill="{NOTE_BG}"/>\n'
        )
        for j, line in enumerate(note_lines):
            parts.append(
                f'  <text x="64" y="{y + 36 + j * 32}" fill="{WARN}" font-size="24">'
                f"{escape(line)}</text>\n"
            )
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

    def col_lines(items: list[str], max_units: float) -> list[str]:
        out: list[str] = []
        for t in items:
            wrapped = wrap("• " + t, max_units)
            out.extend(wrapped)
            out.append("")
        return out

    left_lines = col_lines(left, 16)
    right_lines = col_lines(right, 16)
    content_h = 96 + 40 * max(len(left_lines), len(right_lines))
    box_bottom = top + max(520, content_h)
    h = max(820, box_bottom + 96)

    parts = [header_svg(w, title, subtitle)]
    parts.append(
        f'  <rect x="36" y="{top}" width="{mid - 52}" height="{box_bottom - top}" '
        f'rx="20" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>\n'
    )
    parts.append(
        f'  <rect x="{mid + 16}" y="{top}" width="{mid - 52}" height="{box_bottom - top}" '
        f'rx="20" fill="{WHITE}" stroke="{LINE}" stroke-width="2"/>\n'
    )
    parts.append(
        f'  <rect x="52" y="{top + 20}" width="{mid - 84}" height="52" rx="12" fill="{OK}"/>\n'
    )
    parts.append(
        f'  <rect x="{mid + 32}" y="{top + 20}" width="{mid - 84}" height="52" '
        f'rx="12" fill="{WARN}"/>\n'
    )
    parts.append(
        f'  <text x="72" y="{top + 54}" fill="{WHITE}" font-size="26" font-weight="600">'
        f"{escape(left_h)}</text>\n"
    )
    parts.append(
        f'  <text x="{mid + 52}" y="{top + 54}" fill="{WHITE}" font-size="26" font-weight="600">'
        f"{escape(right_h)}</text>\n"
    )

    yy = top + 104
    for line in left_lines:
        if line:
            parts.append(
                f'  <text x="56" y="{yy}" fill="{TEXT}" font-size="24">{escape(line)}</text>\n'
            )
        yy += 36
    yy = top + 104
    for line in right_lines:
        if line:
            parts.append(
                f'  <text x="{mid + 36}" y="{yy}" fill="{TEXT}" font-size="24">'
                f"{escape(line)}</text>\n"
            )
        yy += 36
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

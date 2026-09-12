#!/usr/bin/env python3
"""Migrate Docsify markdown + images into astro/src/content/docs (Starlight)."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASTRO = ROOT / "astro"
DOCS = ASTRO / "src" / "content" / "docs"
PUBLIC_IMAGES = ASTRO / "public" / "images"
SITE_URL = "https://hilda.lhl.hk"

CONTENT_DIRS = [
    "mother",
    "00-0-to-1-month",
    "01-1-to-12-months",
    "02-1-to-3-years",
    "03-3-to-6-years",
    "resources",
]

# Standalone markdown at repo root (not in a content directory)
ROOT_PAGES = ["meal.md"]

LINK_RE = re.compile(r"(!?\[[^\]]*\]\()([^)]+)(\))")
SIDEBAR_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def is_external(url: str) -> bool:
    return url.startswith(("http://", "https://", "mailto:"))


def is_doc_link(url: str) -> bool:
    if is_external(url) or url.startswith("#"):
        return False
    path = url.split("#", 1)[0]
    if not path:
        return False
    lower = path.lower()
    if lower.startswith("/images/") or "/images/" in lower:
        return False
    if lower.endswith((".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp")):
        return False
    return lower.endswith(".md") or lower.endswith("/readme") or "/readme.md" in lower


def yaml_quote(value: str) -> str:
    if re.search(r'[:#\[\]{}&*!|>\'"%@`]', value) or value.strip() != value:
        return json.dumps(value, ensure_ascii=False)
    return value


def add_frontmatter(text: str) -> str:
    if text.startswith("---\n"):
        return text
    match = re.match(r"^#\s+(.+)$", text, re.MULTILINE)
    title = match.group(1).strip() if match else "Untitled"
    return f"---\ntitle: {yaml_quote(title)}\n---\n\n{text}"


def resolve_docs_path(url: str, source_dir: str) -> str:
    path, _, anchor = url.partition("#")
    if path.startswith("/"):
        resolved = path.lstrip("/")
    else:
        base = Path(source_dir) if source_dir else Path(".")
        resolved = (base / path).as_posix()
        resolved = str(Path(resolved).as_posix())

    if resolved.endswith("/README.md"):
        slug = resolved[: -len("/README.md")]
    elif resolved == "README.md":
        slug = ""
    elif resolved.endswith(".md"):
        slug = resolved[: -len(".md")]
    else:
        slug = resolved.rstrip("/")

    slug = slug.strip("/")
    href = "/" if not slug else f"/{slug}/"
    if anchor:
        href += f"#{anchor}"
    return href


def rewrite_markdown_links(text: str, source_dir: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        if prefix.startswith("!") or not is_doc_link(url):
            return match.group(0)
        return f"{prefix}{resolve_docs_path(url, source_dir)}{suffix}"

    return LINK_RE.sub(repl, text)


def rewrite_image_paths(text: str, source_dir: str) -> str:
    def repl(match: re.Match[str]) -> str:
        prefix, url, suffix = match.group(1), match.group(2), match.group(3)
        if not prefix.startswith("!") or is_external(url) or url.startswith("/images/"):
            return match.group(0)
        if url.startswith("/"):
            image_path = url.lstrip("/")
        else:
            base = Path(source_dir) if source_dir else Path(".")
            image_path = (base / url).as_posix()
            image_path = str(Path(image_path).as_posix())
        if not image_path.startswith("images/"):
            idx = image_path.find("images/")
            if idx == -1:
                return match.group(0)
            image_path = image_path[idx:]
        return f"{prefix}/{image_path}{suffix}"

    return LINK_RE.sub(repl, text)


def transform_markdown(text: str, source_dir: str) -> str:
    text = rewrite_image_paths(text, source_dir)
    text = rewrite_markdown_links(text, source_dir)
    return add_frontmatter(text)


def href_to_slug(href: str) -> str:
    href = href.lstrip("/")
    if href.endswith("/README.md"):
        return href[: -len("/README.md")]
    if href.endswith(".md"):
        return href[: -len(".md")]
    return href.rstrip("/")


def parse_sidebar(sidebar_path: Path) -> list[dict]:
    groups: list[dict] = []
    current: dict | None = None

    for raw_line in sidebar_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.rstrip()
        if not line.strip():
            continue
        if line.startswith("  - "):
            match = SIDEBAR_LINK_RE.search(line)
            if not match or current is None:
                continue
            label, href = match.group(1), match.group(2)
            if href == "/":
                continue
            current["items"].append({"label": label, "slug": href_to_slug(href)})
            continue
        if line.startswith("- "):
            match = SIDEBAR_LINK_RE.search(line)
            if match and match.group(2) == "/":
                continue
            label = line[2:].strip()
            current = {"label": label, "items": []}
            groups.append(current)

    return groups


def homepage_content(readme: str) -> str:
    text = readme
    text = rewrite_image_paths(text, "")
    text = rewrite_markdown_links(text, "")
    text = text.replace(
        "## 本機瀏覽（Docsify）\n\n```bash\nnpx serve\n```\n\n"
        "開 http://localhost:3000 。Docsify 用 hash 路由（`#/mother/breastfeeding`），"
        "靜態伺服器唔使 rewrite。側欄連結由網站根開始（`/mother/...`）， "
        "nested 頁唔會疊錯路徑。亦可以用 `npx docsify-cli serve .`。\n",
        "## 本機瀏覽（Astro）\n\n```bash\ncd astro\nnpm run dev\n```\n\n"
        "開 http://localhost:4320 。靜態 build：`npm run build`，輸出喺 `astro/dist/`。\n",
    )
    frontmatter = (
        "---\n"
        "title: 2026 育兒筆記\n"
        "description: 整理、歸類同總結育嬰知識（繁體中文 · 香港）\n"
        "---\n\n"
    )
    return frontmatter + text


def write_astro_config(sidebar: list[dict]) -> None:
    config_path = ASTRO / "astro.config.mjs"
    sidebar_json = json.dumps(sidebar, ensure_ascii=False, indent=2)
    sidebar_json = "\n".join("\t\t\t" + line for line in sidebar_json.splitlines())

    content = f"""// @ts-check
import {{ defineConfig }} from 'astro/config';
import sitemap from '@astrojs/sitemap';
import starlight from '@astrojs/starlight';

const site = process.env.SITE ?? '{SITE_URL}';

// https://astro.build/config
export default defineConfig({{
\tsite,
\tintegrations: [
\t\tstarlight({{
\t\t\ttitle: '2026 育兒筆記',
\t\t\tdefaultLocale: 'root',
\t\t\tlocales: {{
\t\t\t\troot: {{
\t\t\t\t\tlabel: '繁體中文',
\t\t\t\t\tlang: 'zh-TW',
\t\t\t\t}},
\t\t\t}},
\t\t\tsidebar: {sidebar_json},
\t\t}}),
\t\tsitemap(),
\t],
}});
"""
    config_path.write_text(content, encoding="utf-8")


def migrate() -> None:
    if DOCS.exists():
        shutil.rmtree(DOCS)
    DOCS.mkdir(parents=True)

    if PUBLIC_IMAGES.exists():
        shutil.rmtree(PUBLIC_IMAGES)
    shutil.copytree(ROOT / "images", PUBLIC_IMAGES)

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    (DOCS / "index.md").write_text(homepage_content(readme), encoding="utf-8")

    for content_dir in CONTENT_DIRS:
        src_dir = ROOT / content_dir
        for src in sorted(src_dir.rglob("*.md")):
            rel = src.relative_to(src_dir)
            dest_name = "index.md" if rel.name == "README.md" else rel.name
            dest = DOCS / content_dir / rel.parent / dest_name
            dest.parent.mkdir(parents=True, exist_ok=True)
            source_dir = (
                content_dir
                if rel.parent == Path(".")
                else f"{content_dir}/{rel.parent.as_posix()}"
            )
            body = src.read_text(encoding="utf-8")
            (dest).write_text(transform_markdown(body, source_dir), encoding="utf-8")

    for page in ROOT_PAGES:
        src = ROOT / page
        if not src.is_file():
            continue
        dest = DOCS / page
        body = src.read_text(encoding="utf-8")
        dest.write_text(transform_markdown(body, ""), encoding="utf-8")

    sidebar = parse_sidebar(ROOT / "_sidebar.md")
    write_astro_config(sidebar)

    astro_readme = """# 2026 育兒筆記（Astro / Starlight）

育嬰筆記嘅 Astro 版，內容由 repo 根目錄嘅 Markdown 遷移而嚟。

## 本機開發

```bash
npm install
npm run dev
```

## Build

```bash
npm run build
```

輸出：`dist/`（Cloudflare Pages root directory 設 `astro`，output 設 `dist`）。

## 重新遷移內容

改完根目錄 Markdown 後：

```bash
python3 scripts/migrate_to_astro.py
```
"""
    (ASTRO / "README.md").write_text(astro_readme, encoding="utf-8")

    migrated = list(DOCS.rglob("*.md"))
    print(f"Migrated {len(migrated)} markdown files to {DOCS.relative_to(ROOT)}/")
    print(f"Copied images to {PUBLIC_IMAGES.relative_to(ROOT)}/")
    print(f"Updated {ASTRO.relative_to(ROOT)}/astro.config.mjs")


if __name__ == "__main__":
    migrate()

# 2026 育兒筆記（Astro / Starlight）

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

## SEO 同機械人檔案

Build 會自動產生：

| 路徑 | 說明 |
|------|------|
| `/sitemap-index.xml` | 網站地圖（`@astrojs/sitemap`） |
| `/robots.txt` | 允許爬蟲，並指向 sitemap |
| `/llms.txt` | 供 LLM 讀嘅站點摘要同全部頁面連結 |

正式網址：**https://hilda.lhl.hk/**

`sitemap-index.xml`、`robots.txt`、`llms.txt` 預設用以上 domain。如需覆寫（例如 staging），可設 environment variable：

```bash
SITE=https://hilda.lhl.hk
```

## 搜尋

Starlight 內建 **Pagefind** 全文搜尋（build 時自動索引所有頁面）。

UI 文案用香港繁體（`src/content/i18n/zh-TW.json` 覆寫 Starlight 預設）。Starlight 用 `zh-TW` 語系包做基底（`zh-HK` 會錯誤 fallback 到簡體 `zh`）。

- 網站頂部有 **搜尋** 按鈕，或按 **⌘K** / **Ctrl+K**
- `npm run dev` 開發模式搜尋唔會載入索引；要本地試搜尋：

```bash
npm run build
npm run preview
```

然後開 http://localhost:4321 試搜尋（例如「黃疸」「母乳」「疫苗」）。

## 重新遷移內容

改完根目錄 Markdown 後：

```bash
python3 scripts/migrate_to_astro.py
```

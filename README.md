# Trend Blog System

此專案提供一個最小可用的 CLI，可以根據指定關鍵字抓取 Google Trends 每日趨勢，產出話題想法、下標策略與部落格草稿。輸出為 Markdown 或 JSON，便於後續串接 CMS 或自動化流程。

## 功能概覽

- 讀取指定關鍵字的每日 Google Trends（使用 `pytrends`）
- 萃取相關熱門查詢與每日趨勢
- 生成話題靈感、文章架構與標題方向
- 輸出 Markdown/JSON 草稿，方便後續自動化

## 安裝

```bash
pip install -r requirements.txt
```

## 使用方式

```bash
python -m trend_blog_system.main "AI 教育" --geo TW --format markdown
```

輸出檔案會寫入 `outputs/` 目錄，檔名包含關鍵字與日期。

## 範例輸出內容

- 今日話題想法
- 內容架構
- 推薦關鍵字
- 參考趨勢來源

## 延伸方向

- 加入 LLM 進行更細緻的標題/內文生成
- 串接 CMS API（如 WordPress、Ghost）進行自動發布
- 加入排程器（cron / Airflow）每日自動執行

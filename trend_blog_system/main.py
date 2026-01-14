"""CLI for generating trend-based blog ideas and draft posts."""
from __future__ import annotations

import argparse
import datetime as dt
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from pytrends.request import TrendReq


@dataclass
class TrendIdea:
    title: str
    angle: str
    sources: List[str]


@dataclass
class BlogDraft:
    title: str
    summary: str
    outline: List[str]
    ideas: List[TrendIdea]
    keywords: List[str]
    sources: List[str]


def fetch_daily_trends(pytrends: TrendReq, geo: str) -> List[str]:
    """Fetch daily trend titles for the specified geo."""
    daily = pytrends.daily_trends(geo=geo)
    return daily[0].dropna().astype(str).tolist()


def fetch_related_queries(pytrends: TrendReq, keyword: str, geo: str) -> List[str]:
    """Fetch related queries for a given keyword."""
    pytrends.build_payload([keyword], geo=geo, timeframe="now 1-d")
    related = pytrends.related_queries()
    if keyword not in related or related[keyword] is None:
        return []
    top = related[keyword].get("top")
    if top is None:
        return []
    return top["query"].astype(str).tolist()


def rank_keywords(base_keyword: str, daily: Iterable[str], related: Iterable[str]) -> List[str]:
    """Merge and rank keywords by relevance to the base keyword."""
    pool = [base_keyword] + list(daily) + list(related)
    unique = []
    seen = set()
    for item in pool:
        key = item.strip()
        if key and key.lower() not in seen:
            seen.add(key.lower())
            unique.append(key)
    return unique


def build_ideas(keyword: str, trend_keywords: List[str]) -> List[TrendIdea]:
    """Generate idea angles from trend keywords."""
    ideas = []
    for idx, trend in enumerate(trend_keywords[:5], start=1):
        ideas.append(
            TrendIdea(
                title=f"{trend} 與 {keyword} 的關聯分析",
                angle=f"從第 {idx} 個熱門關鍵字切入，解析 {keyword} 的趨勢意義與延伸需求。",
                sources=[trend],
            )
        )
    return ideas


def build_blog_draft(keyword: str, trend_keywords: List[str]) -> BlogDraft:
    """Create a blog draft from trend keywords."""
    ideas = build_ideas(keyword, trend_keywords)
    title = f"{keyword} 今日趨勢洞察與內容靈感"
    summary = (
        f"本文整理 {keyword} 相關的每日熱門趨勢，提煉話題與內容角度，"
        "協助快速產出具時效性的文章與標題。"
    )
    outline = [
        "趨勢總覽：今日熱門關鍵字與熱度來源",
        "話題拆解：與目標關鍵字的關聯性",
        "內容架構：文章主題與子題建議",
        "下標策略：吸睛標題與 SEO 關鍵字",
        "行動清單：下一步可產出的內容",
    ]
    sources = trend_keywords[:10]
    return BlogDraft(
        title=title,
        summary=summary,
        outline=outline,
        ideas=ideas,
        keywords=trend_keywords[:10],
        sources=sources,
    )


def render_markdown(draft: BlogDraft) -> str:
    """Render the draft to markdown."""
    ideas_md = "\n".join(
        f"- **{idea.title}**：{idea.angle}" for idea in draft.ideas
    )
    outline_md = "\n".join(f"1. {section}" for section in draft.outline)
    keyword_md = "\n".join(f"- {keyword}" for keyword in draft.keywords)
    sources_md = "\n".join(f"- {source}" for source in draft.sources)

    return (
        f"# {draft.title}\n\n"
        f"{draft.summary}\n\n"
        "## 今日話題想法\n"
        f"{ideas_md}\n\n"
        "## 內容架構\n"
        f"{outline_md}\n\n"
        "## 推薦關鍵字\n"
        f"{keyword_md}\n\n"
        "## 參考趨勢來源\n"
        f"{sources_md}\n"
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Trend-based blog post generator")
    parser.add_argument("keyword", help="主關鍵字，例如：AI 教育")
    parser.add_argument("--geo", default="TW", help="國家/地區代碼，預設 TW")
    parser.add_argument(
        "--output",
        default="outputs",
        help="輸出資料夾，預設 outputs",
    )
    parser.add_argument(
        "--format",
        default="markdown",
        choices=["markdown", "json"],
        help="輸出格式",
    )
    return parser


def ensure_output_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    pytrends = TrendReq(hl="zh-TW", tz=480)
    daily = fetch_daily_trends(pytrends, geo=args.geo)
    related = fetch_related_queries(pytrends, keyword=args.keyword, geo=args.geo)
    trend_keywords = rank_keywords(args.keyword, daily, related)
    draft = build_blog_draft(args.keyword, trend_keywords)

    output_dir = Path(args.output)
    ensure_output_dir(output_dir)
    timestamp = dt.datetime.now().strftime("%Y%m%d")
    filename = output_dir / f"{args.keyword}_{timestamp}.{'md' if args.format == 'markdown' else 'json'}"

    if args.format == "markdown":
        content = render_markdown(draft)
    else:
        content = json.dumps(draft, ensure_ascii=False, default=lambda o: o.__dict__, indent=2)

    filename.write_text(content, encoding="utf-8")
    print(f"Saved draft to {filename}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""从 data/*.json 生成静态网站。只用 Python 标准库。

用法:  python3 build.py
输出:
  index.html                 最新一天的新闻（首页）
  archive/<日期>.html         每天的存档页
  archive/index.html         存档目录
  today-standalone.html      最新一天的单文件版（CSS 内联，可直接当附件发送）
"""
import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
DATA = ROOT / "data"
ARCHIVE = ROOT / "archive"
CSS_FILE = ROOT / "assets" / "style.css"
SITE_TITLE = "AI 每日热点"

CATEGORY_CLASS = {
    "模型发布": "c-model", "产品更新": "c-product", "融资并购": "c-funding",
    "政策监管": "c-policy", "研究突破": "c-research", "X 热议": "c-x",
}
REQUIRED = ["title", "summary", "source", "url", "category"]
WEEKDAYS = "一二三四五六日"

e = lambda s: html.escape(str(s), quote=True)


def load_days():
    days = []
    for p in sorted(DATA.glob("*.json")):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError as err:
            sys.exit(f"[错误] {p.name} 不是合法 JSON: {err}")
        d.setdefault("date", p.stem)
        for i, it in enumerate(d.get("items", []), 1):
            miss = [k for k in REQUIRED if not it.get(k)]
            if miss:
                sys.exit(f"[错误] {p.name} 第 {i} 条缺少字段: {', '.join(miss)}")
            if not str(it["url"]).startswith(("http://", "https://")):
                sys.exit(f"[错误] {p.name} 第 {i} 条链接不是 http(s): {it['url']}")
        days.append(d)
    if not days:
        sys.exit("[错误] data/ 下没有 json 文件")
    days.sort(key=lambda d: d["date"])
    return days


def weekday(d):
    if d.get("weekday"):
        return d["weekday"]
    import datetime
    return "周" + WEEKDAYS[datetime.date.fromisoformat(d["date"]).weekday()]


def render_items(day):
    top = day.get("top_story_id")
    out = ['<ol class="news">']
    for n, it in enumerate(day["items"], 1):
        is_top = it.get("id") and it.get("id") == top
        cls = CATEGORY_CLASS.get(it["category"], "")
        tags = f'<span class="tag {cls}">{e(it["category"])}</span>'
        if is_top:
            tags = '<span class="tag star">★ 今日最重要</span>' + tags
        if it.get("published_at"):
            tags += f'<span class="time">{e(it["published_at"])}</span>'
        rel = ""
        if it.get("related"):
            links = "".join(
                f'<a href="{e(r["url"])}" target="_blank" rel="noopener">{e(r["source"])}</a>'
                for r in it["related"])
            rel = f'<div class="related">相关报道：{links}</div>'
        orig = f' title="{e(it["original_title"])}"' if it.get("original_title") else ""
        out.append(
            f'<li class="item{" top" if is_top else ""}" id="{e(it.get("id", n))}">'
            f'<div class="tags">{tags}</div>'
            f'<h2><span class="rank">{n}.</span>{e(it["title"])}</h2>'
            f'<p>{e(it["summary"])}</p>'
            f'<div class="src">来源：<a href="{e(it["url"])}" target="_blank" rel="noopener"{orig}>{e(it["source"])}</a></div>'
            f'{rel}</li>')
    out.append("</ol>")
    return "\n".join(out)


def page(title, body, css_href=None, inline_css=None):
    style = (f"<style>\n{inline_css}\n</style>" if inline_css is not None
             else f'<link rel="stylesheet" href="{css_href}">')
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{style}
</head>
<body><div class="wrap">
{body}
<footer>所有新闻均来自原文链接，摘要为中文整理，请以原文为准。时间均为新加坡时间（SGT, UTC+8），标注"美国时间"者除外。</footer>
</div></body></html>
"""


def day_body(day, nav):
    hdr = (f'<header class="site"><h1>{SITE_TITLE} · {e(day["date"])} {e(weekday(day))}</h1>'
           f'<div class="meta">新加坡时间 · 共 {len(day["items"])} 条'
           + (f' · 更新于 {e(day["updated_at"])}' if day.get("updated_at") else "")
           + (f'<br>收录范围：{e(day["window"])}' if day.get("window") else "")
           + f'</div><div class="nav">{nav}</div></header>')
    return hdr + "\n" + render_items(day)


def main():
    days = load_days()
    latest = days[-1]
    css = CSS_FILE.read_text(encoding="utf-8")
    ARCHIVE.mkdir(exist_ok=True)

    # 首页
    (ROOT / "index.html").write_text(page(
        f"{SITE_TITLE} · {latest['date']}",
        day_body(latest, '<a href="archive/index.html">📚 往期存档</a>'),
        css_href="assets/style.css"), encoding="utf-8")

    # 单文件版（CSS 内联、无外部依赖）
    (ROOT / "today-standalone.html").write_text(page(
        f"{SITE_TITLE} · {latest['date']}",
        day_body(latest, ""), inline_css=css), encoding="utf-8")

    # 每日存档
    for d in days:
        (ARCHIVE / f"{d['date']}.html").write_text(page(
            f"{SITE_TITLE} · {d['date']}",
            day_body(d, '<a href="../index.html">🏠 首页</a><a href="index.html">📚 往期存档</a>'),
            css_href="../assets/style.css"), encoding="utf-8")

    # 存档目录
    lis = "\n".join(
        f'<li><a href="{e(d["date"])}.html">{e(d["date"])} {e(weekday(d))}</a>'
        f' <span class="meta">· {len(d["items"])} 条</span></li>'
        for d in reversed(days))
    body = (f'<header class="site"><h1>{SITE_TITLE} · 往期存档</h1>'
            f'<div class="meta">共 {len(days)} 天</div>'
            f'<div class="nav"><a href="../index.html">🏠 返回首页</a></div></header>'
            f'<ul class="archive">\n{lis}\n</ul>')
    (ARCHIVE / "index.html").write_text(page(f"{SITE_TITLE} · 往期存档", body,
                                             css_href="../assets/style.css"), encoding="utf-8")

    print(f"已生成：最新 {latest['date']}（{len(latest['items'])} 条），存档 {len(days)} 天")
    print("  index.html, today-standalone.html, archive/index.html, "
          + ", ".join(f"archive/{d['date']}.html" for d in days))


if __name__ == "__main__":
    main()

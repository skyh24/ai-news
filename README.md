# AI 每日热点（静态网站）

纯 HTML + CSS，无需构建工具或服务器。双击 `index.html` 即可在浏览器中以 `file://` 方式打开（全部为相对路径）。

## 目录结构

文件在仓库根目录（对应线上路径 `/ai-news/`）：

```
index.html                  # 首页：最新一天的新闻（build.py 生成）
today-standalone.html       # 最新一天的单文件版，CSS 内联，可直接当附件发送到手机/电脑
archive/
├── index.html              # 存档目录（build.py 生成）
└── YYYY-MM-DD.html         # 每天的存档页（build.py 生成）
assets/style.css            # 样式（含手机适配和深色模式）
data/YYYY-MM-DD.json        # 每天的新闻数据（唯一需要手动/自动编写的文件）
build.py                    # 生成脚本（只依赖 Python 3 标准库）
check_links.py              # 检查站内链接是否为相对路径
.nojekyll                   # 按原始文件发布，不走 Jekyll
.github/workflows/pages.yml # 推送到 main 时生成页面并部署到 GitHub Pages
```

## 每天怎么更新

1. 复制前一天的 json 为新文件，文件名为新加坡日期，例如 `data/2026-10-09.json`。
2. 修改顶层字段和 `items` 列表（按重要性排序，第 1 条排最前）。
3. 在仓库根目录运行：
   ```bash
   python3 build.py
   ```
4. 脚本会自动：把首页和 `today-standalone.html` 换成最新日期、为每个 json 生成 `archive/<日期>.html`、更新 `archive/index.html`。

> 只要不删 json，历史存档会一直保留。build.py 会校验每条新闻必须有标题、摘要、来源、链接（http/https）和分类，缺失时报错退出。

## JSON 格式

```json
{
  "date": "2026-10-09",                 // 新加坡日期（必填，默认取文件名）
  "weekday": "周五",                    // 可选，不填自动计算
  "timezone": "Asia/Singapore (UTC+8)",
  "window": "2026-10-08 12:00 至 2026-10-09 12:00（新加坡时间）",  // 可选
  "updated_at": "2026-10-09 12:30 SGT", // 可选，显示在页面顶部
  "top_story_id": "某条的 id",          // 可选，该条会高亮为「今日最重要」
  "items": [
    {
      "id": "short-unique-id",
      "title": "中文标题",               // 必填
      "summary": "1-2 句中文摘要",       // 必填
      "source": "来源名称",              // 必填
      "url": "https://原文链接",         // 必填
      "category": "模型发布",            // 必填，见下
      "published_at": "2026-10-09 08:00 SGT",
      "original_title": "英文原标题（鼠标悬停来源链接时显示）",
      "related": [{"source": "其他媒体", "url": "https://..."}]
    }
  ]
}
```
（实际 json 里不能写 `//` 注释，上面仅作说明。）

分类及对应颜色：`模型发布`、`产品更新`、`融资并购`、`政策监管`、`研究突破`、`X 热议`。其他分类也能用，只是显示默认颜色；要加新颜色就在 `build.py` 的 `CATEGORY_CLASS` 和 `assets/style.css` 里各加一行。

## 收录原则

- 只收真实抓到的新闻，每条都要有原文链接和来源名称，不编造标题、数字和引言。
- 时间范围约为前一天中午到当天中午（新加坡时间）；如果某条是更早发布、但在这个时段内持续发酵，需要在 `published_at` 里注明。
- 时间统一写新加坡时间（SGT），只知道美国日期的写「（美国时间）」。

## 在手机/电脑上查看

- 最简单：把 `today-standalone.html` 作为文件发到手机/电脑，直接用浏览器打开（无需联网加载样式，但点原文链接时需要联网）。
- 完整站点（含存档）：把仓库根目录拷贝过去，然后打开 `index.html`。

## 发布到 GitHub Pages

线上地址：<https://skyh24.github.io/ai-news/>

页面、样式和存档导航都使用相对路径（例如 `assets/style.css`、`archive/index.html`、`../index.html`），没有以 `/` 开头的站内链接，因此在项目站点的 `/ai-news/` 前缀下可以正常打开。

`.github/workflows/pages.yml` 在每次 push 到 `main` 时先运行 `python3 build.py`，再把仓库根目录（含 `.nojekyll`）部署到 GitHub Pages。之后每天把新的 `data/YYYY-MM-DD.json` 和重新生成的 HTML 推到 `main` 即可自动更新。

Pages 目前尚未启用，而且本仓库的自动化令牌没有 `administration:write`，无法代为打开。合并到 `main` 之后，需要仓库管理员做一次设置：

1. 打开 <https://github.com/skyh24/ai-news/settings/pages>
2. 在 **Build and deployment** 下，把 **Source** 选为 **GitHub Actions**
3. 如果合并触发的工作流因为 Pages 尚未启用而失败，到 Actions 里重新运行 **Deploy static content to Pages**

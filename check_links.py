#!/usr/bin/env python3
# 确认站内链接保持相对路径，以便在 /ai-news/ 前缀下正常工作。
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
ATTR = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)
CSS_URL = re.compile(r"""url\(\s*['"]?([^'")]+)['"]?\s*\)""", re.I)


def main():
    html_files = sorted(ROOT.glob("*.html")) + sorted((ROOT / "archive").glob("*.html"))
    errors = []
    checked = 0
    for path in html_files:
        text = path.read_text(encoding="utf-8")
        for url in ATTR.findall(text):
            checked += 1
            if url.startswith(("#", "mailto:", "http://", "https://", "data:")):
                continue
            if url.startswith("/") or url.startswith("//"):
                errors.append(f"{path.relative_to(ROOT)}: root-absolute link {url}")
                continue
            target = (path.parent / url.split("#", 1)[0].split("?", 1)[0]).resolve()
            try:
                target.relative_to(ROOT)
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes site root: {url}")
                continue
            if not target.is_file():
                errors.append(f"{path.relative_to(ROOT)}: missing target for {url}")
    css = (ROOT / "assets" / "style.css").read_text(encoding="utf-8")
    for url in CSS_URL.findall(css):
        if url.startswith(("data:", "http://", "https://")):
            continue
        errors.append(f"assets/style.css: unexpected url({url})")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        sys.exit(1)
    print(f"checked {len(html_files)} html files, {checked} links")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Build the Market Notes site.

Each file in src/ is a page fragment: <title>, <meta>, <link> and <style> first,
then the page body. This script wraps every fragment in a full HTML document,
adds the shared site menu, rewrites old claude.ai artifact links to site pages,
and writes the result to docs/, which GitHub Pages serves.
"""
import html
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent
SRC = ROOT / "src"
OUT = ROOT / "docs"

# Order here is the order of the site menu. A page appears once its src file exists.
PAGES = [
    ("index", "Home", "Learning notes on five market sectors, updated as news happens."),
    ("overview", "Overview", "A beginner's map of AI chips, AI infrastructure, games, Big Tech and Tesla."),
    ("buying-basics", "Buying basics", "How to size a position, read a quote, choose an order type and decide what price to pay."),
    ("momentum-lab", "Momentum lab", "Interactive momentum reader, rule tester, news-reaction simulator and exit-plan builder."),
    ("ai-chips", "AI chips", "How AI chips work, who earns what, Nvidia vs. custom chips, and how to read Nvidia's earnings."),
    ("memory-power", "Memory & power", "The memory boom and its cycle, how neoclouds like IREN make money, and the AI power squeeze."),
    ("games", "Games", "How game companies make money, GTA VI, Roblox, Nintendo and the rest of the sector."),
    ("big-tech", "Big Tech", "How Microsoft, Alphabet, Amazon, Meta and Apple make money, and the AI spending question."),
    ("hot-topics", "Tesla & hot topics", "Tesla's robotaxi and robot bets, the Anthropic IPO, and the market's other big themes."),
]

# Pages first published as claude.ai artifacts link to each other by those URLs.
ARTIFACT_LINKS = {
    "https://claude.ai/artifact/Mq5pzCbhH5xSqJEqRew4Hj": "overview.html",
    "https://claude.ai/artifact/JfRPRWfJcdke7rCqFeHAEH": "ai-chips.html",
    "https://claude.ai/artifact/YHuiNNUqNfbSJ46JjqbufD": "memory-power.html",
}

FAVICON = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='7' fill='%232b47cf'/%3E"
    "%3Cpath d='M7 23V9h3.2l5.8 8.2L21.8 9H25v14h-3.2v-8.4L16 22.4l-5.8-7.8V23z' fill='white'/%3E"
    "%3C/svg%3E"
)

BASE_CSS = """
:root { color-scheme: light; padding-top: env(safe-area-inset-top, 0px); padding-bottom: env(safe-area-inset-bottom, 0px); }
body { margin: 0; }
img { max-width: 100%; }
[hidden] { display: none !important; }
"""

NAV_CSS = """
.site-nav { background: var(--surface); border-bottom: 1px solid var(--line); }
.site-nav-in {
  max-width: 800px; margin: 0 auto; box-sizing: border-box;
  padding-left: max(16px, env(safe-area-inset-left, 0px));
  padding-right: max(16px, env(safe-area-inset-right, 0px));
  padding-block: 10px;
  display: flex; flex-wrap: wrap; align-items: baseline; gap: 6px 18px;
}
.site-brand { font-family: "Archivo", "Helvetica Neue", Arial, sans-serif; font-weight: 800; font-size: 1rem; color: var(--fg); text-decoration: none; letter-spacing: -0.01em; }
.site-links { display: flex; flex-wrap: wrap; gap: 4px 14px; font-size: 0.86rem; }
.site-links a { color: var(--muted); text-decoration: none; padding: 2px 0; }
.site-links a:hover { color: var(--fg); text-decoration: underline; }
.site-links a[aria-current="page"] { color: var(--fg); font-weight: 600; }
"""


def nav_html(current: str, live: list) -> str:
    links = []
    for slug, label, _ in live:
        if slug == "index":
            continue
        cur = ' aria-current="page"' if slug == current else ""
        links.append(f'<a href="{slug}.html"{cur}>{html.escape(label)}</a>')
    brand_cur = ' aria-current="page"' if current == "index" else ""
    return (
        '<nav class="site-nav" aria-label="Site"><div class="site-nav-in">'
        f'<a class="site-brand" href="index.html"{brand_cur}>Market Notes</a>'
        f'<div class="site-links">{"".join(links)}</div>'
        "</div></nav>\n"
    )


def open_external_in_new_tab(body: str) -> str:
    def fix(m):
        attrs = m.group(1)
        if "target=" in attrs:
            return m.group(0)
        return f'<a {attrs}target="_blank" rel="noopener" href="{m.group(2)}"'
    return re.sub(r'<a ([^>]*?)href="(https?://[^"]+)"', fix, body)


def build_page(slug: str, description: str, live: list) -> None:
    fragment = (SRC / f"{slug}.html").read_text(encoding="utf-8")

    for url, local in ARTIFACT_LINKS.items():
        fragment = fragment.replace(url, local)
    # The old "back to field guide" links are replaced by the site menu.
    fragment = re.sub(r'\s*<a class="back" href="[^"]*">[^<]*</a>', "", fragment)

    split_at = fragment.find("</style>")
    if split_at == -1:
        raise SystemExit(f"{slug}: no </style> found")
    split_at += len("</style>")
    head_part = fragment[:split_at]
    body_part = open_external_in_new_tab(fragment[split_at:])

    doc = (
        "<!doctype html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f'<meta name="description" content="{html.escape(description)}">\n'
        f'<link rel="icon" href="{FAVICON}">\n'
        f"<style>{BASE_CSS}</style>\n"
        f"{head_part}\n"
        f"<style>{NAV_CSS}</style>\n"
        "</head>\n<body>\n"
        f"{nav_html(slug, live)}"
        f"{body_part}\n"
        "</body>\n</html>\n"
    )
    (OUT / f"{slug}.html").write_text(doc, encoding="utf-8")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    live = [p for p in PAGES if (SRC / f"{p[0]}.html").exists()]
    for slug, _, description in live:
        build_page(slug, description, live)
    (OUT / ".nojekyll").write_text("", encoding="utf-8")
    print("built:", ", ".join(f"{p[0]}.html" for p in live))


if __name__ == "__main__":
    main()

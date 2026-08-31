#!/usr/bin/env python3
"""
Convert writing/posts/*.md → writing/*.html and regenerate writing/index.html.
Requires: pandoc (brew install pandoc)

Usage:
    python3 build.py
"""

import os
import re
import subprocess
from pathlib import Path

POSTS_DIR = Path("writing/posts")
OUT_DIR   = Path("writing")
TEMPLATE  = Path("writing/_post_template.html")
INDEX     = Path("writing/index.html")


def parse_front_matter(text):
    """Return (meta_dict, body_text). Front matter is YAML between --- lines."""
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not match:
        return {}, text
    meta = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    body = text[match.end():]
    return meta, body


def md_to_html(md_text):
    """Run pandoc to convert Markdown to an HTML fragment."""
    result = subprocess.run(
        ["pandoc", "--from=markdown", "--to=html"],
        input=md_text, capture_output=True, text=True, check=True
    )
    return result.stdout


def build_post(md_path, template_html):
    raw = md_path.read_text(encoding="utf-8")
    meta, body_md = parse_front_matter(raw)

    title = meta.get("title", md_path.stem.replace("-", " ").title())
    date  = meta.get("date", "")
    body_html = md_to_html(body_md)

    html = (template_html
            .replace("{{TITLE}}", title)
            .replace("{{DATE}}", date)
            .replace("{{BODY}}", body_html))

    slug = md_path.stem
    out_path = OUT_DIR / f"{slug}.html"
    out_path.write_text(html, encoding="utf-8")
    return {"title": title, "date": date, "slug": slug}


def build_index(posts):
    """Rebuild the POSTS_START … POSTS_END block in writing/index.html."""
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)

    if not posts_sorted:
        items_html = '<p style="color: var(--muted); font-size: 0.95rem;">Nothing here yet.</p>'
    else:
        rows = []
        for p in posts_sorted:
            rows.append(
                f'<li>'
                f'<span class="post-title"><a href="/writing/{p["slug"]}.html">{p["title"]}</a></span>'
                f'<span class="post-date">{p["date"]}</span>'
                f'</li>'
            )
        items_html = '<ul class="post-list">\n' + "\n".join(rows) + "\n</ul>"

    index_html = INDEX.read_text(encoding="utf-8")
    index_html = re.sub(
        r"<!-- POSTS_START -->.*?<!-- POSTS_END -->",
        f"<!-- POSTS_START -->\n      {items_html}\n      <!-- POSTS_END -->",
        index_html,
        flags=re.DOTALL,
    )
    INDEX.write_text(index_html, encoding="utf-8")


def main():
    template_html = TEMPLATE.read_text(encoding="utf-8")
    md_files = sorted(POSTS_DIR.glob("*.md"))

    # skip files starting with _ (drafts / examples)
    md_files = [f for f in md_files if not f.stem.startswith("_")]

    posts = []
    for md in md_files:
        post = build_post(md, template_html)
        posts.append(post)
        print(f"  built: writing/{post['slug']}.html  ({post['title']})")

    build_index(posts)
    print(f"  index: writing/index.html  ({len(posts)} posts)")


if __name__ == "__main__":
    main()

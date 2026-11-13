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
DL_DIR    = Path("writing/downloads")
AUTHOR    = "Terrace"
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


def has_chapters(md_text):
    """Chapters are `#` headings (one per manuscript file). The post title is
    the page's <h1>, so they render one level down, as <h2>, and a chapter's
    own `##` (a recipe, a list) becomes <h3>."""
    return re.search(r"^# ", md_text, flags=re.M) is not None


def md_to_html(md_text):
    """Run pandoc to convert Markdown to an HTML fragment."""
    shift = ["--shift-heading-level-by=1"] if has_chapters(md_text) else []
    result = subprocess.run(
        ["pandoc", "--from=markdown", "--to=html"] + shift,
        input=md_text, capture_output=True, text=True, check=True
    )
    return result.stdout


def build_epub(md_path, meta, body_md, slug):
    """Write writing/downloads/<slug>.epub, one EPUB chapter per `#` heading.

    The identifier and SOURCE_DATE_EPOCH are pinned so an unchanged post
    rebuilds to the same bytes (no churn in git)."""
    DL_DIR.mkdir(exist_ok=True)
    out = DL_DIR / f"{slug}.epub"
    args = ["pandoc", "--from=markdown", "--to=epub3", "--split-level=1",
            "--metadata", f"title={meta.get('title', slug)}",
            "--metadata", f"author={AUTHOR}",
            "--metadata", "lang=en",
            "--metadata", f"identifier=https://terrace.zone/writing/{slug}.html",
            "-o", str(out)]
    if meta.get("date"):
        args += ["--metadata", f"date={meta['date']}"]
    if meta.get("summary"):
        args += ["--metadata", f"description={meta['summary']}"]
    if len(re.findall(r"^# ", body_md, flags=re.M)) >= 2:
        args += ["--toc", "--toc-depth=1"]
    cover = next((COVER_DIR / f"{slug}.{e}" for e in ("jpg", "jpeg", "png", "webp")
                  if (COVER_DIR / f"{slug}.{e}").exists()), None)
    if cover:
        args += ["--epub-cover-image", str(cover)]
    env = dict(os.environ, SOURCE_DATE_EPOCH="0")
    if meta.get("date"):
        import datetime
        d = datetime.datetime.strptime(meta["date"], "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        env["SOURCE_DATE_EPOCH"] = str(int(d.timestamp()))
    subprocess.run(args, input=body_md, text=True, check=True, env=env)
    return out


def build_post(md_path, template_html):
    raw = md_path.read_text(encoding="utf-8")
    meta, body_md = parse_front_matter(raw)

    title = meta.get("title", md_path.stem.replace("-", " ").title())
    date  = meta.get("date", "")
    body_html = md_to_html(body_md)

    ao3_url    = meta.get("ao3_url", "")
    fandom     = meta.get("fandom", "")
    word_count = meta.get("word_count", "")
    summary    = meta.get("summary", "")

    wc_block  = f' · {word_count} words' if word_count else ""
    fan_block = f' · {fandom}' if fandom else ""
    ao3_block = (f' · <a href="{ao3_url}" target="_blank" rel="noopener">AO3</a>'
                 if ao3_url else "")
    sum_block = (f'<p class="post-summary">{summary}</p>' if summary else "")
    slug = md_path.stem
    epub = build_epub(md_path, meta, body_md, slug)
    dl_block = f' · <a href="downloads/{epub.name}" download>EPUB</a>'

    html = (template_html
            .replace("{{TITLE}}", title)
            .replace("{{DATE}}", date)
            .replace("{{WORD_COUNT_BLOCK}}", wc_block)
            .replace("{{FANDOM_BLOCK}}", fan_block)
            .replace("{{AO3_LINK}}", ao3_block)
            .replace("{{DOWNLOAD_BLOCK}}", dl_block)
            .replace("{{SUMMARY_BLOCK}}", sum_block)
            .replace("{{BODY}}", body_html))

    out_path = OUT_DIR / f"{slug}.html"
    out_path.write_text(html, encoding="utf-8")
    return {"title": title, "date": date, "slug": slug,
            "word_count": word_count, "summary": summary,
            "cover": meta.get("cover", ""), "tile": meta.get("tile", ""),
            "pin": meta.get("pin", "")}


COVER_DIR = Path("images/covers")


def words(p):
    try:
        return int(p["word_count"].replace(",", ""))
    except (ValueError, AttributeError):
        return 0


def cover_for(p):
    """A painting for the tile: front-matter `cover:`, else images/covers/<slug>.*"""
    if p["cover"]:
        return p["cover"]
    for ext in ("webp", "jpg", "jpeg", "png"):
        if (COVER_DIR / f"{p['slug']}.{ext}").exists():
            return f"../images/covers/{p['slug']}.{ext}"
    return ""


def tile_shape(p):
    """`tile: wide|tall|square` in front matter wins; else long works get a wide tile."""
    if p["tile"] in ("wide", "tall", "square"):
        return p["tile"]
    return "wide" if words(p) >= 10000 else "square"


def build_index(posts):
    """Rebuild the POSTS_START … POSTS_END block in writing/index.html as a gallery."""
    # newest first; posts with `pin: N` in front matter go up front, in N order
    posts_sorted = sorted(posts, key=lambda p: p["date"], reverse=True)
    posts_sorted.sort(key=lambda p: int(p["pin"]) if p["pin"].isdigit() else 10**6)

    if not posts_sorted:
        items_html = '<p style="color: var(--muted); font-size: 0.95rem;">Nothing here yet.</p>'
    else:
        tiles = []
        for p in posts_sorted:
            cover = cover_for(p)
            art = (f'<img src="{cover}" alt="" loading="lazy">' if cover
                   else '<span class="tile-pending">painting to come</span>')
            wc = f' · {p["word_count"]} words' if p["word_count"] else ""
            tiles.append(
                f'<li class="tile tile-{tile_shape(p)}">'
                f'<div class="tile-art{"" if cover else " is-pending"}">{art}</div>'
                f'<div class="tile-body">'
                f'<span class="tile-title"><a href="{p["slug"]}.html">{p["title"]}</a></span>'
                f'<span class="tile-meta">{p["date"]}{wc}</span>'
                f'</div></li>'
            )
        items_html = '<ul class="gallery">\n' + "\n".join(tiles) + "\n</ul>"

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

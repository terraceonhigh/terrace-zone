#!/usr/bin/env python3
"""
Convert writing/posts/*.md → writing/*.html and regenerate writing/index.html.
Requires: pandoc (brew install pandoc); for PDFs, WeasyPrint (see tools/make-pdfs.py)

Usage:
    python3 build.py
"""

import os
import re
import subprocess
import sys
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


def load_credits():
    """images/covers/CREDITS.md lines `- `slug`: credit text. <url>` -> {slug: (html, url)}"""
    out = {}
    path = COVER_DIR / "CREDITS.md"
    if not path.exists():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^- `([^`]+)`: (.*?)\s*<(https?://[^>]+)>\s*$", line)
        if m:
            text = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", m.group(2).strip())
            out[m.group(1)] = (text, m.group(3))
    return out


def add_cover(html, slug, meta, credits):
    """Put the story's painting behind its title (a .post-hero), credit below."""
    src = cover_for({"cover": meta.get("cover", ""), "slug": slug})
    if not src:
        return html
    credit = ""
    if slug in credits:
        text, url = credits[slug]
        full = re.sub(r"<[^>]+>", "", text)
        credit = (f'<a class="cover-credit" href="{url}" target="_blank" rel="noopener" '
                  f'title="{full}">{short_credit(text)}</a>')
    fig = f'<figure class="post-cover"><img src="{src}" alt="" decoding="async"></figure>'
    return re.sub(r'(<header class="post-header"[^>]*>.*?</header>)',
                  lambda m: f'<div class="post-hero">{fig}{m.group(1)}{credit}</div>',
                  html, count=1, flags=re.S)


def short_credit(text):
    """'<em>A Mermaid</em>, John William Waterhouse (British, 1849–1917), 1900.
    Public domain.' -> '<em>A Mermaid</em>, John William Waterhouse, 1900'"""
    t = re.sub(r" \([^)]*\)", "", text)          # (nationality, dates)
    t = re.split(r"(?<!\bc)\.\s(?=[A-Z])", t, maxsplit=1)[0]  # first sentence ("c. 1888" is not an end)
    return t.rstrip(". ")


def build_post(md_path, template_html, credits=None):
    raw = md_path.read_text(encoding="utf-8")
    meta, body_md = parse_front_matter(raw)

    title = meta.get("title", md_path.stem.replace("-", " ").title())
    date  = meta.get("date", "")
    body_html = md_to_html(body_md)

    ao3_url    = meta.get("ao3_url", "")
    word_count = meta.get("word_count", "")
    summary    = meta.get("summary", "")

    # D layout: the painting carries the title alone; the tagline sits under it
    # as an epigraph; downloads and AO3 sit in a quiet line after the story
    # (reader.js also lists them in its Download menu)
    sum_block = (f'<p class="post-epigraph">{summary}</p>' if summary else "")
    slug = md_path.stem
    epub = build_epub(md_path, meta, body_md, slug)
    # the PDF is typeset from the same Markdown afterwards (tools/make-pdfs.py)
    links = [f'<a href="downloads/{epub.name}" download>EPUB</a>',
             f'<a href="downloads/{slug}.pdf" download>PDF</a>']
    # EPUB/PDF line for readers without JS (reader.js shows them as the
    # Download menu instead), then the AO3 card where a reader finishes
    links_block = ('<p class="post-links">Download '
                   + '<span class="sep"> · </span>'.join(links) + "</p>")
    if ao3_url:
        links_block += ('<aside class="ao3-card"><p>Liked it? Kudos and comments live on AO3.</p>'
                        f'<a class="pill" href="{ao3_url}" target="_blank" rel="noopener">'
                        'Leave kudos on AO3 ↗</a></aside>')
    wc_attr = word_count.replace(",", "")

    html = (template_html
            .replace("{{TITLE}}", title)
            .replace("{{WORDS}}", wc_attr)
            .replace("{{SUMMARY_BLOCK}}", sum_block)
            .replace("{{LINKS_BLOCK}}", links_block)
            .replace("{{BODY}}", body_html))
    html = add_cover(html, slug, meta, credits or {})

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

    credits = load_credits()
    posts = []
    for md in md_files:
        post = build_post(md, template_html, credits)
        posts.append(post)
        print(f"  built: writing/{post['slug']}.html  ({post['title']})")

    build_index(posts)
    print(f"  index: writing/index.html  ({len(posts)} posts)")

    # PDFs: typeset by WeasyPrint; skipped (old PDFs kept) when it isn't
    # installed in this Python
    try:
        import weasyprint  # noqa: F401
    except ImportError:
        print("  pdf: SKIPPED, WeasyPrint not installed; existing PDFs kept "
              "(pip install weasyprint)")
        return
    subprocess.run([sys.executable, "tools/make-pdfs.py"], check=True)


if __name__ == "__main__":
    main()

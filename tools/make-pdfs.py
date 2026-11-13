#!/usr/bin/env python3
"""Typeset writing/posts/<slug>.md as writing/downloads/<slug>.pdf (A5 book).

pandoc turns the Markdown into a standalone HTML book (tools/pdf/template.html:
title page, contents for works with chapters), and WeasyPrint sets it with
tools/pdf/book.css (page numbers, running chapter title, contents with page
numbers). No browser. build.py calls this after writing the site.

Locally a PDF is only re-set when its inputs change (writing/downloads/
pdf-inputs.json), so repeat builds are quick.

Requires: pandoc; pip install weasyprint
Usage:    python3 tools/make-pdfs.py [slug ...] [--force]
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
POSTS = ROOT / "writing" / "posts"
DL = ROOT / "writing" / "downloads"
PDF_DIR = Path(__file__).resolve().parent / "pdf"
STAMPS = DL / "pdf-inputs.json"

sys.path.insert(0, str(ROOT))
from build import parse_front_matter, has_chapters  # noqa: E402


def inputs_hash(md):
    h = hashlib.sha256()
    for p in [md, Path(__file__), PDF_DIR / "template.html", PDF_DIR / "book.css"] + sorted((ROOT / "fonts").glob("*")):
        h.update(p.name.encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def book_html(md):
    meta, body = parse_front_matter(md.read_text(encoding="utf-8"))
    slug = md.stem
    args = ["pandoc", "--from=markdown", "--to=html5", "--standalone", "--section-divs",
            f"--template={PDF_DIR / 'template.html'}",
            "-M", f"title={meta.get('title', slug)}", "-V", f"slug={slug}",
            "-V", f"date={meta.get('date', '')}", "-V", f"words={meta.get('word_count', '')}"]
    if meta.get("summary"):
        args += ["-M", f"summary={meta['summary']}"]
    if has_chapters(body):
        args += ["--shift-heading-level-by=1", "--toc", "--toc-depth=2"]
    return subprocess.run(args, input=body, capture_output=True, text=True, check=True).stdout


def main(argv):
    force = "--force" in argv
    wanted = [a for a in argv if not a.startswith("--")]
    mds = [POSTS / f"{s}.md" for s in wanted] if wanted else \
        sorted(p for p in POSTS.glob("*.md") if not p.stem.startswith("_"))
    stamps = json.loads(STAMPS.read_text()) if STAMPS.exists() else {}
    from weasyprint import HTML
    DL.mkdir(exist_ok=True)
    failed = done = 0
    for md in mds:
        slug = md.stem
        out = DL / f"{slug}.pdf"
        hsh = inputs_hash(md)
        if not force and stamps.get(slug) == hsh and out.exists():
            continue
        try:  # one bad post must not stop the rest
            doc = HTML(string=book_html(md), base_url=str(PDF_DIR) + "/").render()
            doc.write_pdf(out)
            stamps[slug] = hsh
            done += 1
            print(f"  pdf: writing/downloads/{slug}.pdf  ({len(doc.pages)} pages)", flush=True)
        except Exception as e:
            failed += 1
            print(f"  pdf FAILED {slug}: {e}", flush=True)
    if not done and not failed:
        print("  pdf: all up to date")
    STAMPS.write_text(json.dumps(stamps, indent=1, sort_keys=True) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

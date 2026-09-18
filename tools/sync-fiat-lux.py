#!/usr/bin/env python3
"""
Rebuild writing/posts/fiat-lux.md from a fiatLux manuscript checkout.

The canary tracks every push: each manuscript/*.md file becomes one
chapter, joined by the same "---" scene-break rule chapters use inside
themselves, under a fixed front matter block.

Usage:
    tools/sync-fiat-lux.py <path-to-fiatLux-checkout>
"""

import datetime
import re
import sys
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "writing/posts/fiat-lux.md"

FRONT_MATTER = """---
title: Fiat Lux
date: {date}
ao3_url: https://archiveofourown.org/works/89851861
fandom: Original Work
word_count: {word_count}
summary: At the beginning, a restaurant advertised that they used locally grown tomatoes. A Cascadian university sleepwalks into statehood. Post-collapse nobledark fiction based on the Soviet collapse and Cuba's Período especial.
---

> This is the canary version of *Fiat Lux*. It changes more often and may contain rougher prose than the relatively stable version on AO3.
"""


def chapter_title(md_path):
    slug = re.sub(r"^\d+-", "", md_path.stem)
    return slug.replace("-", " ").title()


def main():
    manuscript_dir = Path(sys.argv[1]) / "manuscript"
    md_files = sorted(manuscript_dir.glob("*.md"))

    chapters = []
    word_count = 0
    for md in md_files:
        content = md.read_text(encoding="utf-8").strip()
        word_count += len(content.split())
        chapters.append(f"## {chapter_title(md)}\n\n{content}")

    body = "\n\n---\n\n".join(chapters)
    front = FRONT_MATTER.format(
        date=datetime.date.today().isoformat(),
        word_count=f"{word_count:,}",
    )
    OUT.write_text(f"{front}\n{body}\n", encoding="utf-8")
    print(f"wrote {OUT} ({word_count:,} words, {len(md_files)} chapters)")


if __name__ == "__main__":
    main()

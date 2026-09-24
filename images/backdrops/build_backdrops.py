#!/usr/bin/env python3
"""Build terrace.zone's duotone WebP backdrops from source scans."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageOps


# Comprador's parchment: sepia ink on the #f4ebe1 cream underlay by day,
# warm lamplit lines on a near-black ground by night.
LIGHT_BLACK = "#5a4a3f"
LIGHT_WHITE = "#f4ebe1"
DARK_BLACK = "#1c1612"
DARK_WHITE = "#cdb8a5"


def duotone(
    source: Path,
    destination: Path,
    *,
    dark: bool = False,
    invert: bool | None = None,
    width: int = 1920,
) -> None:
    with Image.open(source) as image:
        gray = ImageOps.grayscale(image)
        if gray.width > width:
            height = round(gray.height * width / gray.width)
            gray = gray.resize((width, height), Image.Resampling.LANCZOS)
        if invert is None:
            invert = dark
        if invert:
            gray = ImageOps.invert(gray)
        colors = (DARK_BLACK, DARK_WHITE) if dark else (LIGHT_BLACK, LIGHT_WHITE)
        result = ImageOps.colorize(gray, *colors)
        result.save(destination, "WEBP", quality=76, method=6)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source_dir",
        type=Path,
        help="directory containing the six source files listed in README.md",
    )
    args = parser.parse_args()
    source = args.source_dir
    output = Path(__file__).resolve().parent

    pairs = {
        "roman-forum": source / "roman-forum.jpg",
        "bibliotheque-nationale": source / "bibliotheque-nationale.jpg",
        "cenotaphe-newton": source / "newton-elevation.jpg",
    }
    for name, image in pairs.items():
        duotone(image, output / f"{name}-light.webp")
        duotone(image, output / f"{name}-dark.webp", dark=True)

    # The portrait image gets a smaller width cap while still more than tripling
    # the resolution of the old 455-pixel asset.
    tower = source / "round-tower.jpg"
    duotone(tower, output / "round-tower-light.webp", width=1600)
    duotone(tower, output / "round-tower-dark.webp", dark=True, width=1600)

    # These two complementary sections are intentionally cross-mapped instead
    # of creating the dark file by inverting the light file.
    duotone(source / "newton-day-section.jpg", output / "backdrop-light.webp")
    duotone(
        source / "newton-night-section.jpg",
        output / "backdrop-dark.webp",
        dark=True,
        invert=False,
    )


if __name__ == "__main__":
    main()

# Backdrop sources and processing

The backdrops are public-domain architectural drawings converted to duotone
WebP files. The color is baked into the images; CSS only chooses and positions
them.

`build_backdrops.py` first converts each scan to grayscale. Light variants map
black to a sepia ink `#5a4a3f` and white to Comprador's parchment `#f4ebe1`.
Dark variants invert the grayscale, then map black to `#1c1612` and white to
`#cdb8a5`. Landscape files are capped
at 1920 pixels wide, the portrait Round Tower at 1600 pixels, and all are
encoded as WebP at quality 76.

The default Newton backdrop is the exception: its light and dark files use the
two complementary day/night cross-sections directly, rather than inverting a
single drawing.

Expected source filenames:

- `round-tower.jpg` — Piranesi, *The Round Tower*, first edition, from
  [Wikimedia Commons](https://commons.wikimedia.org/wiki/File:Giovanni_Battista_Piranesi_-_Le_Carceri_d%27Invenzione_-_First_Edition_-_1750_-_03_-_The_Round_Tower.jpg)
- `roman-forum.jpg` — Piranesi, *Foro antico Romano*, from
  [SMK Open](https://www.open.smk.dk/en/artwork/image/KKSgb9845/16)
- `bibliotheque-nationale.jpg` — Boullée, project for the royal library,
  [Gallica btv1b77010108, plate 9](https://gallica.bnf.fr/ark:/12148/btv1b77010108/f9.item)
- `newton-elevation.jpg` — Boullée, Newton cenotaph perspective elevation,
  [Gallica btv1b7701015b, plate 2](https://gallica.bnf.fr/ark:/12148/btv1b7701015b/f2.item)
- `newton-day-section.jpg` and `newton-night-section.jpg` — the matching
  [day](https://gallica.bnf.fr/ark:/12148/btv1b7701015b/f4.item) and
  [night](https://gallica.bnf.fr/ark:/12148/btv1b7701015b/f5.item) sections.

Run `python3 images/backdrops/build_backdrops.py SOURCE_DIRECTORY` after naming
the downloaded scans as above. The Roman Forum source should be cropped to the
plate before processing; the current version uses the SMK IIIF region
`pct:14,13,67,62` at 2400 pixels wide.

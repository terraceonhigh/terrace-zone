# Deploying terrace.zone

The site is static files. `.github/workflows/pages.yml` builds it on every push to
`main` (`build.py`: post HTML, the gallery, EPUBs via pandoc, PDFs via WeasyPrint) and
deploys the result to Pages. `writing/downloads/` is build output and is not committed;
`writing/*.html` still is, so the repo previews without a build.

## Hosting: GitHub Pages

The repo is <https://github.com/terraceonhigh/terrace-zone>. Settings → Pages →
Source must be **GitHub Actions**. Pushing to `main` redeploys.

```bash
git push        # that's the whole deploy; watch it under Actions → Pages
```

To build locally: `pip install weasyprint` (optional; without it the PDFs are skipped),
pandoc 3.x on PATH, then `python3 build.py`.

### Custom domain ✅ live at https://terrace.zone

Done. For the record, the setup is:

- **Porkbun:** the apex `ALIAS terrace.zone` → `terraceonhigh.github.io` (Porkbun
  flattens it to GitHub's four A records: `185.199.108–111.153`). This replaced the
  default `pixie.porkbun.com` parking target.
- **GitHub:** Settings → Pages → Custom domain = `terrace.zone`, which committed the
  `CNAME` file at the repo root. **Don't delete `CNAME`** — losing it drops the domain.
- **HTTPS:** Let's Encrypt cert issued automatically, *Enforce HTTPS* on, so `http://`
  301s to `https://`.

`terraceonhigh.github.io/terrace-zone/` now redirects here. Every internal link and the
backdrop URLs are relative, so the site works at either location regardless.

> **Mail was not touched.** Only the apex ALIAS changed. The Proton MX, SPF,
> `protonmail-verification`, three DKIM CNAMEs and DMARC records are exactly as they
> were, as are the six tailnet subdomain A records (`forge`, `cloud`, `chat`, `media`,
> `qbit`, `cockpit` → the humboldt tailnet IP). Send yourself a test message anyway.

To revert to the parking page, set the apex ALIAS back to `pixie.porkbun.com`.

> **This repo is public and served in full.** `DEPLOY.md`, `build.py` and
> `writing/posts/*.md` are readable both on GitHub and over the web. Keep anything
> private out of it.

---

## Writing a new post

1. Create `writing/posts/my-post-title.md` with YAML front matter:

   ```markdown
   ---
   title: My Post Title
   date: 2026-09-15
   summary: One line, optional.
   ---

   Post body in Markdown.
   ```

2. Build and preview:

   ```bash
   python3 build.py
   python3 -m http.server 8080   # then open http://localhost:8080
   ```

3. Commit and push. Pages redeploys on its own.

> Files starting with `_` in `writing/posts/` are treated as drafts and skipped.

---

## Updating the portfolio

Edit `index.html` directly — no build step. The Work and Projects sections carry HTML
comments showing the pattern.

---

## Backdrops

`images/backdrops/` holds a light and a dark WebP per scene. `script.js` picks one at
random for the active theme, keeps it stable for the tab via `sessionStorage`, and
resolves it relative to its own URL. To add a scene, drop in `<name>-light.webp` and
`<name>-dark.webp` and add `"<name>"` to the `names` array in `script.js`.

Re-encode new sources rather than committing large PNGs — the originals were 6.8 MB
of PNG, 944 KB as WebP:

```bash
cwebp -q 82 source.png -o images/backdrops/<name>-light.webp
```

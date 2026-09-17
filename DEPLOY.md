# Deploying terrace.zone

The site is plain static files served straight from the repo root. There is no build
step on the host: `build.py` runs **locally** and its output (`writing/*.html`) is
committed.

## Hosting: GitHub Pages

The repo is <https://github.com/terraceonhigh/terrace-zone>, and Pages serves `main`
from the root. Pushing to `main` redeploys.

```bash
git push        # that's the whole deploy
```

> **Do not** set a build command that runs `build.py` on the host. It shells out to
> pandoc, which isn't present in hosted build images, so the deploy would fail. Build
> locally, commit the HTML.

### Custom domain

Pages serves the site at <https://terraceonhigh.github.io/terrace-zone/> until a custom
domain is set. Every internal link and the backdrop URLs are relative, so the site works
correctly at either location.

To put it on `terrace.zone`:

1. At your DNS provider, point the apex at GitHub Pages — either the four `A` records
   (`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) or an
   `ALIAS`/`CNAME` at `@` → `terraceonhigh.github.io` if the provider supports apex
   aliasing.
2. Repo → Settings → Pages → Custom domain → `terrace.zone` → Save. This writes a
   `CNAME` file into the repo.
3. Tick **Enforce HTTPS** once the certificate is issued (usually a few minutes).

> **Mail is unaffected.** These records only change HTTP/HTTPS routing; MX, SPF, DKIM
> and DMARC stay as they are. Send yourself a test message afterwards anyway.

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

# Deploying to Cloudflare Pages → terrace.zone

## One-time setup

### 1. Push to GitHub ✅ done

Cloudflare Pages can't reach forge.terrace.zone (tailnet-only), so the repo lives on
GitHub: <https://github.com/terraceonhigh/terrace-zone> (private). `origin` is already
set and `main` is pushed — from here on, `git push` is all that's needed.

It was created with:

```bash
gh repo create terrace-zone --private --source=. --push
```

### 2. Connect Cloudflare Pages

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com)
2. Workers & Pages → Create → Pages → Connect to Git
3. Select your `terrace-zone` repo
4. Build settings:
   - **Build command:** leave blank
   - **Build output directory:** `/` (root — serve the whole repo)
   - **Root directory:** leave blank

   > Do **not** set the build command to `python3 build.py`. That script shells out to
   > pandoc, which isn't in Cloudflare's build image, so the deploy would fail. Run
   > `build.py` locally and commit the generated `writing/*.html` — the repo is served
   > as-is.
5. Deploy

### 3. Add custom domain

In the Pages project → Custom domains → Add domain → `terrace.zone`

> **Heads up: the whole repo is served.** With output directory `/`, `DEPLOY.md`,
> `build.py`, `writing/posts/*.md` and `writing/_post_template.html` are all reachable
> publicly — and this file names your registrar, mail provider and `forge.terrace.zone`.
> If that bothers you, the simplest fix is to keep the ops notes out of the deployed
> repo (move this file to a private gist or your notes) before connecting Pages.

Cloudflare will tell you what DNS records to add. Since you're on **Porkbun**:

- Go to Porkbun → Domain Management → terrace.zone → DNS
- Add an **ALIAS** record: `@` → `<your-pages-project>.pages.dev`
  (Porkbun supports ALIAS at the apex; it behaves like CNAME but works for root domains)
- Cloudflare Pages handles TLS automatically — no lego cert needed for this

> **Mail records are untouched.** The ALIAS only affects HTTP/HTTPS traffic. Your Proton
> Mail MX, SPF, DKIM, and DMARC records stay where they are. Still, send a test email
> after the DNS change to confirm.

---

## Writing a new post

1. Create `writing/posts/my-post-title.md` with YAML front matter:

   ```markdown
   ---
   title: My Post Title
   date: 2026-09-15
   ---

   Post body in Markdown.
   ```

2. Build locally to preview:

   ```bash
   python3 build.py
   # opens writing/my-post-title.html
   ```

3. Commit and push — Cloudflare Pages rebuilds automatically.

> Files starting with `_` in `writing/posts/` are treated as drafts and skipped.

---

## Updating the portfolio

Edit `index.html` directly. The Work and Projects sections have HTML comments
showing the pattern. No build step needed — just edit, commit, push.

---

## Local preview

```bash
python3 -m http.server 8080
# open http://localhost:8080
```

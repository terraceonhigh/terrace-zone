# Deploying to Cloudflare Pages → terrace.zone

## One-time setup

### 1. Push to GitHub (or any public git host Cloudflare Pages can reach)

Cloudflare Pages can't reach forge.terrace.zone (tailnet-only). Use GitHub:

```bash
gh repo create terrace-zone --private --source=. --push
```

Or push manually to a new GitHub repo.

### 2. Connect Cloudflare Pages

1. Log into [dash.cloudflare.com](https://dash.cloudflare.com)
2. Workers & Pages → Create → Pages → Connect to Git
3. Select your `terrace-zone` repo
4. Build settings:
   - **Build command:** `python3 build.py`
   - **Build output directory:** `/` (root — serve the whole repo)
   - **Root directory:** leave blank
5. Deploy

### 3. Add custom domain

In the Pages project → Custom domains → Add domain → `terrace.zone`

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

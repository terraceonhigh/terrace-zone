---
title: Example Post
date: 2026-08-31
---

This is an example post. Delete or replace it with real writing.

Write posts as Markdown files in `writing/posts/`. Run `python3 build.py` to convert them to HTML and rebuild the post index.

## Front matter

Every post needs a `title` and `date` in YAML front matter at the top:

```yaml
---
title: My Post Title
date: 2026-09-01
---
```

The filename becomes the URL slug: `my-post-title.md` → `writing/my-post-title.html`.

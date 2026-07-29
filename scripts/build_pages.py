#!/usr/bin/env python3
"""Generate static HTML pages from data/daily/*.json and data/forecasts/*.json.

Run after adding, editing, or resolving an entry:
    python3 scripts/build_pages.py

Generates:
  entries/<date>.html    one dated permalink per daily entry
  forecasts/<id>.html    one permalink per forecast
  tags/<tag>.html        one topic-cluster page per unique tag, aggregating
                          every entry and forecast that carries it
  sitemap.xml            regenerated to list every URL above

Without real HTML permalinks, the archive only ever linked to raw JSON
files -- invisible to search engines and unshareable. This is what fixes
that. CI (validate-content.yml) re-runs this with --check and fails the
build if any generated file is out of date, so pages can't drift from the
JSON source of truth the way a hand-maintained page could.
"""

import glob
import html
import json
import os
import sys

SITE_URL = "https://thepandorabox.github.io"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHOR_NAME = "Mukesh Bansal"
AUTHOR_URL = f"{SITE_URL}/creator.html"

NAV = """<nav class="site-nav">
      <a href="{root}index.html#today">Today</a>
      <a href="{root}index.html#library">Architecture Library</a>
      <a href="{root}index.html#forecasts">Forecasts</a>
      <a href="{root}index.html#archive">Archive</a>
      <a href="{root}creator.html">Creator</a>
      <a href="https://github.com/thepandorabox/thepandorabox.github.io" target="_blank" rel="noopener">GitHub</a>
    </nav>"""

HEADER = """<header class="site-header">
  <div class="wrap header-row">
    <a class="brand" href="{root}index.html">
      <span class="brand-mark" aria-hidden="true"></span>
      <span class="brand-text">THE PANDORA<span class="accent">BOX</span></span>
    </a>
    {nav}
  </div>
</header>"""

FOOTER = """<footer class="site-footer">
  <div class="wrap footer-row">
    <span>&copy; <span class="js-year">2026</span> The Pandora Box &mdash; MIT Licensed</span>
    <a href="{root}index.html">Back to the box</a>
  </div>
</footer>"""

PAGE_SHELL = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="canonical" href="{canonical}">

<meta property="og:type" content="article">
<meta property="og:url" content="{canonical}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{description}">
<meta property="og:image" content="{site_url}/assets/og-image.png">

<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title}">
<meta name="twitter:description" content="{description}">
<meta name="twitter:image" content="{site_url}/assets/og-image.png">

<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'%3E%3Crect x='15' y='35' width='70' height='50' rx='4' fill='%23161b26' stroke='%23f2b134' stroke-width='4'/%3E%3Cpath d='M15 35 L50 15 L85 35' fill='none' stroke='%23f2b134' stroke-width='4' stroke-linejoin='round'/%3E%3Ccircle cx='50' cy='55' r='10' fill='%23f2b134'/%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{root}assets/css/style.css">
{jsonld}
</head>
<body>

<div class="grid-overlay" aria-hidden="true"></div>

{header}

<main class="article-main">
  <div class="wrap">
    <p class="breadcrumb"><a href="{root}index.html">Home</a> / {breadcrumb_tail}</p>
    {content}
  </div>
</main>

{footer}

<script src="{root}assets/js/share.js"></script>
<script data-goatcounter="https://thepandorabox.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>
"""


def esc(s):
    return html.escape(str(s), quote=True)


def truncate(s, n=155):
    s = s.strip()
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def render_shell(*, title, description, canonical, root, breadcrumb_tail, content, jsonld=""):
    return PAGE_SHELL.format(
        title=esc(title),
        description=esc(truncate(description)),
        canonical=canonical,
        site_url=SITE_URL,
        root=root,
        jsonld=jsonld,
        header=HEADER.format(root=root, nav=NAV.format(root=root)),
        breadcrumb_tail=breadcrumb_tail,
        content=content,
        footer=FOOTER.format(root=root),
    )


def load_daily():
    files = sorted(
        f for f in glob.glob(os.path.join(REPO_ROOT, "data/daily/*.json"))
        if os.path.basename(f) not in ("index.json", "TEMPLATE.json")
    )
    entries = []
    for path in files:
        with open(path) as fh:
            entries.append(json.load(fh))
    entries.sort(key=lambda e: e["date"])  # oldest -> newest, for prev/next
    return entries


def load_forecasts():
    files = sorted(
        f for f in glob.glob(os.path.join(REPO_ROOT, "data/forecasts/*.json"))
        if os.path.basename(f) not in ("index.json", "TEMPLATE.json")
    )
    forecasts = []
    for path in files:
        with open(path) as fh:
            forecasts.append(json.load(fh))
    forecasts.sort(key=lambda f: f["created"])
    return forecasts


def tag_pills(tags, root):
    return '<div class="tag-pills-inline">' + "".join(
        f'<a href="{root}tags/{esc(t)}.html">#{esc(t)}</a>' for t in tags
    ) + "</div>"


def share_row(url, title):
    x_url = f"https://twitter.com/intent/tweet?text={esc(title)}&url={esc(url)}"
    li_url = f"https://www.linkedin.com/sharing/share-offsite/?url={esc(url)}"
    return f"""<div class="share-row">
      <span class="share-label">Share</span>
      <a class="share-btn" href="{x_url}" target="_blank" rel="noopener">X / Twitter</a>
      <a class="share-btn" href="{li_url}" target="_blank" rel="noopener">LinkedIn</a>
      <button class="share-btn copy-link-btn" type="button">Copy link</button>
    </div>"""


def entry_jsonld(entry, url):
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": entry["title"],
        "datePublished": entry["date"],
        "dateModified": entry["date"],
        "author": {"@type": "Person", "name": AUTHOR_NAME, "url": AUTHOR_URL},
        "publisher": {"@type": "Organization", "name": "The Pandora Box", "url": SITE_URL},
        "description": entry["summary"],
        "mainEntityOfPage": url,
        "keywords": ", ".join(entry.get("tags", [])),
    }
    return f'<script type="application/ld+json">{json.dumps(data)}</script>'


def build_entry_page(entry, prev_e, next_e):
    root = "../"
    url = f"{SITE_URL}/entries/{entry['date']}.html"
    sources = "".join(
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a>'
        for s in entry.get("sources", [])
    )
    nav_links = []
    if prev_e:
        nav_links.append(f'<a class="nav-prev" href="{prev_e["date"]}.html">&larr; {esc(prev_e["title"])}</a>')
    else:
        nav_links.append('<span class="nav-spacer"></span>')
    if next_e:
        nav_links.append(f'<a class="nav-next" href="{next_e["date"]}.html">{esc(next_e["title"])} &rarr;</a>')
    else:
        nav_links.append('<span class="nav-spacer"></span>')

    content = f"""<article class="article-card">
      <div class="today-date">
        <span>{entry['date']}</span>
        <span class="today-pattern-tag">{esc(entry.get('pattern', ''))}</span>
      </div>
      <h1>{esc(entry['title'])}</h1>
      <p class="summary">{esc(entry['summary'])}</p>
      <div class="key-learning">
        <strong>Key learning</strong>
        {esc(entry.get('key_learning', ''))}
      </div>
      <div class="sources">{sources}</div>
      <p class="related-pattern">Part of the <a href="{root}index.html#library">architecture library</a>: {esc(entry.get('pattern', ''))}</p>
      {tag_pills(entry.get('tags', []), root)}
      {share_row(url, entry['title'])}
    </article>
    <div class="article-nav">{''.join(nav_links)}</div>"""

    return render_shell(
        title=f"{entry['title']} — The Pandora Box",
        description=entry["summary"],
        canonical=url,
        root=root,
        breadcrumb_tail=f'<a href="{root}index.html#archive">Archive</a> / {esc(entry["title"])}',
        content=content,
        jsonld=entry_jsonld(entry, url),
    )


def build_forecast_page(f):
    root = "../"
    url = f"{SITE_URL}/forecasts/{f['id']}.html"
    pct = round(f["probability"] * 100)
    sources = "".join(
        f'<a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])}</a>'
        for s in f.get("sources", [])
    )
    resolution_html = ""
    if f["status"] == "resolved":
        correct = f.get("outcome") is True
        resolution_html = f"""<div class="key-learning">
          <strong>{"Correct" if correct else "Wrong"} &mdash; resolved {esc(f['resolution_date'])}</strong>
          {esc(f.get('resolution_note') or '')}
        </div>"""

    content = f"""<article class="article-card">
      <div class="today-date">
        <span>{esc(f['category'])}</span>
        <span class="today-pattern-tag">{pct}% likely at creation</span>
      </div>
      <h1>{esc(f['question'])}</h1>
      <p class="reasoning">{esc(f['reasoning'])}</p>
      <div class="key-learning">
        <strong>Resolution criteria</strong>
        {esc(f['resolution_criteria'])}
      </div>
      {resolution_html}
      <div class="sources">{sources}</div>
      {tag_pills(f.get('tags', []), root)}
      {share_row(url, f['question'])}
    </article>
    <div class="article-nav"><a href="{root}index.html#forecasts">&larr; All forecasts</a></div>"""

    return render_shell(
        title=f"Forecast: {truncate(f['question'], 70)} — The Pandora Box",
        description=f['question'],
        canonical=url,
        root=root,
        breadcrumb_tail=f'<a href="{root}index.html#forecasts">Forecasts</a> / {esc(truncate(f["question"], 60))}',
        content=content,
    )


def build_tag_page(tag, entries, forecasts):
    root = "../"
    url = f"{SITE_URL}/tags/{tag}.html"
    items = []
    for e in sorted(entries, key=lambda x: x["date"], reverse=True):
        items.append((e["date"], f"""<a class="tag-page-item" href="{root}entries/{e['date']}.html">
          <div class="tag-item-meta">{e['date']} &middot; daily entry</div>
          <div class="tag-item-title">{esc(e['title'])}</div>
        </a>"""))
    for f in sorted(forecasts, key=lambda x: x["created"], reverse=True):
        items.append((f["created"], f"""<a class="tag-page-item" href="{root}forecasts/{f['id']}.html">
          <div class="tag-item-meta">{f['created']} &middot; forecast &middot; {round(f['probability']*100)}%</div>
          <div class="tag-item-title">{esc(f['question'])}</div>
        </a>"""))
    items.sort(key=lambda pair: pair[0], reverse=True)
    list_html = "\n".join(html_ for _, html_ in items) or "<p>Nothing tagged yet.</p>"

    content = f"""<p class="eyebrow">// TAG</p>
    <h1 style="margin: 4px 0 20px;">#{esc(tag)}</h1>
    <div class="tag-page-list">{list_html}</div>"""

    return render_shell(
        title=f"#{tag} — The Pandora Box",
        description=f"Every daily entry and forecast tagged #{tag} on The Pandora Box.",
        canonical=url,
        root=root,
        breadcrumb_tail=f"#{esc(tag)}",
        content=content,
    )


def build_sitemap(entries, forecasts, tags):
    urls = [
        (f"{SITE_URL}/", "daily", "1.0"),
        (f"{SITE_URL}/creator.html", "monthly", "0.3"),
    ]
    for e in entries:
        urls.append((f"{SITE_URL}/entries/{e['date']}.html", "yearly", "0.6"))
    for f in forecasts:
        urls.append((f"{SITE_URL}/forecasts/{f['id']}.html", "monthly", "0.5"))
    for t in sorted(tags):
        urls.append((f"{SITE_URL}/tags/{t}.html", "weekly", "0.4"))

    entries_xml = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n    <changefreq>{freq}</changefreq>\n    <priority>{prio}</priority>\n  </url>"
        for loc, freq, prio in urls
    )
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{entries_xml}\n</urlset>\n'


def generate():
    entries = load_daily()
    forecasts = load_forecasts()

    files = {}

    for i, e in enumerate(entries):
        prev_e = entries[i - 1] if i > 0 else None
        next_e = entries[i + 1] if i < len(entries) - 1 else None
        files[f"entries/{e['date']}.html"] = build_entry_page(e, prev_e, next_e)

    for f in forecasts:
        files[f"forecasts/{f['id']}.html"] = build_forecast_page(f)

    tag_map = {}
    for e in entries:
        for t in e.get("tags", []):
            tag_map.setdefault(t, {"entries": [], "forecasts": []})["entries"].append(e)
    for f in forecasts:
        for t in f.get("tags", []):
            tag_map.setdefault(t, {"entries": [], "forecasts": []})["forecasts"].append(f)

    for t, group in tag_map.items():
        files[f"tags/{t}.html"] = build_tag_page(t, group["entries"], group["forecasts"])

    files["sitemap.xml"] = build_sitemap(entries, forecasts, tag_map.keys())

    return files


def main():
    files = generate()

    if "--check" in sys.argv:
        mismatches = []
        for rel_path, content in files.items():
            abs_path = os.path.join(REPO_ROOT, rel_path)
            if not os.path.exists(abs_path):
                mismatches.append(f"missing: {rel_path}")
                continue
            with open(abs_path) as fh:
                if fh.read() != content:
                    mismatches.append(f"stale: {rel_path}")

        # also catch generated files on disk that no longer have a source
        for existing in glob.glob(os.path.join(REPO_ROOT, "entries/*.html")) + \
                         glob.glob(os.path.join(REPO_ROOT, "forecasts/*.html")) + \
                         glob.glob(os.path.join(REPO_ROOT, "tags/*.html")):
            rel = os.path.relpath(existing, REPO_ROOT)
            if rel not in files:
                mismatches.append(f"orphaned: {rel}")

        if mismatches:
            print("Generated pages are out of date — run `python3 scripts/build_pages.py` and commit the result:")
            for m in mismatches:
                print(f"  - {m}")
            sys.exit(1)
        print(f"OK — {len(files)} generated files (entries/forecasts/tags/sitemap) are up to date.")
        return

    for rel_path, content in files.items():
        abs_path = os.path.join(REPO_ROOT, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, "w") as fh:
            fh.write(content)

    print(f"Wrote {len(files)} generated files.")


if __name__ == "__main__":
    main()

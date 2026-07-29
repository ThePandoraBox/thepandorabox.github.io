# The Pandora Box

**An agentic ecosystem in a box.** A daily-synthesized field guide to agentic
AI architecture — hosted as a plain static site at
[thepandorabox.github.io](https://thepandorabox.github.io).

## What this is

Three layers:

1. **The architecture library** (`assets/js/app.js`) — a hand-curated,
   stable reference of the recurring patterns agentic systems keep
   converging on: prompt chaining, routing, parallelization,
   orchestrator-workers, evaluator-optimizer, ReAct, Reflexion, memory
   architectures, autonomous agent loops, and human-in-the-loop gates.
2. **The daily log** (`data/daily/*.json`) — one new entry added per day by
   an automated agent that researches recent developments in agentic
   architecture (papers, engineering blogs, trending repos) and synthesizes
   a short, specific write-up.
3. **Forecasts** (`data/forecasts/*.json`) — specific, checkable predictions
   about where agentic AI is headed, each with a probability and a
   resolution date, scored against reality once that date arrives.

See [`AUTOMATION.md`](AUTOMATION.md) for exactly how the agent-driven loop
behind (2) and (3) works.

The site itself is a handful of hand-written static pages (`index.html`,
`creator.html`, `404.html` + `assets/`) that fetch the JSON above
client-side and render it, plus a set of **generated** static pages —
`entries/*.html`, `forecasts/*.html`, `tags/*.html` — one dated permalink
per daily entry and forecast, and one topic-cluster page per tag, so
individual entries are actually indexable and shareable instead of being
raw JSON responses. `scripts/build_pages.py` generates these (and
`sitemap.xml`) from the JSON source of truth. No build step for the
hand-written pages, no server, no framework anywhere.

## Local development

It's plain static files — any local HTTP server works:

```sh
python3 -m http.server 8000
# then open http://localhost:8000
```

(Opening `index.html` directly via `file://` won't work — the page fetches
JSON with `fetch()`, which browsers block on the `file://` scheme.)

## Hosting

This repo is named `thepandorabox.github.io`, so GitHub Pages serves it
automatically once enabled. Two ways to enable it:

- **Deploy from a branch** (simplest): Settings → Pages → Source: Deploy
  from a branch → `master` / `root`.
- **GitHub Actions** (recommended, already wired up): Settings → Pages →
  Source: "GitHub Actions". `.github/workflows/deploy-pages.yml` then
  validates content and deploys on every push to `master`.

## Adding or editing content by hand

- **Daily entry**: copy `data/daily/TEMPLATE.json` to
  `data/daily/YYYY-MM-DD.json`, fill it in, add a row to
  `data/daily/index.json`.
- **Forecast**: copy `data/forecasts/TEMPLATE.json` to
  `data/forecasts/<id>.json`, fill it in — `resolution_criteria` must name
  an exact, checkable fact — and add a row to `data/forecasts/index.json`.
- Then run both generators and commit their output:

  ```sh
  python3 scripts/build_feed.py    # refreshes feed.xml
  python3 scripts/build_pages.py   # refreshes entries/, forecasts/, tags/, sitemap.xml
  ```

`.github/workflows/validate-content.yml` checks schema, index consistency,
and that neither generator's output has drifted, on every push that
touches generated content.

## License

MIT — see [`LICENSE`](LICENSE).

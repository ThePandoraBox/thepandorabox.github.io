# The Pandora Box

**An agentic ecosystem in a box.** A daily-synthesized field guide to agentic
AI architecture — hosted as a plain static site at
[thepandorabox.github.io](https://thepandorabox.github.io).

## What this is

Two layers:

1. **The architecture library** (`assets/js/app.js`) — a hand-curated,
   stable reference of the recurring patterns agentic systems keep
   converging on: prompt chaining, routing, parallelization,
   orchestrator-workers, evaluator-optimizer, ReAct, Reflexion, memory
   architectures, autonomous agent loops, and human-in-the-loop gates.
2. **The daily log** (`data/daily/*.json`) — one new entry added per day by
   an automated agent that researches recent developments in agentic
   architecture (papers, engineering blogs, trending repos) and synthesizes
   a short, specific write-up. See [`AUTOMATION.md`](AUTOMATION.md) for
   exactly how that loop runs.

The site itself is a single static page (`index.html` + `assets/`) that
fetches `data/daily/index.json` client-side and renders the latest entry
and the full archive. No build step, no server, no framework.

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
automatically once enabled: **Settings → Pages → Source: Deploy from a
branch → `master` / `root`**. No Actions build step is required for plain
HTML/CSS/JS.

## Adding or editing a daily entry by hand

Copy `data/daily/TEMPLATE.json` to `data/daily/YYYY-MM-DD.json`, fill it
in, and add a matching row to `data/daily/index.json` (newest first isn't
required — the front end sorts by date). A GitHub Actions workflow
(`.github/workflows/validate-content.yml`) checks schema and consistency
on every push that touches `data/daily/`.

## License

MIT — see [`LICENSE`](LICENSE).

#!/usr/bin/env python3
"""Regenerate feed.xml from data/daily/*.json.

Run this after adding or editing a daily entry:
    python3 scripts/build_feed.py

CI (validate-content.yml) re-runs this and fails the build if feed.xml
doesn't match, so it can't silently drift from the JSON entries.
"""

import glob
import json
import os
import sys
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape

SITE_URL = "https://thepandorabox.github.io"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_entries():
    files = sorted(
        f for f in glob.glob(os.path.join(REPO_ROOT, "data/daily/*.json"))
        if os.path.basename(f) not in ("index.json", "TEMPLATE.json")
    )
    entries = []
    for path in files:
        with open(path) as fh:
            entries.append(json.load(fh))
    entries.sort(key=lambda e: e["date"], reverse=True)
    return entries


def build_feed(entries):
    items = []
    for e in entries:
        pub_date = format_datetime(
            datetime.strptime(e["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
        )
        link = f"{SITE_URL}/data/daily/{e['date']}.json"
        items.append(f"""  <item>
    <title>{escape(e['title'])}</title>
    <link>{escape(link)}</link>
    <guid isPermaLink="false">{escape(e['slug'])}-{e['date']}</guid>
    <pubDate>{pub_date}</pubDate>
    <description>{escape(e['summary'])}</description>
  </item>""")

    latest_date = entries[0]["date"] if entries else "1970-01-01"
    last_build = format_datetime(
        datetime.strptime(latest_date, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    )

    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>The Pandora Box — Daily Log</title>
  <link>{SITE_URL}/</link>
  <description>A daily-synthesized reference for agentic AI architecture patterns.</description>
  <language>en-us</language>
  <lastBuildDate>{last_build}</lastBuildDate>
{chr(10).join(items)}
</channel>
</rss>
"""


def main():
    entries = load_entries()
    feed_xml = build_feed(entries)
    out_path = os.path.join(REPO_ROOT, "feed.xml")

    if "--check" in sys.argv:
        with open(out_path) as fh:
            current = fh.read()
        if current != feed_xml:
            print("feed.xml is out of date — run `python3 scripts/build_feed.py` and commit the result.")
            sys.exit(1)
        print("feed.xml is up to date.")
        return

    with open(out_path, "w") as fh:
        fh.write(feed_xml)
    print(f"Wrote {out_path} ({len(entries)} entries).")


if __name__ == "__main__":
    main()

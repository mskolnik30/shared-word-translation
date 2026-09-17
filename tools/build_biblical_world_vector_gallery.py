#!/usr/bin/env python3
"""Build a local review gallery for Biblical World vector candidates."""

from __future__ import annotations

import html
import json
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
VECTOR_DIR = ROOT / "resources" / "biblical-world" / "candidates" / "vectors"
MANIFEST = VECTOR_DIR / "manifest.json"
GALLERY = VECTOR_DIR / "review-gallery.html"


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cards = []
    for entry in data["entries"]:
        src = Path(entry["file"]).name
        sources = "".join(
            f'<li><a href="{html.escape(url)}">{html.escape(urlparse(url).netloc)}</a></li>'
            for url in entry["sources"]
        ) or "<li>The listed Bible passages supply the content.</li>"
        kind = "Geographic map" if entry["candidate_format"] == "geographic-orientation-map" else "Reading guide"
        cards.append(f'''<article class="card">
  <p class="kind">{kind} · review required</p>
  <h2>{html.escape(entry["title"])}</h2>
  <a href="{html.escape(src)}"><img src="{html.escape(src)}" alt="{html.escape(entry["alt_text"])}"></a>
  <details><summary>Sources and accessibility notes</summary>
    <p><strong>Bible passages:</strong> {html.escape('; '.join(entry['primary_texts']))}</p>
    <p><strong>Image description:</strong> {html.escape(entry['alt_text'])}</p>
    <ul>{sources}</ul>
  </details>
</article>''')
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Fluent Companion visual review</title>
<style>
:root{{--paper:#f7f2e8;--panel:#fffdfc;--navy:#19354d;--teal:#2b7773;--rust:#a6533f;--ink:#26333b;--line:#cad5d2}}
*{{box-sizing:border-box}} body{{margin:0;background:var(--paper);color:var(--ink);font:16px/1.5 system-ui,sans-serif}}
header{{background:var(--navy);color:#fff;padding:2rem clamp(1rem,4vw,4rem)}} header p{{max-width:75ch}}
main{{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:1.5rem;padding:2rem clamp(1rem,4vw,4rem)}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:1rem;box-shadow:0 6px 22px #19354d18}}
h1,h2{{line-height:1.15}} h2{{font-size:1.25rem;margin:.35rem 0 1rem}} .kind{{color:var(--rust);font-size:.78rem;font-weight:800;letter-spacing:.06em;text-transform:uppercase;margin:0}}
img{{display:block;width:100%;height:auto;border:1px solid var(--line);border-radius:10px;background:#fff}}
summary{{cursor:pointer;color:var(--teal);font-weight:700;margin-top:1rem}} a{{color:var(--teal);overflow-wrap:anywhere}}
</style></head><body>
<header><h1>Fluent Companion visual review</h1><p>{len(cards)} unpublished maps and reading guides. Select any image to inspect it at full size. Publication is blocked until historical, theological, accessibility, and visual review is complete.</p></header>
<main>{''.join(cards)}</main></body></html>
'''
    GALLERY.write_text(page, encoding="utf-8")
    print(GALLERY.relative_to(ROOT))


if __name__ == "__main__":
    main()

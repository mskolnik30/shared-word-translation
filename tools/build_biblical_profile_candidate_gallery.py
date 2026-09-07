#!/usr/bin/env python3
"""Build a local review gallery for the blocked profile candidates."""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANDIDATE_DIR = ROOT / "resources/biblical-world/profiles/candidates"
MANIFEST = CANDIDATE_DIR / "manifest.json"
OUTPUT = CANDIDATE_DIR / "review-gallery.html"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def main() -> None:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cards = []
    for entry in data["entries"]:
        sources = "".join(f'<li><a href="{esc(source)}">{esc(source)}</a></li>' for source in entry["sources"])
        notes = "".join(f"<li>{esc(note)}</li>" for note in entry["red_team_notes"])
        cards.append(
            f"""
            <article class="card">
              <img src="{esc(entry['file'])}" alt="{esc(entry['alt_text'])}">
              <div class="body">
                <p class="tag">BLOCKED · HUMAN REVIEW REQUIRED</p>
                <h2>{esc(entry['subject'])}</h2>
                <p><strong>Class:</strong> {esc(entry['candidate_type'])}</p>
                <p><strong>Period/region:</strong> {esc(entry['period_region'])}</p>
                <p><strong>Caption:</strong> {esc(entry['caption'])}</p>
                <details><summary>Alternative text</summary><p>{esc(entry['alt_text'])}</p></details>
                <details><summary>Red-team notes</summary><ul>{notes}</ul></details>
                <details><summary>Sources</summary><ul>{sources}</ul></details>
                <details><summary>Generation prompt</summary><p>{esc(entry['prompt'])}</p></details>
                <p class="hash"><strong>SHA-256:</strong> {esc(entry['sha256'])}</p>
              </div>
            </article>
            """.strip()
        )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Biblical Profile Candidate Review</title>
  <style>
    :root {{ color-scheme: light; --navy:#17324d; --rust:#9a4f33; --paper:#f6f1e7; --ink:#202020; }}
    * {{ box-sizing:border-box; }}
    body {{ margin:0; background:var(--paper); color:var(--ink); font:16px/1.5 system-ui,sans-serif; }}
    header {{ padding:2rem max(1rem,5vw); background:var(--navy); color:white; }}
    header p {{ max-width:70ch; }}
    main {{ padding:2rem max(1rem,5vw); display:grid; grid-template-columns:repeat(auto-fit,minmax(310px,1fr)); gap:1.5rem; }}
    .card {{ background:white; border:1px solid #c9c1b4; border-radius:12px; overflow:hidden; box-shadow:0 3px 14px #0001; }}
    img {{ display:block; width:100%; height:auto; aspect-ratio:1; object-fit:cover; }}
    .body {{ padding:1.1rem; }} h2 {{ margin:.25rem 0 1rem; color:var(--navy); }}
    .tag {{ color:var(--rust); font-weight:800; font-size:.8rem; letter-spacing:.06em; }}
    details {{ border-top:1px solid #ddd; padding:.65rem 0; }} summary {{ cursor:pointer; font-weight:650; }}
    .hash {{ overflow-wrap:anywhere; font-size:.78rem; color:#555; }} a {{ color:#005a72; }}
  </style>
</head>
<body>
  <header>
    <h1>Biblical profile-image candidates</h1>
    <p>{esc(data['global_disclosure'])}</p>
    <p><strong>{data['candidate_count']} files; {data['covered_plan_entry_count']} of 76 plan records represented. Nothing in this gallery is approved for publication.</strong></p>
  </header>
  <main>{''.join(cards)}</main>
</body>
</html>
"""
    OUTPUT.write_text(document, encoding="utf-8")
    print(f"Wrote {OUTPUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

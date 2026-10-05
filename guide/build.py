#!/usr/bin/env python3
"""Build the illustrated guide (guide/life-crm-guide.pdf) from the chapter files in guide/.

    python3 guide/build.py               # writes guide/life-crm-guide.html and .pdf
    python3 guide/build.py --html-only   # just the HTML, for a quick look in a browser

The chapters (NN-*.md) are the source: edit them, then rebuild, so the text and the PDF never
drift apart. Needs `markdown-it-py` (pip install markdown-it-py) and Google Chrome or Chromium
for the PDF. Fonts: Georgia and Lato if installed, otherwise the closest system fonts.

Markdown conventions the design picks up:
  > **You do:** ...            a "You" box
  > **Your agent does:** ...   an "Agent" box
  > **For money:** / **For health:** ...   a box labelled "For money" / "For health"
  > other blockquotes          an example / note card
  ```text fences               a "Paste this" card
  images whose alt mentions "phone"  shown at phone width
"""
from __future__ import annotations

import argparse
import html
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from markdown_it import MarkdownIt

GUIDE = Path(__file__).resolve().parent
CHROMES = ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser", "chrome")

BOXES = [  # (regex on the first bold text of a blockquote, css class, label)
    (r"^You do", "box you", "You"),
    (r"^Your agent does", "box agent", "Your agent"),
    (r"^For (money|health)", "box other", ""),
]


def chapters() -> list[tuple[str, str]]:
    """[(slug, markdown)] in file order."""
    files = sorted(GUIDE.glob("[0-9][0-9]-*.md"))
    if not files:
        sys.exit("no chapters (NN-name.md) in guide/")
    return [(f.stem, f.read_text()) for f in files]


def render(md: MarkdownIt, slug: str, text: str) -> tuple[str, str, str]:
    """One chapter as HTML. Returns (title, eyebrow, html)."""
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    body = md.render(re.sub(r"^# .+\n", "", text, count=1, flags=re.M))
    m = re.match(r"Step (\d+): (.+)", title)
    eyebrow, title = (f"Step {m.group(1)} of 8", m.group(2)) if m else ("", title)

    def box(match: re.Match) -> str:
        inner = match.group(1)
        lead = re.match(r"\s*<p><strong>([^<]+)</strong>", inner)
        for pattern, cls, label in BOXES:
            if lead and re.match(pattern, lead.group(1)):
                inner = inner.replace(f"<strong>{lead.group(1)}</strong>", "", 1).replace("<p> ", "<p>", 1)
                # "For money:" boxes are labelled with their own lead ("For money"), the rest by kind.
                tag = label or lead.group(1).rstrip(": ")
                return f'<aside class="{cls}"><span class="tag">{html.escape(tag)}</span>{inner}</aside>'
        if lead:
            return f'<aside class="box note">{inner}</aside>'
        return f'<aside class="box example"><span class="tag">Example</span>{inner}</aside>'

    body = re.sub(r"<blockquote>(.*?)</blockquote>", box, body, flags=re.S)
    # "You" + "Your agent", and the money + health boxes, sit side by side.
    one = r'<aside class="box (?:you|agent|other)">(?:(?!</aside>).)*</aside>'
    body = re.sub(rf"({one})\s*({one})", r'<div class="pair">\1\2</div>', body, flags=re.S)
    body = re.sub(r'<pre><code class="language-text">(.*?)</code></pre>',
                  r'<figure class="paste"><span class="tag">Paste this</span><pre>\1</pre></figure>', body, flags=re.S)

    def figure(match: re.Match) -> str:
        src, alt = match.group(1), match.group(2)
        cls = "shot phone" if "phone" in alt.lower() else ("diagram" if src.endswith(".svg") else "shot")
        return f'<figure class="{cls}"><img src="{src}" alt="{alt}"></figure>'

    body = re.sub(r'<p><img src="([^"]+)" alt="([^"]*)" ?/?></p>', figure, body)
    return title, eyebrow, f'<section class="chapter" id="{slug}">' + (
        f'<p class="eyebrow">{eyebrow}</p>' if eyebrow else "") + f"<h1>{html.escape(title)}</h1>{body}</section>"


def page(parts: list[tuple[str, str, str, str]]) -> str:
    toc = "".join(
        f'<li><a href="#{slug}"><span class="n">{html.escape(eyebrow.replace(" of 8", "")) or "&nbsp;"}</span>'
        f'<span class="t">{html.escape(title)}</span></a></li>' for slug, title, eyebrow, _ in parts)
    body = "".join(h for *_, h in parts)
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>life-crm · the guide</title>
<style>{CSS}</style></head>
<body>
<section class="cover">
  <div class="cover-top"><span class="mark"></span>life-crm</div>
  <h1>A personal CRM for any life project</h1>
  <p class="cover-sub">You talk, your agent builds. A plain guide to turning one spreadsheet into a private
  dashboard, a public page and a CV.</p>
  <figure class="cover-shot"><img src="../demo/img/career-roadmap.webp" alt=""></figure>
  <p class="cover-foot">github.com/jerryfane/life-crm · life-crm.jerryfane.com</p>
</section>
<section class="toc"><h1>Contents</h1><ol>{toc}</ol>
  <p class="toc-note">Maya, the medical student in this guide, is fictional. Every name, school and date is made up.</p>
</section>
{body}
</body></html>
"""


CSS = r"""
@page { size: A5; margin: 13mm 12mm 15mm; @bottom-center { content: counter(page); font: 8pt Lato, sans-serif; color: #8a9490; } }
@page cover { margin: 0; @bottom-center { content: none; } }
@page toc { @bottom-center { content: none; } }
:root { --ink: #1c2321; --muted: #5d6763; --line: #e4e0d6; --bg: #f6f4ef; --teal: #1f5f5b; --teal-soft: #e3efed;
  --indigo: #4f46e5; --indigo-soft: #ecebfd; --amber: #9a6700; --amber-soft: #fff6dc; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--ink); font: 9.1pt/1.48 Lato, "Helvetica Neue", Arial, sans-serif; }
a { color: var(--teal); text-decoration: none; }
h1 { font: 600 22pt/1.1 Georgia, "Times New Roman", serif; letter-spacing: -.01em; margin: 0 0 5mm; }
h2 { font: 600 12.5pt/1.25 Georgia, serif; margin: 6mm 0 2mm; break-after: avoid; }
p { margin: 0 0 2.6mm; } ul, ol { margin: 0 0 3mm; padding-left: 5mm; } li { margin-bottom: 1mm; }
strong { font-weight: 700; }
code { font: 8.6pt "DejaVu Sans Mono", monospace; background: #f1efe9; padding: 0 1mm; border-radius: 1mm; }

.chapter { break-before: page; }
.eyebrow { display: inline-block; font-size: 7.5pt; font-weight: 700; letter-spacing: .1em; text-transform: uppercase;
  color: var(--teal); background: var(--teal-soft); padding: .8mm 2.6mm; border-radius: 10mm; margin: 0 0 3mm; }

table { width: 100%; border-collapse: collapse; margin: 1mm 0 4mm; font-size: 8.6pt; break-inside: avoid; }
th { text-align: left; font-weight: 700; color: var(--muted); font-size: 7.4pt; letter-spacing: .05em; text-transform: uppercase;
  border-bottom: 1.4pt solid var(--ink); padding: 1.4mm 2mm 1.4mm 0; }
td { border-bottom: .6pt solid var(--line); padding: 1.6mm 2mm 1.6mm 0; vertical-align: top; }

.box { position: relative; border-radius: 3mm; padding: 3mm 3.6mm 1mm; margin: 0 0 3.5mm; break-inside: avoid; border: .8pt solid; font-size: 8.7pt; }
.pair { display: grid; grid-template-columns: 1fr 1fr; gap: 3mm; margin: 0 0 3.5mm; break-inside: avoid; }
.pair .box { margin: 0; }
.box .tag, .paste .tag { display: block; font-size: 7pt; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; margin-bottom: 1mm; }
.you { background: var(--teal-soft); border-color: #c4dcd8; } .you .tag { color: var(--teal); }
.agent { background: var(--indigo-soft); border-color: #d6d3fb; } .agent .tag { color: var(--indigo); }
.other { background: var(--amber-soft); border-color: #f1e3b8; } .other .tag { color: var(--amber); }
.example { background: #fff; border-color: var(--line); border-left: 2.4pt solid var(--teal); } .example .tag { color: var(--muted); }
.note { background: #faf9f6; border-color: var(--line); }
.box ol, .box ul { padding-left: 4.5mm; }

.paste { margin: 0 0 4mm; background: var(--ink); color: #e9efed; border-radius: 3mm; padding: 3mm 4mm; break-inside: avoid; }
.paste .tag { color: #8fd1c7; }
.paste pre { margin: 0; white-space: pre-wrap; font: 8.4pt/1.5 "DejaVu Sans Mono", monospace; }

figure { margin: 1mm 0 4.5mm; break-inside: avoid; }
.shot img { display: block; width: 100%; max-height: 64mm; object-fit: cover; object-position: top left; border-radius: 2.4mm;
  border: .6pt solid var(--line); box-shadow: 0 1.5mm 5mm rgba(28,35,33,.16); }
.phone img { width: auto; max-width: 40%; max-height: 82mm; margin: 0 auto; border-radius: 4mm; border: 1.6mm solid var(--ink); object-fit: contain; }
.diagram img { display: block; width: 100%; }

.cover { page: cover; height: 210mm; width: 148mm; background: var(--teal); color: #fff; padding: 16mm 13mm 12mm; display: flex; flex-direction: column; overflow: hidden; }
.cover-top { display: flex; align-items: center; gap: 2.5mm; font-weight: 800; font-size: 11pt; letter-spacing: .01em; }
.mark { width: 7mm; height: 7mm; border-radius: 1.8mm; background: #fff; position: relative; }
.mark::before { content: ""; position: absolute; left: 1.7mm; right: 1.7mm; top: 2mm; height: 3mm; border-top: .8mm solid var(--teal); border-bottom: .8mm solid var(--teal); }
.cover h1 { color: #fff; font-size: 30pt; line-height: 1.05; margin: 16mm 0 5mm; max-width: 11em; }
.cover-sub { color: #d5e6e3; font-size: 11pt; line-height: 1.5; max-width: 26em; }
.cover-shot { margin: auto -26mm 0 0; transform: rotate(-4deg) translateY(4mm); transform-origin: left bottom; }
.cover-shot img { width: 100%; border-radius: 3mm; box-shadow: 0 6mm 16mm rgba(0,0,0,.35); border: .6pt solid rgba(255,255,255,.4); }
.cover-foot { margin: 12mm 0 0; font-size: 8pt; color: #b7d3ce; letter-spacing: .02em; position: relative; }

.toc { page: toc; break-before: page; }
.toc ol { list-style: none; padding: 0; margin: 2mm 0 6mm; }
.toc li { border-bottom: .6pt solid var(--line); margin: 0; }
.toc a { display: flex; gap: 4mm; padding: 2.4mm 0; color: var(--ink); }
.toc .n { width: 13mm; flex: none; font-size: 7.5pt; font-weight: 700; color: var(--teal); letter-spacing: .06em; text-transform: uppercase; padding-top: .6mm; }
.toc .t { font: 600 11pt/1.3 Georgia, serif; }
.toc-note { font-size: 8.4pt; color: var(--muted); }

@media screen {
  body { background: #d9d6ce; padding: 8mm 0; }
  .cover, .toc, .chapter { width: 148mm; min-height: 210mm; margin: 0 auto 8mm; background: #fff; padding: 15mm 13mm; box-shadow: 0 2mm 8mm rgba(0,0,0,.15); }
  .cover { background: var(--teal); height: auto; }
}
"""


def find_chrome() -> str:
    for name in (os.environ.get("CHROME"), *CHROMES):
        if name and shutil.which(name):
            return shutil.which(name)
    sys.exit("Chrome or Chromium not found; set CHROME=/path/to/chrome, or use --html-only")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args()

    md = MarkdownIt("commonmark", {"html": False, "typographer": True}).enable(["table", "replacements", "smartquotes"])
    parts = []
    for slug, text in chapters():
        title, eyebrow, body = render(md, slug, text)
        parts.append((slug, title, eyebrow, body))
    out_html = GUIDE / "life-crm-guide.html"
    out_html.write_text(page(parts))
    print(f"html: {out_html}")
    if args.html_only:
        return

    out_pdf = GUIDE / "life-crm-guide.pdf"
    with tempfile.TemporaryDirectory() as profile:
        run = subprocess.run([find_chrome(), "--headless", "--disable-gpu", "--no-sandbox", f"--user-data-dir={profile}",
                              "--allow-file-access-from-files", "--no-pdf-header-footer", "--virtual-time-budget=10000",
                              f"--print-to-pdf={out_pdf}", out_html.as_uri()], capture_output=True, text=True, timeout=180)
    if run.returncode != 0 or not out_pdf.is_file():
        sys.exit(f"PDF failed:\n{run.stderr[-2000:]}")
    print(f"pdf: {out_pdf} ({out_pdf.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()

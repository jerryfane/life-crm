#!/usr/bin/env python3
"""Build the short illustrated guide (guide/life-crm-guide.pdf) from the chapter files in guide/.

    python3 guide/build.py               # writes guide/life-crm-guide.html and .pdf
    python3 guide/build.py --html-only   # just the HTML, for a quick look in a browser

Layout: a cover with the prompt to paste, then one A5 page per chapter (NN-*.md). The chapters
are the source: edit them, then rebuild, so the text and the PDF never drift apart. Keep each
chapter to one page; the build fails if the PDF grows past 1 + number of chapters pages.

Needs `markdown-it-py` (pip install markdown-it-py), Google Chrome or Chromium, and `pdfinfo`
(poppler) for the page check. Fonts: Georgia and Lato if installed, else close system fonts.

Markdown conventions: `> **Label:** text` becomes a flat tinted note tagged "Label"; a two-column
table with an empty header row becomes a list of definitions; `## 3 Choose` followed by
`**You:**`, `**Your agent:**`, `**Expect:**` paragraphs becomes a numbered step block.
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
PROMPT = ("I want a personal CRM for a project in my life. Download https://github.com/jerryfane/life-crm "
          "(git clone, or the ZIP), read skill/SKILL.md, and follow it step by step with me. I am not a "
          "developer: ask me one thing at a time, show me options to choose from, and explain anything I "
          "need to click. Start with step 1.")


def chapters() -> list[Path]:
    files = sorted(GUIDE.glob("[0-9][0-9]-*.md"))
    if not files:
        sys.exit("no chapters (NN-name.md) in guide/")
    return files


def render(md: MarkdownIt, text: str) -> str:
    title = re.search(r"^# (.+)$", text, re.M).group(1).strip()
    body = md.render(re.sub(r"^# .+\n", "", text, count=1, flags=re.M))

    def card(m: re.Match) -> str:
        inner = m.group(1)
        lead = re.match(r"\s*<p><strong>([^<]+?):?</strong>:?\s*", inner)
        if not lead:
            return f'<aside class="card">{inner}</aside>'
        label, rest = lead.group(1).rstrip(":"), inner[lead.end():]
        # "> **You:** ..." / "> **Assistant:** ..." are a chat: message bubbles instead of notes.
        if label in ("You", "Assistant"):
            return f'<div class="bubble {"me" if label == "You" else "them"}"><p>{rest}</div>'
        return f'<aside class="card"><span class="tag">{html.escape(label)}</span><p>{rest}</aside>'

    body = re.sub(r"<blockquote>(.*?)</blockquote>", card, body, flags=re.S)
    body = re.sub(r"<table>\s*<thead>\s*<tr>\s*<th></th>\s*<th></th>\s*</tr>\s*</thead>", '<table class="defs">', body)
    # "## 3 Choose" + "**You:** ..." paragraphs -> a numbered step block with labelled lines.
    body = re.sub(r"<p><strong>(You|Your agent|Expect):</strong>\s*",
                  lambda m: f'<p class="line"><span class="who">{"Agent" if m[1] == "Your agent" else m[1]}</span>', body)
    body = re.sub(r"<h2>(\d+) ([^<]+)</h2>((?:(?!<h2>|<aside).)*)",
                  r'<div class="step"><span class="num">\1</span><div><h2>\2</h2>\3</div></div>', body, flags=re.S)
    body = re.sub(r'<p><img src="([^"]+)" alt="([^"]*)" ?/?></p>', r'<figure class="diagram"><img src="\1" alt="\2"></figure>', body)
    return f'<section class="page"><h1>{html.escape(title)}</h1>{body}</section>'


def page(body: str) -> str:
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>life-crm · the guide</title>
<style>{CSS}</style></head>
<body>
<section class="cover">
  <div class="brand"><span class="mark"></span>life-crm</div>
  <h1>A personal CRM for any life project</h1>
  <p class="sub">Paste one prompt into your AI agent. It interviews you, then builds a private dashboard,
  a public page and a CV from one spreadsheet you own.</p>
  <figure class="paste"><span class="tag">Paste this into your agent</span><p>{html.escape(PROMPT)}</p></figure>
  <figure class="shot"><img src="../demo/img/career-roadmap.webp" alt=""></figure>
  <p class="foot">life-crm.jerryfane.com · github.com/jerryfane/life-crm</p>
</section>
{body}
</body></html>
"""


CSS = r"""
@page { size: A5; margin: 14mm 13mm 14mm; @bottom-center { content: counter(page) " / " counter(pages); font: 7.5pt Lato, sans-serif; color: #8a9490; } }
@page cover { margin: 0; @bottom-center { content: none; } }
:root { --ink: #1c2321; --muted: #5d6763; --line: #e4e0d6; --teal: #1f5f5b; --teal-soft: #e3efed; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; color: var(--ink); font: 9.2pt/1.5 Lato, "Helvetica Neue", Arial, sans-serif; }
h1 { font: 600 21pt/1.1 Georgia, "Times New Roman", serif; letter-spacing: -.01em; margin: 0 0 3mm; }
p { margin: 0 0 3mm; }
strong { font-weight: 700; }

.page { break-before: page; }
.page > p:first-of-type { color: var(--muted); font-size: 10pt; }

table { width: 100%; border-collapse: collapse; margin: 1mm 0 4mm; font-size: 8.4pt; break-inside: avoid; }
th { text-align: left; font-weight: 800; color: var(--muted); font-size: 6.8pt; letter-spacing: .08em; text-transform: uppercase;
  border-bottom: 1.3pt solid var(--ink); padding: 1.2mm 2mm 1.2mm 0; }
td { border-bottom: .6pt solid var(--line); padding: 1.7mm 2.5mm 1.7mm 0; vertical-align: top; }
td:first-child { white-space: nowrap; }
table.defs td:first-child { width: 30%; color: var(--teal); white-space: normal; }
/* Numbered setup steps: number, title, then You / Your agent / Expect lines. */
.step { display: grid; grid-template-columns: 7mm 1fr; gap: 3mm; padding: 2.3mm 0; border-bottom: .6pt solid var(--line); break-inside: avoid; }
.step:last-of-type { border-bottom: 0; }
.step .num { width: 7mm; height: 7mm; border-radius: 50%; background: var(--teal); color: #fff; font: 700 9pt/7mm Lato, sans-serif; text-align: center; }
.step h2 { font: 600 11.5pt/1.2 Georgia, serif; margin: .7mm 0 1.2mm; }
.line { display: grid; grid-template-columns: 17mm 1fr; gap: 2mm; margin: 0 0 .8mm; font-size: 8.3pt; line-height: 1.4; }
.line .who { font-size: 6.6pt; font-weight: 800; letter-spacing: .1em; text-transform: uppercase; color: var(--teal); padding-top: .5mm; }
.line:last-child { color: var(--muted); margin-bottom: 0; }

/* Section headings on single-step pages; .page > .line lines sit directly on the page. */
.page > h2 { font: 600 12pt/1.2 Georgia, serif; margin: 5mm 0 2mm; }
.page > ul { margin: 0 0 3mm; padding-left: 4.5mm; } .page > ul li { margin-bottom: .8mm; }
.page > .line { margin-bottom: 1.6mm; }

/* Chat example: messages as bubbles, yours on the right. */
.bubble { width: fit-content; max-width: 80%; border-radius: 4mm; padding: 2.4mm 3.4mm; margin: 0 0 2mm; font-size: 8.6pt; line-height: 1.45; break-inside: avoid; }
.bubble p { margin: 0; }
.bubble.me { margin-left: auto; background: var(--teal); color: #fff; border-bottom-right-radius: 1mm; }
.bubble.them { background: #f0efea; border-bottom-left-radius: 1mm; }

/* Flat note: a soft tinted panel, no outline or side stripe. */
.card { background: #eef4f2; border-radius: 2mm; padding: 2.8mm 3.6mm .6mm; margin: 0 0 3mm; font-size: 8.6pt; break-inside: avoid; }
.card .tag, .paste .tag { display: block; font-size: 6.8pt; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; color: var(--teal); margin-bottom: .6mm; }
.diagram { margin: 2mm 0 4mm; } .diagram img { display: block; width: 100%; }

.cover { page: cover; height: 210mm; width: 148mm; background: var(--teal); color: #fff; padding: 14mm 13mm 11mm; display: flex; flex-direction: column; overflow: hidden; }
.brand { display: flex; align-items: center; gap: 2.5mm; font-weight: 800; font-size: 11pt; }
.mark { width: 7mm; height: 7mm; border-radius: 1.8mm; background: #fff; position: relative; }
.mark::before { content: ""; position: absolute; left: 1.7mm; right: 1.7mm; top: 2mm; height: 3mm; border-top: .8mm solid var(--teal); border-bottom: .8mm solid var(--teal); }
.cover h1 { color: #fff; font-size: 27pt; line-height: 1.05; margin: 11mm 0 4mm; max-width: 11em; }
.sub { color: #d5e6e3; font-size: 10.5pt; line-height: 1.5; max-width: 27em; }
.paste { margin: 2mm 0 0; background: rgba(0,0,0,.22); border: .6pt solid rgba(255,255,255,.25); border-radius: 3mm; padding: 3mm 4mm; }
.paste .tag { color: #9fd6cd; }
.paste p { margin: 0; font: 8.3pt/1.5 "DejaVu Sans Mono", monospace; color: #f1f6f5; }
.shot { margin: auto -24mm 0 0; transform: rotate(-3deg) translateY(3mm); transform-origin: left bottom; }
.shot img { width: 100%; border-radius: 3mm; box-shadow: 0 6mm 16mm rgba(0,0,0,.35); }
.foot { margin: 9mm 0 0; font-size: 7.8pt; color: #b7d3ce; position: relative; }

@media screen {
  body { background: #d9d6ce; padding: 8mm 0; }
  .cover, .page { width: 148mm; min-height: 210mm; margin: 0 auto 8mm; background: #fff; padding: 14mm 13mm; box-shadow: 0 2mm 8mm rgba(0,0,0,.15); }
  .cover { background: var(--teal); height: auto; }
}
"""


def find(names) -> str:
    for name in names:
        if name and shutil.which(name):
            return shutil.which(name)
    return ""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html-only", action="store_true")
    args = ap.parse_args()

    md = MarkdownIt("commonmark", {"html": False, "typographer": True}).enable(["table", "replacements", "smartquotes"])
    files = chapters()
    out_html = GUIDE / "life-crm-guide.html"
    out_html.write_text(page("".join(render(md, f.read_text()) for f in files)))
    print(f"html: {out_html}")
    if args.html_only:
        return

    chrome = find((os.environ.get("CHROME"), *CHROMES))
    if not chrome:
        sys.exit("Chrome or Chromium not found; set CHROME=/path/to/chrome, or use --html-only")
    out_pdf = GUIDE / "life-crm-guide.pdf"
    with tempfile.TemporaryDirectory() as profile:
        run = subprocess.run([chrome, "--headless", "--disable-gpu", "--no-sandbox", f"--user-data-dir={profile}",
                              "--allow-file-access-from-files", "--no-pdf-header-footer", "--virtual-time-budget=10000",
                              f"--print-to-pdf={out_pdf}", out_html.as_uri()], capture_output=True, text=True, timeout=180)
    if run.returncode != 0 or not out_pdf.is_file():
        sys.exit(f"PDF failed:\n{run.stderr[-2000:]}")
    pages = re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(out_pdf)], capture_output=True, text=True).stdout)
    want = 1 + len(files)
    if pages and int(pages.group(1)) > want:
        sys.exit(f"{out_pdf.name} has {pages.group(1)} pages, expected {want}: a chapter spills onto a second page; shorten it")
    print(f"pdf: {out_pdf} ({out_pdf.stat().st_size // 1024} KB, {pages.group(1) if pages else '?'} pages)")


if __name__ == "__main__":
    main()

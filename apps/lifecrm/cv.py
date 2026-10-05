"""Spreadsheet (Profile + Entries) -> CV as LaTeX, compiled to PDF when latexmk is installed.

Uses the same Profile and Entries as the public site, plus Profile `phone`. build.py makes two
copies: cv.pdf with the phone (for the person) and cv-public.pdf without it (offered on the site).
"""
from __future__ import annotations

import re
import shutil
import subprocess
from pathlib import Path

from .site import ordered_sections, profile_links, read_entries, read_profile

_TEX = {"\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$", "#": r"\#", "_": r"\_",
        "{": r"\{", "}": r"\}", "~": r"\textasciitilde{}", "^": r"\textasciicircum{}"}


def tex(s: str) -> str:
    return "".join(_TEX.get(ch, ch) for ch in s or "").replace(" – ", " -- ").replace("–", "--")


def _bullet(line: str) -> str:
    label, sep, rest = line.partition(":")
    if sep and 0 < len(label) <= 40 and rest.strip():
        return rf"\textbf{{{tex(label)}:}} {tex(rest.strip())}"
    return tex(line)


def _entry(x: dict) -> str:
    when = " -- ".join(tex(v) for v in (x["start"], x["end"]) if v)
    where = tex(", ".join(v for v in (x["organization"], x["location"]) if v))
    parts = [rf"\entry{{{tex(x['title'])}}}{{{when}}}{{{where}}}"]
    if x["summary"]:
        parts.append(rf"{{\small {tex(x['summary'])}\par}}")
    lines = [ln.strip() for ln in x["highlights"].splitlines() if ln.strip()]
    if lines:
        parts.append("{\\small\n\\begin{itemize}\n" + "\n".join(rf"  \item {_bullet(ln)}" for ln in lines) + "\n\\end{itemize}}")
    # minipage keeps one entry on one page
    return "\\noindent\\begin{minipage}{\\linewidth}\n" + "\n".join(parts) + "\n\\end{minipage}\\par"


def render(wb, template: Path, warnings: list[str], with_phone: bool = True) -> str:
    p = read_profile(wb)
    sections = ordered_sections(p, read_entries(wb, warnings))
    contact = [tex(p.get("phone", "")) if with_phone else "", tex(p.get("email", ""))]
    for _, url in profile_links(p):
        contact.append(rf"\href{{{url}}}{{{tex(re.sub(r'^https?://(www\.)?', '', url).rstrip('/'))}}}")
    if p.get("site_url"):
        contact.append(rf"\href{{{p['site_url']}}}{{{tex(re.sub(r'^https?://', '', p['site_url']).rstrip('/'))}}}")
    body = "\n".join(rf"\section{{{tex(title)}}}" + "\n" + "\n\\gap\n".join(_entry(x) for x in items) for title, items in sections)
    return (template.read_text()
            .replace("<<NAME>>", tex(p.get("name", "")))
            .replace("<<HEADLINE>>", tex(p.get("headline", "")))
            .replace("<<CONTACT>>", r" \textperiodcentered{} ".join(c for c in contact if c))
            .replace("<<SECTIONS>>", body))


def build(wb, template: Path, out_dir: Path, warnings: list[str], with_phone: bool = True, stem: str = "cv") -> Path | None:
    """Write out_dir/<stem>.tex and compile <stem>.pdf. Returns the PDF path, or None without LaTeX."""
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{stem}.tex").write_text(render(wb, template, warnings, with_phone))
    if not shutil.which("latexmk"):
        warnings.append(f"CV: latexmk not installed; wrote {stem}.tex but no PDF")
        return None
    run = subprocess.run(["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-silent", f"{stem}.tex"],
                         cwd=out_dir, capture_output=True, text=True)
    if run.returncode != 0:
        warnings.append(f"CV: LaTeX failed; see {out_dir / (stem + '.log')}")
        return None
    return out_dir / f"{stem}.pdf"

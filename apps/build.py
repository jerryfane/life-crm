#!/usr/bin/env python3
"""Build your CRM from one spreadsheet file.

    python3 apps/build.py examples/career/crm.xlsx --out build/career

Writes:
    <out>/dashboard/   private dashboard (roadmap, timelines, collection pages)
    <out>/site/        public one-page site (only if the spreadsheet has Profile + Entries)
    <out>/cv/cv.pdf    CV (only with --cv, needs LaTeX)
    <out>/warnings.txt rows that need fixing (also shown on the dashboard)

Options:
    --only dashboard,site,cv   build a subset
    --cv                       also build the CV (and offer it as a download on the site)
    --documents FILE.json      list of Drive files for the Documents page (written by pull.py)

Requirements: Python 3.10+, `pip install openpyxl pillow`; LaTeX (latexmk) only for the CV.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path

from openpyxl import load_workbook

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from lifecrm import cv, dashboard, site  # noqa: E402
from lifecrm.sheet import key_values, tab  # noqa: E402

NO = {"no", "n", "false", "0"}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<meta name="robots" content="noindex, nofollow">
<title>{title}</title>
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="style.css?v={css}">
</head>
<body>
<div id="app"></div>
<script id="data" type="application/json">{data}</script>
<script src="app.js?v={js}"></script>
</body>
</html>
"""


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:10]


def build_dashboard(wb, out: Path, documents: dict | None, extra_warnings: list[str]) -> dict:
    """extra_warnings: site/CV problems, shown on the dashboard too so the person editing the sheet sees them."""
    data = dashboard.convert(wb)
    data["warnings"] += extra_warnings
    if documents:
        data["documents"] = documents
    static = HERE / "dashboard"
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    for f in ("app.js", "style.css"):
        shutil.copy2(static / f, out / f)
    (out / "favicon.svg").write_text(site.favicon(data["name"] or data["title"]))
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /\n")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    from html import escape
    (out / "index.html").write_text(PAGE.format(title=escape(data["title"]), css=digest(static / "style.css"), js=digest(static / "app.js"), data=payload))
    return data


def main() -> int:
    ap = argparse.ArgumentParser(description="Build the life-crm dashboard, site and CV from a spreadsheet.")
    ap.add_argument("sheet", type=Path, help="the spreadsheet (.xlsx)")
    ap.add_argument("--out", type=Path, default=Path("build"))
    ap.add_argument("--only", default="dashboard,site", help="comma list of dashboard, site, cv")
    ap.add_argument("--cv", action="store_true", help="also build the CV")
    ap.add_argument("--documents", type=Path, help="JSON list of Drive files for the Documents page")
    args = ap.parse_args()

    parts = {p.strip() for p in args.only.split(",") if p.strip()} | ({"cv"} if args.cv else set())
    wb = load_workbook(args.sheet, data_only=True)
    documents = json.loads(args.documents.read_text()) if args.documents and args.documents.is_file() else None
    warnings: list[str] = []
    built = []

    cv_pdf = public_cv = None
    if "cv" in parts:
        template = HERE / "cv" / "template.tex"
        cv_pdf = cv.build(wb, template, args.out / "cv", warnings)
        built.append(f"cv: {cv_pdf or args.out / 'cv' / 'cv.tex'}")
        profile = key_values(tab(wb, "Profile")) if tab(wb, "Profile") else {}
        # The site offers a CV download; that copy never carries the phone number.
        if "site" in parts and profile.get("cv_on_site", "yes").lower() not in NO:
            public_cv = cv.build(wb, template, args.out / "cv", warnings, with_phone=False, stem="cv-public") \
                if profile.get("phone") else cv_pdf
    if "site" in parts:
        if tab(wb, "Profile") and tab(wb, "Entries"):
            site.build(wb, args.sheet.parent, args.out / "site", HERE / "site", public_cv, warnings)
            built.append(f"site: {args.out / 'site'}")
        else:
            built.append("site: skipped (no Profile + Entries tabs)")
    if "dashboard" in parts:
        data = build_dashboard(wb, args.out / "dashboard", documents, warnings)
        warnings = data["warnings"]
        built.append(f"dashboard: {args.out / 'dashboard'} ({len(data['timelines'])} timelines, {len(data['steps'])} steps, {len(data['collections'])} pages)")

    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "warnings.txt").write_text("".join(w + "\n" for w in warnings))
    for line in built:
        print(line)
    for w in warnings:
        print("warning:", w, file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

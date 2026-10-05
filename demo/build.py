#!/usr/bin/env python3
"""Build the public demo (life-crm.jerryfane.com) from the example spreadsheets.

    python3 demo/build.py                                  # -> build/demo/
    wrangler deploy --config demo/wrangler.json            # one Worker serving build/demo/

Layout:
    /                    landing page (demo/index.html, demo/img/)
    /demo/site/          Maya's public page, with her CV
    /demo/dashboard/     Maya's dashboard (public here on purpose: every name and fact is made up)
    /demo/finance/       money example
    /demo/health/        health example
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLES = ROOT / "examples"


def build(sheet: Path, out: Path, *extra: str) -> None:
    run = subprocess.run([sys.executable, str(ROOT / "apps" / "build.py"), str(sheet), "--out", str(out), *extra],
                         capture_output=True, text=True)
    if run.returncode != 0 or run.stderr.strip():
        # The demo must build cleanly: a warning here is a bug in the example sheet.
        sys.exit(f"{sheet}: {run.stderr.strip() or 'build failed'}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=ROOT / "build" / "demo")
    args = ap.parse_args()
    out, work = args.out, args.out.parent / "demo-work"
    shutil.rmtree(out, ignore_errors=True)
    shutil.rmtree(work, ignore_errors=True)

    build(EXAMPLES / "career" / "crm.xlsx", work / "career", "--cv")
    build(EXAMPLES / "finance" / "crm.xlsx", work / "finance")
    build(EXAMPLES / "health" / "crm.xlsx", work / "health")

    shutil.copytree(ROOT / "demo" / "img", out / "img")
    shutil.copy2(ROOT / "demo" / "index.html", out / "index.html")
    shutil.copy2(ROOT / "demo" / "404.html", out / "404.html")
    shutil.copytree(work / "career" / "site", out / "demo" / "site")
    shutil.copytree(work / "career" / "dashboard", out / "demo" / "dashboard")
    shutil.copytree(work / "finance" / "dashboard", out / "demo" / "finance")
    shutil.copytree(work / "health" / "dashboard", out / "demo" / "health")
    for sub in ("site", "dashboard", "finance", "health"):
        # One robots.txt and one 404 page for the whole domain, at the root.
        (out / "demo" / sub / "robots.txt").unlink(missing_ok=True)
        (out / "demo" / sub / "404.html").unlink(missing_ok=True)
    # Maya is fictional: keep her pages out of search results; the landing page stays indexable.
    (out / "robots.txt").write_text("User-agent: *\nDisallow: /demo/\n")
    shutil.rmtree(work)
    print(f"demo: {out}")


if __name__ == "__main__":
    main()

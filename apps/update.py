#!/usr/bin/env python3
"""Pull from Drive, build, and deploy, in one command, using a small settings file.

    python3 apps/update.py crm.json

crm.json (written by the agent during setup):
    {
      "folder": "DRIVE_FOLDER_ID",
      "sheet": "SHEET_ID",
      "cv": true,
      "site": "maya-site=maya.example.com",
      "dashboard": "maya-crm=maya-crm.YOURNAME.workers.dev"
    }

"site" and "dashboard" are optional (leave one out to skip it); see deploy.py for the format.
"dashboard" must include its address, so its login can be checked on every run.
Files go to data/ and build/ next to crm.json. Safe to run as often as you like.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

APPS = Path(__file__).resolve().parent


def run(*args: str) -> None:
    if subprocess.run([sys.executable, *args]).returncode != 0:
        sys.exit(f"stopped: {Path(args[0]).name} failed")


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    cfg_path = Path(sys.argv[1]).resolve()
    cfg = json.loads(cfg_path.read_text())
    missing = [k for k in ("folder", "sheet") if not cfg.get(k)]
    if missing:
        sys.exit(f"{cfg_path.name}: missing {', '.join(missing)}")
    if cfg.get("dashboard") and "=" not in cfg["dashboard"]:
        # Without an address deploy.py would replace the live dashboard with the locked page.
        sys.exit(f'{cfg_path.name}: "dashboard" needs NAME=ADDRESS, e.g. "maya-crm=maya-crm.YOURNAME.workers.dev"')
    data, build = cfg_path.parent / "data", cfg_path.parent / "build"

    run(str(APPS / "pull.py"), "--folder", cfg["folder"], "--sheet", cfg["sheet"], "--out", str(data))
    run(str(APPS / "build.py"), str(data / "crm.xlsx"), "--out", str(build),
        "--documents", str(data / "documents.json"), *(["--cv"] if cfg.get("cv") else []))
    targets = [f"--{k}={cfg[k]}" for k in ("site", "dashboard") if cfg.get(k)]
    if targets:
        run(str(APPS / "deploy.py"), str(build), *targets)


if __name__ == "__main__":
    main()

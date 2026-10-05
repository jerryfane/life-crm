#!/usr/bin/env python3
"""Fetch the spreadsheet (and photo, and file list) from Google Drive, ready for build.py.

    python3 apps/pull.py --folder FOLDER_ID --sheet SHEET_ID --out data/

Writes:
  data/crm.xlsx         the spreadsheet, exported from Google Sheets
  data/<photo>          the Profile tab's photo file, if a file with that name is in the folder
  data/documents.json   the folder's files, for the dashboard's Documents page

Then: python3 apps/build.py data/crm.xlsx --out build --documents data/documents.json

Needs drivekey (https://github.com/jerryfane/drivekey), logged in to the Drive account that
owns the folder. Drive is only read, never changed.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from openpyxl import load_workbook

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lifecrm.sheet import key_values, tab  # noqa: E402

DRIVEKEY = os.environ.get("DRIVEKEY", "drivekey")
KINDS = {
    "application/vnd.google-apps.folder": "folder",
    "application/vnd.google-apps.spreadsheet": "sheet",
    "application/vnd.google-apps.document": "doc",
    "application/pdf": "pdf",
}


def dk(*args: str) -> dict:
    """Run drivekey and return its JSON output; exit with its error message on failure."""
    p = subprocess.run([DRIVEKEY, *args], capture_output=True, text=True)
    if p.returncode != 0:
        try:
            err = json.loads(p.stderr)["error"]
            msg = f"{err.get('code')}: {err.get('message')}" + (f"\n  hint: {err['hint']}" if err.get("hint") else "")
        except (ValueError, KeyError, TypeError):
            msg = (p.stderr or p.stdout).strip()[-500:]
        sys.exit(f"drivekey {args[0]} failed: {msg}")
    return json.loads(p.stdout) if p.stdout.strip() else {}


def ls(folder: str) -> list[dict]:
    out = dk("ls", folder)
    if not isinstance(out, dict) or not isinstance(out.get("files"), list):
        sys.exit(f"drivekey ls {folder}: unexpected output (no 'files' list); is drivekey up to date?")
    return out["files"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--folder", required=True, help="Drive folder id (the part after /folders/ in its link)")
    ap.add_argument("--sheet", required=True, help="spreadsheet id (the part after /d/ in its link)")
    ap.add_argument("--out", type=Path, default=Path("data"))
    args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    xlsx = args.out / "crm.xlsx"
    dk("get", args.sheet, "--export", "xlsx", "--out", str(xlsx), "--force")
    print(f"sheet: {xlsx}")

    files = ls(args.folder)

    ws = tab(load_workbook(xlsx, read_only=True), "Profile")
    photo = key_values(ws).get("photo", "").strip("/") if ws else ""
    if photo:
        # "photo.jpg" or a path inside the folder such as "Website/photo.jpg".
        parent, found = args.folder, []
        for i, part in enumerate(photo.split("/")):
            found = [f for f in (files if i == 0 else ls(parent)) if f["name"] == part]
            if len(found) != 1:
                break
            parent = found[0]["id"]
        if len(found) == 1:
            dest = args.out / Path(photo).name
            dk("get", found[0]["id"], "--out", str(dest), "--force")
            print(f"photo: {dest}")
        else:
            # Missing, or several items with that name: picking one could publish the wrong picture.
            print(f"photo: '{part}' (from '{photo}') is in the folder {len(found)} times; expected once", file=sys.stderr)

    # The spreadsheet itself is not a document: the dashboard links to it separately (Settings sheet_url).
    docs = [f for f in files if f["id"] != args.sheet]
    documents = {
        "root_url": f"https://drive.google.com/drive/folders/{args.folder}",
        "items": sorted(({
            "name": f["name"], "url": f.get("webViewLink", ""),
            "kind": KINDS.get(f["mimeType"], "file"), "modified": f.get("modifiedTime", "")[:10],
        } for f in docs), key=lambda x: (x["kind"] != "folder", x["name"].lower())),
    }
    (args.out / "documents.json").write_text(json.dumps(documents, indent=1))
    print(f"documents: {args.out / 'documents.json'} ({len(docs)} files)")


if __name__ == "__main__":
    main()

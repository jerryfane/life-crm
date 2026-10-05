#!/usr/bin/env python3
"""Build several dashboard variants and one page to click through them side by side.

    python3 skill/tools/proposals.py proposals.json --out work/proposals
    then open work/proposals/index.html (or serve the folder) and send the person the link.

proposals.json:
    {
      "title": "Three ways to set up your dashboard",
      "intro": "Same data, three layouts. Click around in each, then tell me which feels right.",
      "options": [
        {"label": "A · One timeline per goal", "about": "Every goal is a lane ...", "sheet": "a.json"},
        {"label": "B · Grouped by area", "about": "...", "sheet": "b.json", "part": "site"}
      ]
    }

Each "sheet" is a spreadsheet in sheetjson.py's JSON form (or an .xlsx), relative to
proposals.json. "part" is "dashboard" (default) or "site". Every option is a real build, so what
the person clicks is what they will get.
"""
from __future__ import annotations

import argparse
import html
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILD = HERE.parent.parent / "apps" / "build.py"
sys.path.insert(0, str(HERE))
from sheetjson import load  # noqa: E402

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{ margin: 0; font: 15px/1.5 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif; color: #1c2321; background: #f6f4ef; }}
  header {{ padding: 18px 22px 0; }}
  h1 {{ font: 600 24px/1.2 Georgia, serif; margin: 0 0 4px; }}
  header p {{ margin: 0 0 14px; color: #5d6763; max-width: 60em; }}
  nav {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 0 22px 12px; }}
  nav button {{ font: inherit; font-weight: 650; border: 1px solid #d9d4c7; background: #fff; border-radius: 10px; padding: 8px 14px; cursor: pointer; }}
  nav button[aria-pressed="true"] {{ background: #1f5f5b; border-color: #1f5f5b; color: #fff; }}
  .about {{ margin: 0 22px 12px; padding: 10px 14px; background: #fff; border: 1px solid #e4e0d6; border-radius: 10px; }}
  .about a {{ color: #1f5f5b; font-weight: 600; margin-left: 6px; }}
  iframe {{ display: block; width: calc(100% - 44px); margin: 0 22px 22px; height: calc(100vh - 210px); min-height: 520px;
    border: 1px solid #e4e0d6; border-radius: 12px; background: #fff; }}
  @media (max-width: 640px) {{ header, nav {{ padding-left: 12px; padding-right: 12px; }} .about {{ margin: 0 12px 10px; }}
    iframe {{ width: calc(100% - 24px); margin: 0 12px 12px; height: 75vh; }} }}
</style></head>
<body>
<header><h1>{title}</h1><p>{intro}</p></header>
<nav>{buttons}</nav>
<div class="about" id="about"></div>
<iframe id="view" title="Proposal preview"></iframe>
<script>
const OPTIONS = {options};
const show = (i) => {{
  document.querySelectorAll("nav button").forEach((b, j) => b.setAttribute("aria-pressed", String(i === j)));
  const o = OPTIONS[i];
  document.getElementById("view").src = o.href;
  const about = document.getElementById("about");
  about.textContent = o.about;
  const open = Object.assign(document.createElement("a"), {{ href: o.href, target: "_blank", textContent: "Open full screen ↗" }});
  about.append(" ", open);
  history.replaceState(null, "", "#" + (i + 1));
}};
document.querySelectorAll("nav button").forEach((b, i) => b.addEventListener("click", () => show(i)));
show(Math.max(0, Math.min(OPTIONS.length - 1, (parseInt(location.hash.slice(1), 10) || 1) - 1)));
</script>
</body></html>
"""


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()
    spec = json.loads(args.spec.read_text())
    base = args.spec.resolve().parent
    if not spec.get("options"):
        sys.exit("proposals.json has no options")

    options = []
    for n, o in enumerate(spec["options"], 1):
        part = o.get("part", "dashboard")
        if part not in ("dashboard", "site"):
            sys.exit(f"option {n}: part must be dashboard or site")
        sheet = base / o["sheet"]
        work = args.out / f"option-{n}"
        if sheet.suffix == ".json":
            xlsx = work / "crm.xlsx"
            load(json.loads(sheet.read_text()), xlsx)
            # A photo named in Profile is looked for next to the spreadsheet.
            for img in base.glob("*.jpg"):
                (work / img.name).write_bytes(img.read_bytes())
        else:
            xlsx = sheet
        run = subprocess.run([sys.executable, str(BUILD), str(xlsx), "--out", str(work), "--only", part],
                             capture_output=True, text=True)
        if run.returncode != 0:
            sys.exit(f"option {n} ({o['label']}): build failed\n{run.stderr}")
        if run.stderr.strip():
            print(f"option {n} ({o['label']}):\n{run.stderr.strip()}", file=sys.stderr)
        options.append({"href": f"option-{n}/{part}/index.html", "about": o.get("about", "")})

    buttons = "".join(f'<button type="button">{html.escape(o["label"])}</button>' for o in spec["options"])
    page = PAGE.format(title=html.escape(spec.get("title", "Proposals")), intro=html.escape(spec.get("intro", "")),
                       buttons=buttons, options=json.dumps(options).replace("</", "<\\/"))
    (args.out / "index.html").write_text(page)
    print(f"proposals: {args.out / 'index.html'} ({len(options)} options)")


if __name__ == "__main__":
    main()

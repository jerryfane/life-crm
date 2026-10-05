#!/usr/bin/env python3
"""Put the built websites online as Cloudflare Workers (static files, free plan).

    python3 apps/deploy.py build --site maya-site
    python3 apps/deploy.py build --site maya-site=maya.example.com --dashboard maya-crm=crm.maya.example.com
    python3 apps/deploy.py build --dashboard maya-crm=maya-crm.YOURNAME.workers.dev

Each option is WORKER_NAME or WORKER_NAME=ADDRESS. ADDRESS is a domain in your Cloudflare account
or the Worker's free workers.dev address. Without "=ADDRESS" the Worker gets a workers.dev
address, which wrangler prints.

Uses `wrangler` (npm install -g wrangler), logged in with `wrangler login` or the
CLOUDFLARE_API_TOKEN environment variable.

The dashboard is private. Before uploading it, this script opens its address and checks that a
Cloudflare Access login page answers. If not (or no address was given), it uploads only a
"locked" placeholder page with no data and stops, so you can turn on Access first:
    Cloudflare dashboard > Workers & Pages > WORKER_NAME > Access > Protect this Worker behind Access
Then run it again with WORKER_NAME=ADDRESS.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from datetime import date
from pathlib import Path

LOCKED = """<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex"><title>Private</title>
<body style="font:16px system-ui;display:grid;place-items:center;min-height:90vh;color:#333">
<p>This dashboard is private. It is waiting for its login page to be turned on.</p></body>
"""


def config(name: str, folder: Path, address: str) -> dict:
    on_workers_dev = not address or address.endswith(".workers.dev")
    cfg = {
        "name": name,
        "compatibility_date": date.today().isoformat(),
        "assets": {"directory": str(folder.resolve()), "not_found_handling": "404-page"},
        "workers_dev": on_workers_dev,
        "preview_urls": False,
    }
    if not on_workers_dev:
        cfg["routes"] = [{"pattern": address, "custom_domain": True}]
    return cfg


def wrangler_deploy(name: str, folder: Path, address: str) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "wrangler.json"
        path.write_text(json.dumps(config(name, folder, address), indent=2))
        if subprocess.run(["wrangler", "deploy", "--config", str(path)]).returncode != 0:
            sys.exit(f"wrangler deploy failed for Worker '{name}'")


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def behind_login(address: str) -> bool:
    """True when the address answers with a redirect to a Cloudflare Access login page."""
    # Cloudflare answers Python's default User-Agent with a bot-block 403, so name ourselves.
    req = urllib.request.Request(f"https://{address}/", headers={"User-Agent": "life-crm-deploy/1 (+https://github.com/jerryfane/life-crm)"})
    try:
        urllib.request.build_opener(NoRedirect).open(req, timeout=15)
        return False  # a page was served without a login
    except urllib.error.HTTPError as e:
        location = e.headers.get("Location", "")
        return e.code in (301, 302, 303, 307) and ".cloudflareaccess.com/" in location
    except (urllib.error.URLError, TimeoutError):
        return False  # not reachable yet (new address): treat as unprotected


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", type=Path, help="the --out folder of build.py")
    ap.add_argument("--site", metavar="NAME[=ADDRESS]", help="public site")
    ap.add_argument("--dashboard", metavar="NAME[=ADDRESS]", help="private dashboard")
    args = ap.parse_args()
    if not (args.site or args.dashboard):
        ap.error("nothing to deploy: give --site and/or --dashboard")
    for part in (["site"] if args.site else []) + (["dashboard"] if args.dashboard else []):
        if not (args.build / part / "index.html").is_file():
            sys.exit(f"{args.build / part} has no index.html; run build.py first")

    if args.site:
        name, _, address = args.site.partition("=")
        print(f"site: deploying Worker '{name}'")
        wrangler_deploy(name, args.build / "site", address)

    if args.dashboard:
        name, _, address = args.dashboard.partition("=")
        if address and behind_login(address):
            print(f"dashboard: {address} asks for a login; deploying Worker '{name}'")
            wrangler_deploy(name, args.build / "dashboard", address)
            return
        where = address or "its workers.dev address"
        print(f"dashboard: {where} does not ask for a login yet; uploading a locked placeholder only (no data)")
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "index.html").write_text(LOCKED)
            wrangler_deploy(name, Path(tmp), address)
        again = "this command again" if address else \
            f"again with --dashboard {name}=ADDRESS, using the workers.dev address printed above"
        sys.exit(f"Next: Cloudflare dashboard > Workers & Pages > {name} > Settings > Access > Protect this Worker behind Access\n"
                 f"(production traffic; who may sign in: 'Cloudflare account', never 'Email domain' gmail.com). Then run {again}.")


if __name__ == "__main__":
    main()

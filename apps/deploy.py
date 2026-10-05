#!/usr/bin/env python3
"""Put the built websites online as Cloudflare Workers (static files, free plan).

    python3 apps/deploy.py build --site maya-site=maya.example.com \\
                                 --dashboard maya-dashboard=crm.maya.example.com

Each option is WORKER_NAME=DOMAIN. The domain must be in your Cloudflare account; leave out
"=DOMAIN" to use only the public site's free workers.dev address. Uses `wrangler`
(npm install -g wrangler) logged in to your account (`wrangler login`), or the
CLOUDFLARE_API_TOKEN environment variable.

The dashboard is private: it gets no workers.dev address, only its own domain, and that domain
must sit behind Cloudflare Access (a login page) before you put real data in it. The guide shows
how. This script refuses to deploy a dashboard without a domain.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date
from pathlib import Path


def config(name: str, folder: str, domain: str, private: bool) -> dict:
    cfg = {
        "name": name,
        "compatibility_date": date.today().isoformat(),
        "assets": {"directory": folder, "not_found_handling": "404-page"},
        # A workers.dev or preview address would skip the login in front of the private domain.
        "workers_dev": not private and not domain,
        "preview_urls": False,
    }
    if domain:
        cfg["routes"] = [{"pattern": domain, "custom_domain": True}]
    return cfg


def deploy(build: Path, part: str, spec: str, private: bool) -> None:
    name, _, domain = spec.partition("=")
    if not (build / part / "index.html").is_file():
        sys.exit(f"{build / part} has no index.html; run build.py first")
    if private and not domain:
        sys.exit("--dashboard needs a domain (NAME=DOMAIN): the dashboard must not get a public workers.dev address")
    path = build / f"wrangler-{part}.json"
    path.write_text(json.dumps(config(name, part, domain, private), indent=2))
    print(f"deploying {part} as Worker '{name}'" + (f" on {domain}" if domain else " on workers.dev"))
    if subprocess.run(["wrangler", "deploy", "--config", str(path)]).returncode != 0:
        sys.exit(f"wrangler deploy failed for {part}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("build", type=Path, help="the --out folder of build.py")
    ap.add_argument("--site", metavar="NAME[=DOMAIN]", help="public site")
    ap.add_argument("--dashboard", metavar="NAME=DOMAIN", help="private dashboard")
    args = ap.parse_args()
    if not (args.site or args.dashboard):
        ap.error("nothing to deploy: give --site and/or --dashboard")
    if args.site:
        deploy(args.build, "site", args.site, private=False)
    if args.dashboard:
        deploy(args.build, "dashboard", args.dashboard, private=True)
        print("reminder: the dashboard domain must be behind Cloudflare Access before it holds real data")


if __name__ == "__main__":
    main()

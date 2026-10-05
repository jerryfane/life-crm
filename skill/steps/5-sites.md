# Step 5: Sites

**Goal:** the dashboard online behind a login only they (and people they choose) can pass, and,
if they want one, the public page with the CV.

## What they do

- Create a free Cloudflare account (or use theirs) and log in once through a link you give them.
- Turn on the login page for the dashboard: about 8 clicks, you guide them.
- Open both sites on their phone and say whether they look right.

## What you do

### 1. Show it locally first

Build from their Drive and show them the result before anything goes online:

```sh
python3 apps/pull.py --folder FOLDER_ID --sheet SHEET_ID --out work/data
python3 apps/build.py work/data/crm.xlsx --out work/build --cv --documents work/data/documents.json
```

Open `work/build/dashboard/index.html` and `work/build/site/index.html` yourself, at laptop and
phone width. Check `work/build/warnings.txt` is empty. Then let them look (same computer: give
the paths; otherwise screenshots).

Check the public page with them line by line: **no phone number, address, health, money or ID
numbers**. `phone` appears only in `work/build/cv/cv.pdf` (their own copy); the site and the CV
it offers for download leave it out. Anything typed into Entries is public. Set Profile
`cv_on_site` to `no` if they do not want a CV download on the page.

### 2. Decide the addresses

Ask with options:

| Option | Address | Cost |
|---|---|---|
| Free address (recommended to start) | `maya-site.<their-name>.workers.dev` | free |
| A domain they already own, moved to Cloudflare | `maya.example.com` | free if they have it |
| Buy a domain | `mayalindqvist.com` | about 10-15 USD a year: **ask first, they buy it** |

The dashboard can use the free address too: the login protects it either way.

### 3. Cloudflare access

```sh
npm install -g wrangler
wrangler login        # opens a browser login; on a remote machine follow wrangler's printed steps
wrangler whoami       # shows the account and, after the first deploy, their workers.dev name
```

Creating the account is theirs to do. If you are on a remote machine and the browser login is
not possible, ask them to create an API token (template "Edit Cloudflare Workers") and give it
to you as the `CLOUDFLARE_API_TOKEN` environment variable. Explain that it lets you publish
websites on their account, and that they can delete it any time.

### 4. Publish the public page

```sh
python3 apps/deploy.py work/build --site maya-site                     # free address
python3 apps/deploy.py work/build --site maya-site=maya.example.com    # own domain
```

Open the address, on a phone width too. Put the address in Profile `site_url` and rebuild, so
the page and CV link to it.

### 5. Publish the dashboard, behind a login

```sh
python3 apps/deploy.py work/build --dashboard maya-crm                     # first time, free address
python3 apps/deploy.py work/build --dashboard maya-crm=crm.maya.example.com  # first time, own domain
```

The first time, the script finds no login in front of the dashboard, uploads only a "locked"
page with no data, prints the address, and stops. Now guide them, one step per message:

1. If Cloudflare Zero Trust is not set up yet: dashboard → **Zero Trust**, pick a team name and
   the **Free** plan. Cloudflare may ask for a payment card even for the free plan: tell them
   before, and let them decide.
2. **Workers & Pages** → `maya-crm` → **Access** → **Protect this Worker behind Access**.
3. Choose **All traffic**.
4. Policy: allow **emails**: their own, plus anyone they chose in step 3.
5. **Apply Access**.

Then run it again with the address: `--dashboard maya-crm=maya-crm.<their-name>.workers.dev`
(the address printed the first time) or `--dashboard maya-crm=crm.maya.example.com`. It checks
the login is there and uploads the real
dashboard. Verify: open the address in a private browser window. You must see a Cloudflare
login page, not the dashboard. Then they log in with the code Cloudflare emails them and see
their dashboard.

Write both addresses in `work/crm.json` (`"site"`, `"dashboard"`) and in `work/NOTES.md`.

### No Cloudflare?

The dashboard also works as a file: `work/build/dashboard/index.html` opens in any browser,
offline. It does not update itself, but it is fine for trying the setup. A public page needs
hosting; skip it until they want one.

## Done when

They opened the dashboard through the login on their own phone, the public page (if any) is
checked line by line, and the addresses are saved in `work/crm.json`.

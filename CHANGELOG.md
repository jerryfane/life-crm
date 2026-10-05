# Changelog

## Unreleased

- Guide cut from 25 pages to 4: a cover with the prompt, then one page each for what you get,
  the 8 steps, and privacy/costs. The build fails if a chapter spills past one page.

## v1.0.0 (2026-10-05)

First release.

- **Agent skill** (`skill/`): an 8-step conversation that takes a non-developer from a recorded
  talk to a working personal CRM: interview, goals, clickable proposals, Google Drive storage,
  sites, a guide for their chat assistant, handoff, upkeep.
- **Apps** (`apps/`): one spreadsheet builds a private dashboard (roadmap, timeline pages,
  table/cards/feed pages, documents), a public one-page site and a LaTeX CV. `pull.py` reads
  Google Drive through drivekey; `deploy.py` publishes to Cloudflare Workers and uploads the
  dashboard only once a Cloudflare Access login answers; `update.py` runs all three.
- **Examples** (`examples/`): a fictional medical student (Maya Lindqvist), money, health.
- **Guide** (`guide/`): 13 plain-language chapters and an illustrated A5 PDF built from them.
- **Demo**: https://life-crm.jerryfane.com

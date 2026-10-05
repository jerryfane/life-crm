# Changelog

## Unreleased

- Public page: new "classic CV" layout. Sticky profile and section list on the left (a scrollable row of
  section buttons on phones), compact entries on the right with details on tap; self-hosted fonts.
- New landing page at life-crm.jerryfane.com: the quiet design with the "Chat" hero (the
  prompt is the first message of a chat with your agent, Maya's dashboard on an iPhone is the
  answer), timeline, how the pieces fit, three live examples, steps, cost and privacy. On phones
  the chat and its Copy button fit the first screen down to 375×667.
- Landing: new "Lanes" logo (sharp at 16 and 24 px). The hero chat plays out once (prompt,
  question, answer, then the iPhone with the result), sections slide in as you reach them, and
  the setup steps fill in as you scroll. All motion is off when the device asks for reduced motion.
- Guide (15 pages): the chat assistant page explains what one is, and a new page compares real
  options (Claude, dots by OpenAI, Muse by Meta, Hermes Agent, OpenClaw, Grok Bot; checked October 2026) and the
  ones to skip; skill step 6 carries the same list. Step 1 shows the full prompt to paste. The
  site address life-crm.jerryfane.com is on the first and last pages.
- Guide rewritten (one topic per page): what it is, the framework diagram and each
  piece explained, the personal chat assistant with an example chat, before you start, one page
  per setup step with examples (dictating with Wispr Flow, example goals, what "choose" means),
  daily use, privacy. Notes are flat panels. The build fails if a chapter spills.

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

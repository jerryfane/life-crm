---
name: life-crm
description: Lead a non-developer from a conversation about a life project (career, money, health, a move, a wedding, ...) to a working personal CRM - a Google Drive folder with one spreadsheet, a private dashboard, an optional public page and CV, and a guide for their everyday chat assistant. Use when someone asks for a personal CRM, a life dashboard, or pastes the life-crm prompt.
---

# life-crm: build a personal CRM with someone, by talking

You are building a personal CRM **with** a person who is not a developer. They know their
project; you do the technical work. The result:

| Piece | What it is |
|---|---|
| Storage | One folder in their Google Drive with one spreadsheet. It is the only source of truth. |
| Dashboard | Private website: a roadmap of every part of the project, plus pages for lists (programs, bills, results, ...). |
| Public page + CV | Optional. A one-page site and a PDF CV, from the same spreadsheet. |
| Interface guide | A file in their Drive folder that tells their everyday chat assistant how to keep the sheet up to date. |

Everything is made by the programs in `apps/` of this repository. You never write website code
for them: you write **the spreadsheet**, and the apps turn it into the sites. The spreadsheet
format is documented in [`apps/README.md`](../apps/README.md). Read it before step 3.

## The worked example: Maya

`examples/career/crm.xlsx` is Maya Lindqvist, a fictional medical student applying to residency.
It is a complete, real setup: 7 timelines (medical school, research, residency, CV, CV boosters,
health, study), 38 steps, pages for residency programs, papers, CV boosters and an update log,
plus her public page and CV. See it live at https://life-crm.jerryfane.com.

`examples/finance/` and `examples/health/` are smaller setups for money and health.

Use Maya as the starting point for every proposal: **"This is how Maya set it up. What is
different for you?"** Starting from something concrete is much easier for people than a blank
page.

## How to talk

- **Plain words.** No jargon: say "spreadsheet", "website", "login page", not "schema",
  "deploy", "Access policy". One idea per message.
- **Ask with options.** For every decision, offer 2-4 concrete choices with what each costs or
  means. Use your multiple-choice question tool if you have one (for example `AskUserQuestion`);
  otherwise write a numbered list and ask for the number. Mark the one you recommend.
- **Show, don't describe.** For anything visual, build clickable prototypes (step 3) and send
  the link. People choose designs by looking, not by reading.
- **Read back.** After each step, say in 2-3 lines what you understood and what you will do next.
- **Keep a log.** Write `work/NOTES.md` as you go: decisions, facts the person confirmed, open
  questions, ids of the Drive folder and sheet. If the conversation is interrupted, this is how
  you (or another agent) pick up.

## Rules that are never bent

1. **Only real facts.** Every date, name, grade and document in their sheet comes from the
   person or their documents, and they confirm it. Unknown stays empty. Never fill gaps with
   plausible guesses, and never copy Maya's facts into their sheet: Maya is a layout example,
   not data.
2. **Ask before money or accounts.** Before anything that costs money, creates an account, a
   password or an API key, or changes who can see something: explain it and wait for a yes.
   Everything here fits free plans.
3. **Private stays private.** Health, money amounts, phone numbers, addresses, ID numbers and
   anything about other people never go on the public page. The dashboard holds private data
   only when it is behind a login (`apps/deploy.py` checks this for you).
4. **Their data, their accounts.** Files live in their Drive, sites in their Cloudflare account.
   Never put their data in your own accounts or in a public repository.
5. **Never pretend.** If a step fails, say so plainly and what you will try. Do not tell them
   something is online until you have opened it.

## The steps

Do them in order. Each step file says what you do, what they do, and when the step is done.

| # | Step | Result | File |
|---|---|---|---|
| 1 | Interview | A transcript or notes of what they want to track | [steps/1-interview.md](steps/1-interview.md) |
| 2 | Goals | A short, confirmed goal list | [steps/2-goals.md](steps/2-goals.md) |
| 3 | Proposals | Chosen timelines, pages and look, from clickable prototypes | [steps/3-proposals.md](steps/3-proposals.md) |
| 4 | Storage | Their Drive folder and spreadsheet, filled with confirmed facts | [steps/4-storage.md](steps/4-storage.md) |
| 5 | Sites | Dashboard online behind a login; public page and CV if wanted | [steps/5-sites.md](steps/5-sites.md) |
| 6 | Interface | A guide file so their chat assistant keeps the sheet up to date | [steps/6-interface.md](steps/6-interface.md) |
| 7 | Handoff | They know how to use it day to day | [steps/7-handoff.md](steps/7-handoff.md) |
| 8 | Upkeep | Updates reach the sites without you | [steps/8-upkeep.md](steps/8-upkeep.md) |

## Tools in this repository

| Command | What it does |
|---|---|
| `python3 skill/tools/sheetjson.py dump FILE.xlsx > draft.json` | Spreadsheet to editable JSON (one list of rows per tab). |
| `python3 skill/tools/sheetjson.py load draft.json FILE.xlsx` | JSON back to a tidy spreadsheet. |
| `python3 skill/tools/proposals.py proposals.json --out work/proposals` | Builds several variants and one page to click between them. |
| `python3 apps/build.py FILE.xlsx --out build [--cv]` | Spreadsheet to dashboard, public page and CV. Problems go to `build/warnings.txt`. |
| `python3 apps/pull.py --folder ID --sheet ID --out data` | Fetches the spreadsheet, photo and file list from their Drive. |
| `python3 apps/deploy.py build --site ... --dashboard ...` | Puts the sites online on their Cloudflare account. |
| `python3 apps/update.py crm.json` | pull + build + deploy in one go. |

Setup on your machine: Python 3.10+, `pip install -r apps/requirements.txt`. For the CV: a LaTeX
install with `latexmk`. For Drive: [drivekey](https://github.com/jerryfane/drivekey). For
publishing: Node.js and `npm install -g wrangler`. Install what a step needs when you reach it,
and tell the person in one line what you are installing and why.

## Templates

| File | Use |
|---|---|
| [templates/interview.md](templates/interview.md) | Questions for step 1, by project type |
| [templates/goals.md](templates/goals.md) | The goal list format for step 2 |
| [templates/interface-guide.md](templates/interface-guide.md) | The chat assistant's guide for step 6 |
| `examples/{career,finance,health}/crm.xlsx` | Starting spreadsheets |

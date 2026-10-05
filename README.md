# life-crm

Build your own personal CRM for any life project (your career, your money, your health, a move, a wedding) with the help of an AI agent. No coding needed: you talk, your agent builds.

> **Status: under construction.** The guide, the agent skill and the demo are being written. Watch this repo or check back soon.

## How it works

1. **You talk about what you want to keep track of.** Record a conversation (for example with a voice-to-text app) about your goals, deadlines and the documents you have scattered around.
2. **Your agent turns that into a plan.** It asks you questions and shows you options to pick from, based on a real example (a medical student applying to residency).
3. **Your data lives in Google Drive.** Folders and spreadsheets you can open and edit yourself, any time.
4. **Your agent builds two websites from that data:** a public page (like a portfolio) and a private dashboard only you can log into, showing every part of your project on one timeline.
5. **A chat assistant keeps it up to date.** You tell it "today I did X" and it updates the spreadsheet; the websites follow.

## The pieces

| Piece | What it is | In the example |
|---|---|---|
| Human | You: you set the goals and confirm the facts | The student |
| Capture | The recorded conversation that starts everything | A voice-to-text transcript |
| Engine | The AI agent that builds and maintains everything | A coding agent (Claude Code, Codex, …) |
| Workspace | The engine's folder and its history | A folder + a GitHub repo |
| Storage | Where your data lives, readable by humans | Google Drive folders and Sheets |
| Interface | The AI you chat with day to day | A chat agent with Google Drive access |
| Website | The views of your data | A public page + a private dashboard |
| Privacy | Who can see what | A login in front of the private dashboard |

## What's in this repo

| Folder | What it is |
|---|---|
| [`apps/`](apps/) | The code that turns your spreadsheet into the dashboard, the public site and the CV ([reference](apps/README.md)) |
| [`examples/`](examples/) | Three ready spreadsheets: a career (a fictional medical student), money, and health |

## License

[AGPL-3.0](LICENSE).

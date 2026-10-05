# The pieces

![You talk to your agent, which sets up one spreadsheet in Google Drive. Your chat assistant keeps it current. The spreadsheet builds a private dashboard, a public page and a CV.](img/pieces.svg)

| Piece | What it is | Maya's |
|---|---|---|
| **You** | Set the goals, confirm every fact | Maya |
| **Your agent** | The AI that interviews you and builds everything | A coding agent on her laptop |
| **Storage** | Where your data lives, readable by you | One Drive folder with one spreadsheet |
| **Dashboard** | Private website made from the spreadsheet | Roadmap, programs, papers, boosters, updates |
| **Public page + CV** | Optional, made from the same spreadsheet | Her portfolio page and PDF CV |
| **Login** | The lock in front of the dashboard | A Cloudflare login: only her email gets in |
| **Chat assistant** | The AI you talk to every day | Her phone's chat app, connected to Drive |

## Why one spreadsheet

Everything reads from it and nothing else holds the truth. That has three good effects:

1. **You can always see and fix your data** without any app. It is just a spreadsheet.
2. **Nothing gets out of sync.** Change a date once; the dashboard, page and CV follow.
3. **You are not locked in.** If you stop using the websites, the spreadsheet is still yours.

## Why your agent asks so many questions

Because it must not guess. Every date, grade and name in your sheet comes from you or your
documents, and you confirm it. An empty cell is better than a plausible wrong one, especially
in anything you will send to a school, an employer or a bank.

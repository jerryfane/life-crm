# Each piece, explained

| Piece | What it is | In Maya's case |
|---|---|---|
| **Human** | You. You set the goals and confirm every fact. Nothing goes in the sheet that you did not say or a document does not show. | Maya, talking about her residency plans. |
| **Engine** | An AI agent that can run commands on a computer: it installs tools, writes files, builds websites. You use it to set things up and for bigger changes later. | Claude Code on her laptop. Codex works too. |
| **Repo** | The engine's workspace: a folder on your computer holding its notes and the building tools. Optionally backed up on GitHub. | A `life-crm` folder with a `work` subfolder. |
| **Storage** | One folder in your Google Drive with one spreadsheet and your documents. The single source of truth: every other piece reads from it or writes to it. | "Maya CRM": the sheet, plus folders for CV, certificates, letters. |
| **Interface** | Your everyday chat assistant, connected to your Drive. You tell it what happened; it updates the sheet. See the next page. | A chat app on her phone. |
| **Website** | Built from the spreadsheet: a private dashboard, plus an optional public page and CV. | Her roadmap dashboard and her portfolio page. |
| **Login** | A Cloudflare login in front of the dashboard. Only the email addresses you allow get in; strangers see a login page. | Only Maya's email. |
| **Connectors** | Where facts come from: email, calendar, a fitness tracker. Your assistant or agent reads them when you ask, never on its own. | Her school email and calendar. |

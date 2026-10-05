# The big picture

Seven pieces work together. You only talk to two of them: your AI agent while setting things up, and your chat assistant every day after that.

![You talk to your chat assistant and to your agent. The agent builds a repo and one spreadsheet in Google Drive. The spreadsheet feeds a private dashboard and an optional public page, behind a Cloudflare login. Connectors like email and calendar bring in facts.](img/framework.svg)

> **How to read it:** Follow the spreadsheet in the middle. Your agent builds it, your chat assistant keeps it current, connectors bring facts into it, and the website shows it back to you. Everything below the line is private; only the optional public page sits above it.

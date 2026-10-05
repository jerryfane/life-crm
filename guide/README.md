# The guide

**[Download the guide (PDF)](life-crm-guide.pdf)**: 7 pages, A5, reads well on a phone.

1. Cover, with the prompt to paste into your agent
2. [What life-crm is](01-what-it-is.md)
3. [Before you start](02-before-you-start.md): what you need, what it costs, what to have ready
4. [Setting it up: steps 1-4](03-setup-1.md): talk, goals, choose, store
5. [Setting it up: steps 5-8](04-setup-2.md): publish, assistant, handoff, keep going
6. [Using it day to day](05-day-to-day.md)
7. [Privacy, rules and questions](06-rules.md)

The chapters are the source of the PDF; each fits one page. After editing one, rebuild with
`python3 guide/build.py` (needs `markdown-it-py`, Chrome or Chromium, and `pdfinfo`). The build
fails if a chapter spills onto a second page.

# The guide

**[Download the guide (PDF)](life-crm-guide.pdf)**: 4 pages, A5, reads well on a phone.

1. Cover, with the prompt to paste into your agent
2. [What you get](01-what-you-get.md)
3. [How it goes](02-the-steps.md): the 8 steps, what you do and what your agent does
4. [Yours to keep](03-yours.md): privacy, costs, other projects

The chapters are the source of the PDF; each fits one page. After editing one, rebuild with
`python3 guide/build.py` (needs `markdown-it-py`, Chrome or Chromium, and `pdfinfo`). The build
fails if a chapter spills onto a second page.

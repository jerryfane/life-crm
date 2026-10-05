# Step 6: Interface

**Goal:** the person keeps their CRM up to date by chatting with the AI assistant they already
use every day, without you. The assistant reads and edits the spreadsheet in their Drive,
following a guide file you write.

## What a chat assistant is

An AI they message like a friend (in WhatsApp, Telegram or its own app) that can open their
Google Drive: it reads the sheet to answer questions and edits it when they say what happened.
Explain it in those words if they have never used one.

## What they do

- Pick an assistant and connect it to Google Drive. Menus change often: search the assistant's
  own help for "Google Drive" rather than relying on memory, and send them the link.
- Tell the assistant to read the guide file whenever they talk about the project (a project or
  custom instruction: "Before answering about my CRM, read `GUIDE.md` in my *Maya CRM* folder").

## What you do

1. Ask which assistant they use daily. If they have none, or it cannot edit Sheets, offer the
   options below and let them pick; this step can wait until they have one.
2. Check that assistant's current help pages: can it **edit** Google Sheets or only read them?
   The table below was checked in October 2026 and goes stale; do not repeat it as fact without
   checking. If it can only read, it can still answer questions and write out the exact change
   for them to paste; say so honestly.

   | Assistant | Where they chat | Sheets | Setup |
   |---|---|---|---|
   | Claude (claude.ai) | Claude app, web, desktop | Read + edit (beta, web and desktop) | Toggle the Google connectors |
   | Muse by Meta (ai.meta.com/muse) | WhatsApp, Muse app | Google connectors; Sheets editing not confirmed by Meta | Tap Connectors; US only; free with a limit |
   | Hermes Agent (hermes-agent.nousresearch.com, github.com/NousResearch/hermes-agent) | Telegram, WhatsApp, Slack, Signal, more | Read + write via its Google Workspace skill | Self-hosted or Hermes Cloud; needs a Google Cloud OAuth client; pay for the model |
   | OpenClaw (openclaw.ai, github.com/openclaw/openclaw) | WhatsApp, Telegram, iMessage, more | Read + write via the `gog` skill | Runs on their computer (must stay on); needs a Google OAuth client; pay for the model |
   | Grok Bot by xAI (docs.x.ai/grok-bot) | Own app only | Sheets connector exists; editing not documented | Paid (Cursor Pro or SuperGrok, from $20/month) |

   Do not suggest Dot by New Computer (shut down October 2025), the Gemini app (cannot edit
   Drive) or @GrokAI on Telegram (no Drive access). Link only the official sites above: look-alike
   domains exist for Hermes and OpenClaw. For Hermes or OpenClaw you do the install and the Google
   OAuth setup with them, asking before anything that costs money; never ask for their password.
3. Decide now how updates will reach the sites (the options are in
   [step 8](8-upkeep.md#choose-how-it-runs)), because the guide tells the assistant how long
   changes take to appear. "On request" is a fine start.
4. Write the guide from [../templates/interface-guide.md](../templates/interface-guide.md). Fill
   in every `<...>`: their name, the folder layout, each tab and column **exactly as in their
   sheet**, what the assistant may change, and the rules. Remove sections they do not use (no
   public page → no Profile/Entries section).
5. Upload it to the root of their folder:
   `drivekey put work/GUIDE.md --parent FOLDER_ID --name GUIDE.md`
6. Test it with them: they ask their assistant two things, and you check the sheet afterwards.
   - A question: "What are my next three deadlines?"
   - An update: "Today I finished <a real task>." The assistant should mark it `done`, and ask
     before adding anything public.
   If the assistant gets it wrong, improve the guide (usually: be more explicit about which tab
   and column), upload it again with `drivekey put work/GUIDE.md --replace GUIDE_FILE_ID`, and
   repeat.

## What the guide must say

- Which folder and sheet, and what each tab and column means.
- What the assistant may do on its own (mark a task done, add a new task with a date the person
  gave, add an update row) and what needs a "yes" first (anything public, deleting rows,
  changing timelines or pages).
- **Never invent facts.** Unknown dates stay empty. If something is unclear, ask.
- Privacy: what never goes on the public page; health stays titles only unless they chose more.
- That the sites update by themselves after the sheet changes (step 8), within the delay you
  set up, so it does not need to do anything else.

## Done when

The guide is in their folder, their assistant has Drive access and the instruction to read it,
and both test messages worked.

# Step 6: Interface

**Goal:** the person keeps their CRM up to date by chatting with the AI assistant they already
use every day, without you. The assistant reads and edits the spreadsheet in their Drive,
following a guide file you write.

## What they do

- Connect their chat assistant to Google Drive. Most assistants have a Google Drive connector
  (often under Settings → Connectors, Apps or Extensions). Menus change often: search the
  assistant's own help for "Google Drive" rather than relying on memory, and send them the link.
- Tell the assistant to read the guide file whenever they talk about the project (a project or
  custom instruction: "Before answering about my CRM, read `GUIDE.md` in my *Maya CRM* folder").

## What you do

1. Ask which assistant they use daily. If they do not have one, offer 2-3 common ones with Drive
   connectors and let them pick; this step can wait until they have one.
2. Find out, from that assistant's help pages, whether its Drive connector can **edit** Google
   Sheets or only read them. If it can only read, it can still answer questions and write out the
   exact change for them to paste; say so honestly.
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

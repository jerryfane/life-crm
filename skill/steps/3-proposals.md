# Step 3: Proposals

**Goal:** decide what the dashboard contains and how it looks, by letting the person click
through real options instead of reading descriptions.

The pattern that works: **a few quick decisions → 3-4 clickable options → pick one → 2-3
refinements of it → confirm.** People rarely know what they want until they see two versions
next to each other.

## What you do

### 1. Map their goals onto the building blocks

Read [`apps/README.md`](../../apps/README.md) first. The blocks are:

| Block | Use it for | Maya | Money | Health |
|---|---|---|---|---|
| **Timeline** (a lane on the roadmap) | a part of the project that moves over time | Medical school, Residency | Car loan, Taxes | Check-ups, Fitness |
| **Step**: period / milestone / task | something with dates: a stretch, a deadline, a to-do | a rotation, an exam, "ask for a letter" | "pay off loan", "file taxes" | "book dentist" |
| **Collection page**: table / cards / feed | a list of similar things | residency programs (table), papers (cards), updates (feed) | bills, accounts | lab results |
| **Public page + CV** | showing yourself to others | yes | no | no |

Start from the closest example (`examples/career`, `finance` or `health`) and write down, in
`work/NOTES.md`, which timelines, pages and fields their goals need.

### 2. Ask the few decisions that shape everything

Ask with options, one question at a time or batched in one multiple-choice call. Typical ones:

- **Timelines.** "Maya has 7 lanes. From your goals I would make these 5: … Anything to add,
  merge or drop?"
- **Lists.** "These look like lists you will want to compare: … Should each be its own page?"
- **Public page.** "Do you want a public page and a CV too, or only the private dashboard?"
- **Who else sees the dashboard.** "Only you, or also someone else (partner, parent,
  coach)?"

### 3. Build 3-4 clickable options

1. Dump the starting example: `python3 skill/tools/sheetjson.py dump examples/career/crm.xlsx > work/proposals/base.json`.
2. Make 3-4 copies (`a.json`, `b.json`, ...) that differ in ways that **matter to the person**,
   for example:
   - lanes grouped by area vs. one lane per goal;
   - a list as a table (compare many fields) vs. cards (fewer, richer items);
   - a 12-month roadmap vs. 6 months (more detail, less overview);
   - an update log page or not.
   Change the tabs (Timelines, Steps, Settings, Collections and the collection tabs) to their
   project: their timeline names, their pages, their column names.
3. **Rows in prototypes.** Use the facts they already confirmed. Where you have none yet, write
   clearly fake sample rows: start every sample title with `Example:` and leave dates rough.
   Never put Maya's facts in.
4. Write `work/proposals/proposals.json`: a title, a one-line intro, and per option a short
   label ("A · Grouped by area") and one sentence on what is different. Then build:
   `python3 skill/tools/proposals.py work/proposals/proposals.json --out work/proposals/site`
5. Check warnings it prints and fix them. Open the page yourself and click each option before
   sending it.

### 4. Let them click

- **Same computer:** tell them to open `work/proposals/site/index.html` (give the full path),
  or run `python3 -m http.server -d work/proposals/site 8000` and send http://localhost:8000.
- **You run on another machine** (a server or a cloud agent): the prototypes must reach them
  without exposing their data. Either build the options **with sample rows only** (no real
  facts at all) and publish them for a few days:
  `wrangler deploy --assets work/proposals/site --name proposals-<name> --compatibility-date <today>`,
  then delete it (`wrangler delete proposals-<name>`) once they have chosen; or send
  screenshots. This needs their Cloudflare account (step 5), so ask first.

Ask: **"Which one feels closest? What would you change?"** Offer the options plus "a mix".

### 5. Refine, then confirm

Build a second round of 2-3 variations of the chosen option, changing only what they
commented on (colors, order of lanes, which columns a table shows, page names). Repeat until
they say "this one". Then write down in `work/NOTES.md`: the chosen JSON file, and every
decision with the date.

## Good to know

- Colors: each timeline gets one (teal, indigo, amber, blue, pink, green, violet, red, orange,
  gray, or a hex code). Give related lanes related colors.
- Icons for pages: roadmap, bell, building, document, star, folder, wallet, heart, calendar,
  list.
- Keep it small. Two rounds is usually enough; if a third round is still changing big things,
  go back to step 2 and check the goals.
- The dashboard also works on a phone. If they will mostly use their phone, show them the
  prototype on it.

## Done when

They picked a design, and you have the chosen JSON in `work/proposals/` and the decisions in
`work/NOTES.md`.

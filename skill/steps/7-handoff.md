# Step 7: Handoff

**Goal:** the person knows how to use their CRM day to day, and where everything is, without
needing you.

## What you do

1. Write `work/MY-CRM.md` in plain language and upload it next to the guide
   (`drivekey put work/MY-CRM.md --parent FOLDER_ID`). Keep it to one screen:

   | What | Where |
   |---|---|
   | Your spreadsheet | link |
   | Your dashboard (login with your email) | link |
   | Your public page | link (or "none") |
   | Your CV | link to the PDF on the public page, or "built on request" |
   | Your folder | link |

   Then three short sections:
   - **Every day:** tell your assistant what happened ("today I submitted the application").
   - **When something changes:** edit the sheet directly, or tell the assistant. The sites
     follow within `<delay>`.
   - **If something looks wrong:** the dashboard lists problems at the bottom (for example a
     date it cannot read). Fix that row in the sheet.

2. Show them, live if possible, three things on their own phone:
   - opening the dashboard (and adding it to the home screen);
   - their assistant updating one row;
   - the change appearing on the dashboard after the delay.

3. Tell them what you have access to and how to switch it off:
   - Google Drive: https://myaccount.google.com/permissions ("Google Cloud SDK"), or
     `drivekey logout`;
   - Cloudflare: delete the API token, if they gave you one.
   Ask whether they want you to keep access for upkeep (step 8) or not.

4. Ask for feedback with options: "Is anything missing / too much / hard to use?" Note the
   answers in `work/NOTES.md` and fix small things now.

## Done when

They opened the dashboard on their phone, saw an assistant update arrive, have `MY-CRM.md`,
and know how to remove your access.

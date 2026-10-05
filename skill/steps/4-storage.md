# Step 4: Storage

**Goal:** their own Google Drive folder with one spreadsheet holding only confirmed facts, and
their documents sorted into subfolders. From now on the spreadsheet is the single source of
truth: the sites and the chat assistant both read it.

## What they do

- Log in to Google once, through a link you give them (about 2 minutes).
- New Google Cloud users only: open https://console.cloud.google.com once and accept the terms.
- Check the spreadsheet and correct anything wrong.
- Move or send you their documents.

## What you do

### 1. Get access to their Drive

Use [drivekey](https://github.com/jerryfane/drivekey); its `AGENTS.md` has the exact sequence
and error codes. In short:

```sh
curl -fsSL https://raw.githubusercontent.com/jerryfane/drivekey/main/install.sh | sh
drivekey login            # prints a link: send it to them, they log in and paste back a code
drivekey login --code CODE
drivekey setup            # their own free Google Cloud project, Drive + Sheets turned on
```

Before the login, tell them plainly: "This lets me read and change files in your Google Drive.
I will only work inside the folder we create. You can switch it off any time at
https://myaccount.google.com/permissions." drivekey needs Google's `gcloud` tool (about
500 MB); say so before installing it.

### 2. Create the folder

Agree on a name ("Maya CRM", "Money 2027"). Then create it and the subfolders their documents
need, for example:

| Project | Subfolders |
|---|---|
| Career | `CV`, `Certificates`, `Letters`, `Applications`, `Research`, `Website` (photo) |
| Money | `Statements`, `Taxes`, `Contracts`, `Receipts` |
| Health | `Results`, `Prescriptions`, `Insurance` |

```sh
drivekey mkdir "Maya CRM"                        # note the folder id it prints
drivekey mkdir "Certificates" --parent FOLDER_ID
```

### 3. Write the spreadsheet

1. Copy the chosen proposal JSON to `work/sheet.json`, then **remove every `Example:` row
   and every fact they have not confirmed.** Keep the structure: tabs, headers, Timelines,
   Collections, Settings.
2. Fill in the confirmed facts from `work/interview.md` and `work/NOTES.md`. Unknown dates stay
   empty. Rows you are unsure should be visible get `show` = `no`.
3. Build it locally first and fix every warning:
   ```sh
   python3 skill/tools/sheetjson.py load work/sheet.json work/crm.xlsx
   python3 apps/build.py work/crm.xlsx --out work/build --cv
   ```
4. Upload it as a Google Sheet, and the photo if there is a public page:
   ```sh
   drivekey put work/crm.xlsx --parent FOLDER_ID --name "CRM" --convert   # note the sheet id
   drivekey put photo.jpg --parent WEBSITE_FOLDER_ID
   ```
   In Profile, set `photo` to the path inside the folder, e.g. `Website/photo.jpg`.
5. Write `work/crm.json` (it holds no secrets; `apps/update.py` reads it in step 8):
   ```json
   {"folder": "FOLDER_ID", "sheet": "SHEET_ID", "cv": true}
   ```
6. Check the round trip: `python3 apps/pull.py --folder FOLDER_ID --sheet SHEET_ID --out data`
   then build from `data/crm.xlsx`. It must give the same result as your local file.

### 4. Walk them through it

Send them the sheet link (`https://docs.google.com/spreadsheets/d/SHEET_ID`) and explain the tabs
in one line each. Ask them to check every date and name. Set `sheet_url` in Settings to the link,
so the dashboard links back to it.

### 5. Documents

Ask them to move the files that matter into the subfolders, or to send them to you and upload
them with `drivekey put FILE --parent SUBFOLDER_ID`. Name files so a human can find them:
`YYYY-MM Issuer - What.pdf`. Never rename or delete their files without asking.

## Rules

- Only confirmed facts. If the documents and what they told you disagree, ask.
- Health: titles only ("Dentist", "Blood test"), no diagnoses or values unless they explicitly
  want them in their private dashboard. Never on the public page.
- Work only inside the folder you created.

## Done when

The folder and sheet exist in their Drive, they have checked the sheet, `work/crm.json` has the ids,
and pull + build works with 0 warnings.

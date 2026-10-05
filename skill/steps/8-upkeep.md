# Step 8: Upkeep

**Goal:** changes in the spreadsheet reach the dashboard and public page on their own.

One command does everything: fetch from Drive, build, publish. Every run checks the dashboard's
login first; if it cannot see the login (for example Access was switched off), it publishes the
locked page instead of the data and stops.

```sh
python3 apps/update.py work/crm.json
```

`work/crm.json`:

```json
{
  "folder": "FOLDER_ID",
  "sheet": "SHEET_ID",
  "cv": true,
  "site": "maya-site=maya-site.<their-name>.workers.dev",
  "dashboard": "maya-crm=maya-crm.<their-name>.workers.dev"
}
```

## Choose how it runs

Ask with options. All of them need a computer that is on with drivekey and wrangler logged in.

| Option | Good for | How |
|---|---|---|
| **On request** | trying it out; laptops that sleep | they ask you ("update my sites") and you run the command |
| **Every hour on their computer** | a laptop or desktop that is often on | a scheduled task (below) |
| **On an always-on machine** | a home server or a small cloud machine | the same scheduled task there; a cloud machine costs money: **ask first** |

### Scheduled task

macOS and Linux, every hour, with a log (`crontab -e`, one line):

```
0 * * * * cd /path/to/life-crm && /usr/bin/python3 apps/update.py work/crm.json >> work/update.log 2>&1
```

Windows: Task Scheduler → Create Basic Task → Daily → repeat every 1 hour → start
`python` with arguments `apps\update.py work\crm.json` in the repository folder.

Check the first two runs in the log. If drivekey says `not_logged_in` or wrangler says
`Authentication error`, the login expired: log in again (steps 4 and 5).

## When they want changes

The structure lives in the spreadsheet too, so most changes need no code:

| They want | You change |
|---|---|
| a new part of the project | a row in **Timelines** |
| a new list (apartments, venues, scholarships) | a row in **Collections** + a new tab |
| a column on a page | the `fields` of that **Collections** row |
| a longer or shorter roadmap | `window_months` in **Settings** |
| a section on the public page or CV | rows in **Entries**, and the `sections` order in **Profile** |

For bigger changes (a new kind of page), go back to step 3 and prototype first. Update
`GUIDE.md` (step 6) whenever tabs or columns change, or their assistant will write to the wrong
place.

## Done when

The update runs the way they chose, and a test edit in the sheet showed up on the dashboard.

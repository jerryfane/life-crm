# Step 8: Keep it running

Your websites are rebuilt from the spreadsheet with one command. The last choice is how often
that runs.

| Option | Good for | What you need |
|---|---|---|
| **When you ask** | trying it out; laptops that sleep | ask your agent "update my sites" |
| **Every hour on your computer** | a computer that is often on | a scheduled task your agent sets up |
| **On an always-on machine** | updates even when your laptop is off | a home server, or a small cloud machine (costs money: you decide) |

> **Your agent does:** sets up the option you chose, checks the first runs, and tells you what
> to do if a login expires (log in again; it takes a minute).

> **You do:** make one test edit in the sheet and check it reaches the dashboard.

Every update checks that the dashboard's login is still on. If it is not, the dashboard is
replaced by the locked page instead of showing your data.

## Changing things later

Most changes need no code, because the structure lives in the spreadsheet too:

| You want | Change |
|---|---|
| a new part of your project | a row in **Timelines** |
| a new list (apartments, venues, scholarships) | a row in **Collections** and a new tab |
| a column on a page | that page's row in **Collections** |
| a longer or shorter roadmap | **Settings** |

Your assistant can do the small ones. For bigger ones, ask your agent: it will show you
options again, like in step 3.

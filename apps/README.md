# The apps

One spreadsheet in, three things out:

| Output | What it is | Built when |
|---|---|---|
| `dashboard/` | Private dashboard: a roadmap of all your timelines, one page per timeline, and extra pages (tables, cards, a feed) | always |
| `site/` | Public one-page site, like a portfolio | the sheet has **Profile** and **Entries** tabs |
| `cv/cv.pdf` | A CV in PDF, also offered as a download on the site | with `--cv` (needs LaTeX) |

All three are plain static files. No server, no database.

## Try it

```sh
pip install -r apps/requirements.txt
python3 apps/build.py examples/career/crm.xlsx --out build/career --cv
python3 -m http.server -d build/career 8000   # open http://localhost:8000/dashboard/
```

`examples/` has three spreadsheets: `career` (a fictional medical student, Maya Lindqvist),
`finance` and `health`. `python3 examples/make_examples.py` regenerates them.

## The everyday loop

```sh
python3 apps/pull.py --folder FOLDER_ID --sheet SHEET_ID --out data        # Google Drive -> data/
python3 apps/build.py data/crm.xlsx --out build --cv --documents data/documents.json
python3 apps/deploy.py build --site me-site=me.example.com --dashboard me-crm=crm.me.example.com
```

- `pull.py` reads Drive with [drivekey](https://github.com/jerryfane/drivekey) and never changes
  it. It fetches the spreadsheet, the photo named in Profile, and the folder's file list for the
  dashboard's Documents page.
- `build.py` never stops on a bad row. Problems are listed in `build/warnings.txt` and at the
  bottom of the dashboard, so whoever edits the sheet can fix them.
- `deploy.py` publishes with Cloudflare `wrangler`, on your own domain or a free `workers.dev`
  address. Before uploading the dashboard it checks that its address asks for a Cloudflare
  Access login. If not, it uploads only a "locked" page with no data and tells you how to turn
  the login on (Workers & Pages > your Worker > Access). Rerun it afterwards.
- No Cloudflare? The dashboard also works offline: open `build/dashboard/index.html` in a browser.

## The spreadsheet

Tab names and column headers are case-insensitive. Spaces in headers become `_`
(`Apply by` = `apply_by`). Every tab with rows can have a `show` column: `no` hides a row.
In dashboard tabs, dates are `YYYY-MM-DD`, or a month like `May 2027` (shown as approximate).

### Dashboard tabs

**Timelines**: one row per area of your life, shown as a lane on the roadmap.

| Column | Meaning |
|---|---|
| `id` | short name used by the other tabs, e.g. `residency` (required) |
| `name` | shown name (required) |
| `group` | lanes with the same group sit together (`Career`, `Admin`, …) |
| `color` | teal, indigo, amber, blue, pink, green, violet, red, orange, gray, or a hex code |
| `goal`, `description` | shown on the timeline's page |
| `link` | a Drive folder or document for this timeline |
| `order` | number; lower comes first |

**Steps**: what happens inside a timeline.

| Column | Meaning |
|---|---|
| `timeline` | a Timelines `id` (required) |
| `title` | (required) |
| `kind` | `period` (a bar from `start` to `end`), `milestone` (a diamond on `date`) or `task` (a to-do, `date` optional) |
| `start`, `end`, `date` | dates as above |
| `status` | `todo`, `doing`, `done` or `to book` |
| `progress` | `0`–`100`, for periods |
| `track` | rows inside a timeline's page, e.g. `Exams`, `Letters` |
| `phase` | a shaded band behind the steps with the same phase |
| `owner` | who does it; shown as an avatar |
| `pin` | `yes` puts it in the countdown cards at the top of the roadmap |
| `notes`, `link` | extra detail |

**Settings**: two columns, key and value.

| Key | Meaning |
|---|---|
| `title` | dashboard title (default: "Maya's year") |
| `window_start` | first month of the roadmap, e.g. `2026-10` (default: this month) |
| `window_months` | how many months the roadmap shows, 1–36 (default 12) |
| `sheet_url` | link to the Google Sheet; adds "Open the spreadsheet" links |

**Collections**: one row per extra page in the sidebar. Each page shows the rows of its own tab.

| Column | Meaning |
|---|---|
| `id` | lowercase, e.g. `programs` (required) |
| `name` | page name; `tab` defaults to it |
| `tab` | the tab holding the rows; any columns you like |
| `layout` | `table`, `cards` or `feed` (newest first, like an update log) |
| `title_field` | the column used as each row's title (default: the first column) |
| `status_field`, `statuses` | the status column and its allowed values, e.g. `idea, applied, interview, offer` |
| `date_field` | the date column; if its name contains `deadline`, `due` or `apply`, passed dates are flagged |
| `fields` | columns to show, in order (default: the first five) |
| `group` | sidebar heading |
| `icon` | roadmap, bell, building, document, star, folder, wallet, heart, calendar, list |
| `description`, `empty_text` | page subtitle, and text shown while the tab is empty |
| `order` | number; lower comes first |

Special column names in collection tabs: `fit` or `rating` (0–5) show as a bar of squares;
`who` or `owner` show as an avatar; `link` becomes an "Open" link; in a `feed`, `timeline`
(a Timelines `id`) shows as a colored tag.

Status colors follow the meaning of the word: done/accepted/paid/normal are green,
doing/applied/scheduled/pending are purple, rejected/overdue/missed/high are red.

### Site and CV tabs

**Profile**: two columns, key and value.

| Key | Site | CV |
|---|---|---|
| `name`, `headline`, `location`, `email` | yes | yes |
| `about` | yes | no |
| `phone` | **never** | yes |
| `photo` | file name, e.g. `photo.jpg` (or `Website/photo.jpg` inside the Drive folder) | no |
| `link: <Label>` | a link labelled `<Label>`, e.g. `link: LinkedIn` | the address |
| `sections` | order of the Entries sections, comma-separated | same |
| `site_url` | the site's address, for search engines and link previews | listed |

**Entries**: one row per line of your CV.

| Column | Meaning |
|---|---|
| `section` | e.g. `Education`, `Clinical rotations` |
| `title`, `organization`, `location` | |
| `start`, `end` | shown as typed, e.g. `Sep 2025`, `Present`, `May 2027 (expected)` |
| `summary` | one paragraph |
| `highlights` | one bullet per line; `Label: text` makes the label bold |
| `link` | makes the title a link on the site |

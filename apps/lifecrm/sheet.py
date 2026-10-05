"""Reading the spreadsheet: cell text, dates, rows as dicts. Shared by site, dashboard and CV."""
from __future__ import annotations

import calendar
import re
from datetime import date, datetime

YES = {"yes", "y", "true", "1"}
MONTHS = {name.lower(): i for i, name in enumerate(calendar.month_name) if name}
MONTHS.update({name.lower(): i for i, name in enumerate(calendar.month_abbr) if name})
MONTHS["sept"] = 9


def text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return str(value).strip()


def parse_date(value: object, *, end_of_month: bool = False) -> tuple[str, str] | None:
    """(ISO date, precision 'day'|'month') or None. Accepts sheet dates, YYYY-MM-DD, YYYY-MM and
    'May 2027'. Month-only dates mean the first of the month, or the last with end_of_month.
    Slash dates (05/06/2027) are rejected: day/month and month/day read the same, so a guess
    could silently move an appointment; the caller turns None into a warning."""
    if isinstance(value, datetime):
        return value.date().isoformat(), "day"
    if isinstance(value, date):
        return value.isoformat(), "day"
    s = text(value)
    if not s:
        return None
    try:
        if m := re.fullmatch(r"(\d{4})-(\d{1,2})-(\d{1,2})", s):
            return date(int(m[1]), int(m[2]), int(m[3])).isoformat(), "day"
        year = month = None
        if m := re.fullmatch(r"(\d{4})-(\d{1,2})", s):
            year, month = int(m[1]), int(m[2])
        elif (m := re.fullmatch(r"([A-Za-z]+)\.?\s+(\d{4})", s)) and m[1].lower() in MONTHS:
            year, month = int(m[2]), MONTHS[m[1].lower()]
        if year and month:
            day = calendar.monthrange(year, month)[1] if end_of_month else 1
            return date(year, month, day).isoformat(), "month"
    except ValueError:
        return None
    return None


def header_key(cell: object) -> str:
    """'Highlights (one per line)' -> 'highlights'; 'Due date' -> 'due_date'."""
    return re.sub(r"\s+", "_", text(cell).split("(")[0].strip().lower())


def rows_of(ws) -> list[tuple[int, dict[str, object]]]:
    """(sheet row number, {header: raw value}) for every non-empty row under the header."""
    it = ws.iter_rows(values_only=True)
    keys = [header_key(c) for c in next(it, [])]
    out = []
    for n, row in enumerate(it, start=2):
        item = {k: v for k, v in zip(keys, row) if k}
        if any(text(v) for v in item.values()):
            out.append((n, item))
    return out


def shown(item: dict) -> bool:
    """Rows are shown unless their `show` column says no."""
    return text(item.get("show")).lower() in YES | {""}


def key_values(ws) -> dict[str, str]:
    """A two-column key/value tab (Profile, Settings) as a dict with lowercase keys.

    "link: <Label>" keys keep the label as typed ("link: LinkedIn"), since it is shown.
    """
    out = {}
    for row in ws.iter_rows(min_row=2, values_only=True):
        if len(row) >= 2 and text(row[0]):
            key = text(row[0])
            m = re.match(r"(?i)link\s*[:\s]\s*(.+)", key)
            out[f"link: {m.group(1)}" if m else key.lower()] = text(row[1])
    return out


def tab(wb, name: str):
    """Tab by name, case-insensitive; None if missing."""
    for ws in wb.worksheets:
        if ws.title.strip().lower() == name.lower():
            return ws
    return None

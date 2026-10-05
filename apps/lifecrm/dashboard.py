"""Spreadsheet -> dashboard data (dict, written as JSON into the page).

Tabs read:
  Timelines    one row per life area shown as a lane on the roadmap
  Steps        bars, milestones and tasks inside timelines
  Settings     key/value: title, name, window_start, window_months, sheet_url
  Collections  one row per extra sidebar page (programs, papers, bills, lab results, ...)
  <tab>        one tab per collection, any columns
  Profile      (optional) name, used for the sidebar brand when Settings has no name

Problems in rows never stop the build: they become `warnings`, shown at the bottom of the
dashboard so whoever edits the sheet can fix them.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from .sheet import header_key, key_values, parse_date, rows_of, shown, tab, text

KINDS = {"period", "milestone", "task"}
STATUSES = {"todo", "doing", "done", "to book"}
LAYOUTS = {"table", "cards", "feed"}
COLORS = {"teal", "indigo", "amber", "blue", "pink", "green", "violet", "red", "orange", "gray"}


def _num(s: str, default: float) -> float:
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else default


def convert(wb) -> dict:
    warnings: list[str] = []

    def warn(where: str, row: int, msg: str) -> None:
        warnings.append(f"{where} row {row}: {msg}")

    # ---------- timelines ----------
    timelines, ids = [], set()
    ws = tab(wb, "Timelines")
    for n, r in rows_of(ws) if ws else []:
        if not shown(r):
            continue
        tid, name = text(r.get("id")).lower(), text(r.get("name"))
        if not tid or not name:
            warn("Timelines", n, "needs both an id and a name; skipped")
            continue
        if tid in ids:
            warn("Timelines", n, f"duplicate id '{tid}'; skipped")
            continue
        ids.add(tid)
        color = text(r.get("color")).lower() or "gray"
        if color not in COLORS and not re.fullmatch(r"#?[0-9a-f]{6}", color):
            warn("Timelines", n, f"'{name}': color '{color}' is not one of {', '.join(sorted(COLORS))} or a hex code; using gray")
            color = "gray"
        timelines.append({
            "id": tid, "name": name, "group": text(r.get("group")) or "Other", "color": color,
            "goal": text(r.get("goal")), "description": text(r.get("description")),
            "drive_link": text(r.get("drive_link") or r.get("link")),
            "order": _num(text(r.get("order")), 1e9),
        })
    timelines.sort(key=lambda t: t["order"])

    # ---------- steps ----------
    steps = []
    ws = tab(wb, "Steps")
    for n, r in rows_of(ws) if ws else []:
        if not shown(r):
            continue
        tid, title = text(r.get("timeline")).lower(), text(r.get("title"))
        if not title:
            warn("Steps", n, "has no title; skipped")
            continue
        if tid not in ids:
            warn("Steps", n, f"'{title}': unknown timeline '{tid}'; skipped")
            continue
        kind = text(r.get("kind")).lower() or "task"
        if kind not in KINDS:
            warn("Steps", n, f"'{title}': kind '{kind}' is not period/milestone/task; treated as task")
            kind = "task"
        status = text(r.get("status")).lower() or "todo"
        if status not in STATUSES:
            warn("Steps", n, f"'{title}': status '{status}' is not todo/doing/done/to book; treated as todo")
            status = "todo"
        progress = text(r.get("progress")).rstrip("%")
        step = {
            "timeline": tid, "track": text(r.get("track")) or "General", "title": title, "kind": kind,
            "status": status,
            "progress": max(0, min(100, float(progress))) if re.fullmatch(r"\d+(\.\d+)?", progress) else None,
            "owner": text(r.get("owner")), "phase": text(r.get("phase")),
            "pin": text(r.get("pin")).lower() in {"yes", "y", "true", "1"},
            "notes": text(r.get("notes")), "link": text(r.get("link")), "row": n,
        }

        def field(key: str, **kw):
            raw = r.get(key)
            parsed = parse_date(raw, **kw)
            if text(raw) and parsed is None:
                warn("Steps", n, f"'{title}': cannot read {key} '{text(raw)}' (use YYYY-MM-DD or 'May 2027')")
            return parsed

        if kind == "period":
            start, end = field("start"), field("end", end_of_month=True)
            if start and end and end[0] < start[0]:
                warn("Steps", n, f"'{title}': end is before start; shown as unscheduled")
                start = end = None
            if start and end:
                step.update(start=start[0], end=end[0], approx=start[1] == "month" or end[1] == "month")
            elif start or end:
                warn("Steps", n, f"'{title}': a period needs both start and end; shown as unscheduled")
        else:
            when = field("date") or field("end") or field("start")
            if when:
                step.update(date=when[0], approx=when[1] == "month")
        steps.append(step)

    # ---------- collections (extra sidebar pages) ----------
    collections = []
    ws = tab(wb, "Collections")
    for n, r in rows_of(ws) if ws else []:
        if not shown(r):
            continue
        cid = text(r.get("id")).lower()
        name = text(r.get("name")) or cid.title()
        tab_name = text(r.get("tab")) or name
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", cid):
            warn("Collections", n, f"'{name}': id must be lowercase letters, digits, - or _; skipped")
            continue
        if cid in {c["id"] for c in collections}:
            warn("Collections", n, f"duplicate id '{cid}'; skipped")
            continue
        layout = text(r.get("layout")).lower() or "table"
        if layout not in LAYOUTS:
            warn("Collections", n, f"'{name}': layout '{layout}' is not table/cards/feed; using table")
            layout = "table"
        data_ws = tab(wb, tab_name)
        if data_ws is None:
            warn("Collections", n, f"'{name}': tab '{tab_name}' not found; page shown empty")
        headers = [h for h in (header_key(c) for c in next(data_ws.iter_rows(values_only=True), [])) if h] if data_ws else []
        labels = {header_key(c): text(c) for c in next(data_ws.iter_rows(values_only=True), [])} if data_ws else {}
        title_f = header_key(r.get("title_field")) or (headers[0] if headers else "")
        status_f = header_key(r.get("status_field"))
        date_f = header_key(r.get("date_field"))
        statuses = [s.strip().lower() for s in re.split(r"[|,]", text(r.get("statuses"))) if s.strip()]
        fields = [header_key(f) for f in re.split(r"[|,]", text(r.get("fields"))) if f.strip()]
        for f, what in [(title_f, "title_field"), (status_f, "status_field"), (date_f, "date_field"), *[(f, "fields") for f in fields]]:
            if f and headers and f not in headers:
                warn("Collections", n, f"'{name}': {what} '{f}' is not a column of tab '{tab_name}'")
        if not fields:
            fields = [h for h in headers if h not in {title_f, "show", "link"}][:5]

        items = []
        for m, row in rows_of(data_ws) if data_ws else []:
            if not shown(row):
                continue
            values = {h: text(row.get(h)) for h in headers if h != "show"}
            title = values.get(title_f, "")
            if not title:
                warn(tab_name, m, f"has no {title_f or 'title'}; skipped")
                continue
            item = {"row": m, "title": title, "values": values}
            if status_f:
                st = values.get(status_f, "").lower() or (statuses[0] if statuses else "")
                if statuses and st not in statuses:
                    warn(tab_name, m, f"'{title}': {status_f} '{st}' is not one of {', '.join(statuses)}; treated as {statuses[0]}")
                    st = statuses[0]
                item["status"] = st
            if date_f:
                raw = row.get(date_f)
                parsed = parse_date(raw)
                if text(raw) and parsed is None:
                    warn(tab_name, m, f"'{title}': cannot read {date_f} '{text(raw)}' (use YYYY-MM-DD or 'May 2027')")
                item["date"] = parsed[0] if parsed else ""
                item["approx"] = bool(parsed and parsed[1] == "month")
            if layout == "feed" and values.get("timeline"):
                tl = values["timeline"].lower()
                if tl not in ids:
                    warn(tab_name, m, f"'{title}': unknown timeline '{tl}'")
                    tl = ""
                item["timeline"] = tl
            items.append(item)

        collections.append({
            "id": cid, "name": name, "tab": tab_name, "layout": layout,
            "group": text(r.get("group")) or "Pages", "icon": text(r.get("icon")).lower(),
            "description": text(r.get("description")), "empty": text(r.get("empty_text")),
            "title_field": title_f, "status_field": status_f, "date_field": date_f,
            "statuses": statuses, "fields": fields, "labels": labels, "items": items,
            "order": _num(text(r.get("order")), 1e9 + n),
        })
    collections.sort(key=lambda c: c["order"])

    ws = tab(wb, "Settings")
    settings = key_values(ws) if ws else {}
    profile_ws = tab(wb, "Profile")
    name = settings.get("name") or (key_values(profile_ws) if profile_ws else {}).get("name", "")
    months = settings.get("window_months", "")
    window_start = parse_date(settings.get("window_start", ""))
    first = name.split()[0] if name else ""
    return {
        "synced_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "name": name,
        "title": settings.get("title") or (f"{first}'s year" if first else "My year"),
        "sheet_url": settings.get("sheet_url", ""),
        "settings": {
            "window_start": window_start[0][:7] if window_start else "",
            "window_months": int(months) if months.isdigit() and 1 <= int(months) <= 36 else 12,
        },
        "timelines": [{k: v for k, v in t.items() if k != "order"} for t in timelines],
        "steps": steps,
        "collections": [{k: v for k, v in c.items() if k != "order"} for c in collections],
        "warnings": warnings,
    }

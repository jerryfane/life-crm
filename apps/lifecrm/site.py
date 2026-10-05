"""Spreadsheet (Profile + Entries tabs) -> public one-page site.

Profile (key/value) keys used here:
  name, headline, location, about, email, photo (file name; build.py looks for it next to the
  spreadsheet, pull.py fetches it from the Drive folder, also from a path like "Website/photo.jpg"),
  sections (comma-separated order of Entries sections), site_url,
  link: <Label>  (any number, e.g. "link: LinkedIn" -> URL)
Never shown on the site: phone and any other key not listed above.

Entries columns: show, section, title, organization, location, start, end, summary, highlights, link
(highlights: one bullet per line).
"""
from __future__ import annotations

import shutil
from html import escape
from pathlib import Path

from .sheet import key_values, rows_of, shown, tab, text

ENTRY_FIELDS = ["section", "title", "organization", "location", "start", "end", "summary", "highlights", "link"]


def read_profile(wb) -> dict[str, str]:
    ws = tab(wb, "Profile")
    return key_values(ws) if ws else {}


def read_entries(wb, warnings: list[str]) -> list[dict[str, str]]:
    ws = tab(wb, "Entries")
    out = []
    for n, r in rows_of(ws) if ws else []:
        if not shown(r):
            continue
        item = {f: text(r.get(f)) for f in ENTRY_FIELDS}
        if not item["title"]:
            warnings.append(f"Entries row {n}: has no title; skipped")
            continue
        item["section"] = item["section"] or "Other"
        out.append(item)
    return out


def ordered_sections(profile: dict, entries: list[dict]) -> list[tuple[str, list[dict]]]:
    present: dict[str, list[dict]] = {}
    for e in entries:
        present.setdefault(e["section"], []).append(e)
    wanted = [s.strip() for s in profile.get("sections", "").split(",") if s.strip()]
    order = [s for s in wanted if s in present] + [s for s in present if s not in wanted]
    return [(s, present[s]) for s in order]


def profile_links(profile: dict) -> list[tuple[str, str]]:
    out = []
    for k, v in profile.items():
        if k.startswith("link: ") and v.startswith(("http://", "https://")):
            label = k[6:].strip()
            out.append((label.title() if label.islower() else label, v))
    return out


def e(s: str) -> str:
    return escape(s or "", quote=True)


def _bullet(line: str) -> str:
    # "Surgery: assisted in ..." -> bold label, plain rest.
    label, sep, rest = line.partition(":")
    if sep and 0 < len(label) <= 40 and rest.strip():
        return f"<strong>{e(label)}:</strong> {e(rest.strip())}"
    return e(line)


def _entry(x: dict) -> str:
    when = " – ".join(v for v in (x["start"], x["end"]) if v)
    org = " · ".join(v for v in (x["organization"], x["location"]) if v)
    title = e(x["title"])
    if x["link"].startswith(("http://", "https://")):
        title = f'<a href="{e(x["link"])}" rel="noopener">{title}</a>'
    bullets = "".join(f"<li>{_bullet(ln.strip())}</li>" for ln in x["highlights"].splitlines() if ln.strip())
    return f"""
      <article class="entry">
        <div class="entry-head"><h3>{title}</h3>{f'<span class="when">{e(when)}</span>' if when else ''}</div>
        {f'<p class="org">{e(org)}</p>' if org else ''}
        {f'<p class="summary">{e(x["summary"])}</p>' if x["summary"] else ''}
        {f'<ul>{bullets}</ul>' if bullets else ''}
      </article>"""


def compact_sections(profile: dict) -> set[str]:
    """Profile `compact`: comma-separated Entries sections shown one line per row (e.g. certificates)."""
    return {s.strip().lower() for s in profile.get("compact", "").split(",") if s.strip()}


def one_line(x: dict) -> tuple[str, str, bool]:
    """A row of a compact section as (title, rest, is_label): ("Languages", "English, Italian", True)
    when the row has only a summary, else ("BLS Provider", "Heart Association · Apr 2025", False)."""
    when = " – ".join(v for v in (x["start"], x["end"]) if v)
    rest = " · ".join(v for v in (x["organization"], x["location"], when) if v)
    return (x["title"], rest, False) if rest else (x["title"], x["summary"], bool(x["summary"]))


def _section_body(items: list[dict], compact: bool) -> str:
    if not compact:
        return "".join(_entry(x) for x in items)
    lis = []
    for x in items:
        title, rest, is_label = one_line(x)
        t = e(title)
        if x["link"].startswith(("http://", "https://")):
            t = f'<a href="{e(x["link"])}" rel="noopener">{t}</a>'
        tail = (" " if is_label else " · ") + e(rest) if rest else ""
        lis.append(f"<li><strong>{t}{':' if is_label else ''}</strong>{tail}</li>")
    return f"\n      <ul class=\"plain\">{''.join(lis)}</ul>"


def render(profile: dict, sections: list, has_photo: bool, cv_href: str) -> str:
    name = profile.get("name", "")
    headline = profile.get("headline", "")
    site_url = profile.get("site_url", "").rstrip("/")
    links = []
    if profile.get("email"):
        links.append(f'<a href="mailto:{e(profile["email"])}">Email</a>')
    links += [f'<a href="{e(u)}" rel="noopener">{e(lbl)}</a>' for lbl, u in profile_links(profile)]
    if cv_href:
        links.append(f'<a href="{e(cv_href)}" download>Download CV</a>')
    compact = compact_sections(profile)
    body = "".join(f'\n    <section>\n      <h2>{e(title)}</h2>{_section_body(items, title.lower() in compact)}\n    </section>'
                   for title, items in sections)
    photo = f'<img class="photo" src="photo.jpg" alt="{e(name)}" width="160" height="160">' if has_photo else ""
    og = f'<meta property="og:url" content="{e(site_url)}/">\n<link rel="canonical" href="{e(site_url)}/">' if site_url else ""
    if site_url and has_photo:
        og += f'\n<meta property="og:image" content="{e(site_url)}/photo.jpg">'
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="color-scheme" content="light only">
<title>{e(name)}{' · ' + e(headline) if headline else ''}</title>
<meta name="description" content="{e(profile.get('about') or headline)}">
<meta property="og:type" content="profile">
<meta property="og:title" content="{e(name)}">
<meta property="og:description" content="{e(headline)}">
{og}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="stylesheet" href="style.css">
</head>
<body>
<main>
  <header class="hero">
    {photo}
    <div>
      <h1>{e(name)}</h1>
      {f'<p class="headline">{e(headline)}</p>' if headline else ''}
      {f'<p class="location">{e(profile["location"])}</p>' if profile.get('location') else ''}
      <nav class="links">{''.join(links)}</nav>
    </div>
  </header>
  {f'<p class="about">{e(profile["about"])}</p>' if profile.get('about') else ''}
  {body}
</main>
<footer>© {e(name)}</footer>
</body>
</html>
"""


def favicon(name: str) -> str:
    initials = "".join(w[0] for w in name.split()[:2]).upper() or "★"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><circle cx="32" cy="32" r="32" fill="#1f5f5b"/>'
            f'<text x="32" y="42" font-family="Georgia, serif" font-size="28" font-weight="600" fill="#fbfaf7" text-anchor="middle">{escape(initials)}</text></svg>\n')


def build(wb, sheet_dir: Path, out: Path, static: Path, cv_pdf: Path | None, warnings: list[str]) -> None:
    from PIL import Image, ImageOps

    profile = read_profile(wb)
    sections = ordered_sections(profile, read_entries(wb, warnings))
    shutil.rmtree(out, ignore_errors=True)
    out.mkdir(parents=True)
    for f in ("style.css", "404.html"):
        shutil.copy2(static / f, out / f)
    (out / "favicon.svg").write_text(favicon(profile.get("name", "")))
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\n")

    has_photo = False
    if profile.get("photo"):
        src = sheet_dir / Path(profile["photo"]).name
        if src.is_file():
            with Image.open(src) as img:
                img = ImageOps.exif_transpose(img).convert("RGB")
                ImageOps.fit(img, (640, 640), centering=(0.5, 0.4)).save(out / "photo.jpg", "JPEG", quality=85, optimize=True, progressive=True)
            has_photo = True
        else:
            warnings.append(f"Profile: photo '{profile['photo']}' not found next to the spreadsheet")

    cv_href = ""
    if cv_pdf and cv_pdf.is_file():
        cv_href = (profile.get("name") or "CV").replace(" ", "-") + "-CV.pdf"
        shutil.copy2(cv_pdf, out / cv_href)
    (out / "index.html").write_text(render(profile, sections, has_photo, cv_href))

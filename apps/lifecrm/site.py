"""Spreadsheet (Profile + Entries tabs) -> public one-page site, laid out like a CV: a sticky sidebar
(photo, name, contact buttons, contents with scroll-spy) and one row per entry whose summary and
highlights open on tap. Static files (style.css, site.js, fonts, 404.html) come from apps/site/.

Profile (key/value) keys used here:
  name, headline, location, about, email, photo (file name; build.py looks for it next to the
  spreadsheet, pull.py fetches it from the Drive folder, also from a path like "Website/photo.jpg"),
  sections (comma-separated order of Entries sections), compact (sections shown one line per row),
  site_url, cv_on_site (build.py decides whether a public CV is passed in),
  link: <Label>  (any number, e.g. "link: LinkedIn" -> URL)
Never shown on the site: phone and any other key not listed above.

Entries columns: show, section, title, organization, location, start, end, summary, highlights, link
(highlights: one bullet per line).
"""
from __future__ import annotations

import re
import shutil
from html import escape
from pathlib import Path
from urllib.parse import urlparse

from .sheet import YES, key_values, rows_of, tab, text

ENTRY_FIELDS = ["section", "title", "organization", "location", "start", "end", "summary", "highlights", "link"]


def read_profile(wb) -> dict[str, str]:
    ws = tab(wb, "Profile")
    return key_values(ws) if ws else {}


def read_entries(wb, warnings: list[str]) -> list[dict[str, str]]:
    ws = tab(wb, "Entries")
    out = []
    for n, r in rows_of(ws) if ws else []:
        # Public rows need an explicit yes: a blank `show` cell keeps the row off the site and CV.
        show = text(r.get("show")).lower()
        if show not in YES:
            if not show and text(r.get("title")):
                warnings.append(f"Entries row {n}: '{text(r.get('title'))}': show is empty, so it is hidden; write yes to publish it")
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


def _when(x: dict) -> str:
    return " – ".join(v for v in (x["start"], x["end"]) if v)


def _url(x: dict) -> str:
    return x["link"] if x["link"].startswith(("http://", "https://")) else ""


ICONS = {
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/>',
    "out": '<path d="M7 17 17 7"/><path d="M9 7h8v8"/>',
    "download": '<path d="M12 4v11"/><path d="m7 10 5 5 5-5"/><path d="M5 20h14"/>',
}


def _icon(name: str) -> str:
    return ('<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')


def _entry(x: dict, compact: bool) -> str:
    """One row: title with organization · location under it, dates on the right. Summary, highlights
    and link open on tap (<details>); compact rows and rows with nothing more are static."""
    url = _url(x)
    if compact:
        title, rest, is_label = one_line(x)
        sub, when = (rest, "") if is_label else (" · ".join(v for v in (x["organization"], x["location"]) if v), _when(x))
        body = ""
    else:
        title, when = x["title"], _when(x)
        sub = " · ".join(v for v in (x["organization"], x["location"]) if v)
        bullets = "".join(f"<li>{_bullet(ln.strip())}</li>" for ln in x["highlights"].splitlines() if ln.strip())
        body = (f'<p>{e(x["summary"])}</p>' if x["summary"] else "") + (f"<ul>{bullets}</ul>" if bullets else "")
        if body and url:
            host = (urlparse(url).hostname or url).removeprefix("www.")
            body += f'<p class="lk"><a href="{e(url)}" rel="noopener">{_icon("out")}{e(host)}</a></p>'
    t = f'<a href="{e(url)}" rel="noopener">{e(title)}</a>' if url and not body else e(title)
    o = f' <span class="o">{e(sub)}</span>' if sub else ""
    head = f'<h3 class="et"><span class="t">{t}</span>{o}</h3><span class="d">{e(when)}</span>'
    if body:
        return (f'<details class="e"><summary class="e-r">{head}<span class="pm" aria-hidden="true"></span></summary>'
                f'<div class="e-b">{body}</div></details>')
    return f'<div class="e"><div class="e-r">{head}<span class="pm off" aria-hidden="true"></span></div></div>'


def _section_ids(titles: list[str]) -> list[str]:
    """Anchors for the contents list: "Research & Publications" -> "research-publications", unique."""
    ids: list[str] = []
    for i, t in enumerate(titles, 1):
        sid = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or f"section-{i}"
        ids.append(sid if sid not in ids else f"{sid}-{i}")
    return ids


def compact_sections(profile: dict) -> set[str]:
    """Profile `compact`: comma-separated Entries sections shown one line per row (e.g. certificates)."""
    return {s.strip().lower() for s in profile.get("compact", "").split(",") if s.strip()}


def one_line(x: dict) -> tuple[str, str, bool]:
    """A row of a compact section as (title, rest, is_label): ("Languages", "English, Italian", True)
    when the row has only a summary, else ("BLS Provider", "Heart Association · Apr 2025", False)."""
    when = " – ".join(v for v in (x["start"], x["end"]) if v)
    rest = " · ".join(v for v in (x["organization"], x["location"], when) if v)
    return (x["title"], rest, False) if rest else (x["title"], x["summary"], bool(x["summary"]))


def _button(href: str, icon: str, label: str, attrs: str = "") -> str:
    return f'<a class="btn" href="{e(href)}"{attrs}>{_icon(icon)}<span>{e(label)}</span></a>'


def render(profile: dict, sections: list, has_photo: bool, cv_href: str) -> str:
    name = profile.get("name", "")
    headline = profile.get("headline", "")
    site_url = profile.get("site_url", "").rstrip("/")
    buttons = [_button(f"mailto:{profile['email']}", "mail", "Email")] if profile.get("email") else []
    buttons += [_button(u, "out", lbl, ' rel="noopener"') for lbl, u in profile_links(profile)]
    if cv_href:
        buttons.append(_button(cv_href, "download", "Download CV", " download"))
    compact = compact_sections(profile)
    ids = _section_ids([title for title, _ in sections])
    # Contents: the full section name in the sidebar, its first word in the phone's sideways row.
    toc = "".join(f'<li><a href="#{sid}"><span class="l">{e(title)}</span><span class="m">{e((title.replace("&", " ").split() or [title])[0])}</span>'
                  f'<span class="c">{len(items)}</span></a></li>' for sid, (title, items) in zip(ids, sections))
    body = "".join(f'\n    <section class="sec" id="{sid}"><h2>{e(title)}</h2><div class="es">'
                   + "".join(_entry(x, title.lower() in compact) for x in items) + "</div></section>"
                   for sid, (title, items) in zip(ids, sections))
    photo = f'<img class="photo" src="photo.jpg" alt="{e(name)}" width="120" height="150">' if has_photo else ""
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
<link rel="preload" href="fonts/source-serif-4.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="fonts/source-sans-3.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="style.css">
<script src="site.js" defer></script>
</head>
<body>
<div class="grid">
  <header class="side">
    <div class="me{' ph' if has_photo else ''}">
      {photo}
      <div>
        <h1>{e(name)}</h1>
        {f'<p class="head">{e(headline)}</p>' if headline else ''}
        {f'<p class="loc">{e(profile["location"])}</p>' if profile.get('location') else ''}
      </div>
    </div>
    {f'<nav class="links" aria-label="Contact">{"".join(buttons)}</nav>' if buttons else ''}
    {f'<nav class="toc" aria-label="Sections"><ol>{toc}</ol></nav>' if toc else ''}
  </header>
  <div class="col">
    <main>
    {f'<p class="about">{e(profile["about"])}</p>' if profile.get('about') else ''}{body}
    </main>
    <footer class="foot">© {e(name)}</footer>
  </div>
</div>
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
    for f in ("style.css", "site.js", "404.html"):
        shutil.copy2(static / f, out / f)
    shutil.copytree(static / "fonts", out / "fonts")
    (out / "favicon.svg").write_text(favicon(profile.get("name", "")))
    (out / "robots.txt").write_text("User-agent: *\nAllow: /\n")

    has_photo = False
    if profile.get("photo"):
        src = sheet_dir / Path(profile["photo"]).name
        if src.is_file():
            with Image.open(src) as img:
                img = ImageOps.exif_transpose(img).convert("RGB")
                # A 4:5 portrait, as shown in the sidebar (also the link-preview image).
                ImageOps.fit(img, (480, 600), centering=(0.5, 0.4)).save(out / "photo.jpg", "JPEG", quality=85, optimize=True, progressive=True)
            has_photo = True
        else:
            warnings.append(f"Profile: photo '{profile['photo']}' not found next to the spreadsheet")

    cv_href = ""
    if cv_pdf and cv_pdf.is_file():
        cv_href = (profile.get("name") or "CV").replace(" ", "-") + "-CV.pdf"
        shutil.copy2(cv_pdf, out / cv_href)
    (out / "index.html").write_text(render(profile, sections, has_photo, cv_href))

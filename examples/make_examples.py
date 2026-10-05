#!/usr/bin/env python3
"""Generate the example spreadsheets (career, finance, health). Everything here is fictional.

    python3 examples/make_examples.py      # writes examples/<name>/crm.xlsx (+ career photo)

The career example mirrors a real setup built for a medical student applying to residency,
with every name, school, hospital, supervisor, date and document invented.
"""
from __future__ import annotations

from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill

HERE = Path(__file__).resolve().parent

TIMELINE_COLS = ["id", "name", "group", "color", "goal", "description", "link", "show", "order"]
STEP_COLS = ["timeline", "track", "title", "kind", "start", "end", "date", "status", "progress", "owner", "phase", "pin", "notes", "link", "show"]
COLLECTION_COLS = ["id", "name", "tab", "layout", "title_field", "status_field", "statuses", "date_field", "fields", "group", "icon", "description", "empty_text", "show", "order"]
ENTRY_COLS = ["show", "section", "title", "organization", "location", "start", "end", "summary", "highlights", "link"]


def S(timeline, track, title, kind="task", start="", end="", date="", status="todo", owner="", notes="", phase="", pin="", progress="", link=""):
    """One Steps row in column order."""
    return [timeline, track, title, kind, start, end, date, status, progress, owner, phase, pin, notes, link, "yes"]


def add(wb, name, headers, rows, first=False):
    ws = wb.active if first else wb.create_sheet()
    ws.title = name
    ws.append(headers)
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F5F5B")
    for r in rows:
        ws.append(list(r) + [""] * (len(headers) - len(r)))
    for col in ws.columns:
        ws.column_dimensions[col[0].column_letter].width = 20
        for c in col:
            c.alignment = Alignment(wrap_text=True, vertical="top")
            c.number_format = "@"  # dates stay as typed text; the build parses them
    ws.freeze_panes = "A2"


def save(wb, name):
    out = HERE / name
    out.mkdir(exist_ok=True)
    wb.save(out / "crm.xlsx")
    print(f"wrote {out / 'crm.xlsx'}")


# ======================================================================= career
def career():
    wb = Workbook()
    add(wb, "Profile", ["key", "value"], [
        ["name", "Maya Lindqvist"],
        ["headline", "M.D. Candidate · Coastline University College of Medicine"],
        ["location", "Port Seren"],
        ["about", "Medical student at Coastline University College of Medicine (M.D. expected May 2027) with a B.S. in Biology from Northvale University. Core clerkships in surgery, internal medicine, obstetrics & gynecology, pediatrics, otorhinolaryngology and ophthalmology at Harbor View Teaching Hospital, with clinical electives in emergency medicine and family medicine in the United States. Research experience in clinical biomarkers."],
        ["email", "maya.lindqvist@example.com"],
        ["phone", "+00 555 0100"],
        ["link: LinkedIn", "https://www.linkedin.com/in/example"],
        ["photo", "photo.jpg"],
        ["sections", "Education, Research & Publications, Clinical Rotations & Electives, Work Experience, Teaching, Leadership & Community, Conferences & Continuing Education, Workshops, Certifications"],
        ["site_url", "https://life-crm.jerryfane.com/demo/site"],
        ["compact", "Certifications"],
    ], first=True)

    CL, WK, TE, LC, CO, WS, CE, ED, RE = ("Clinical Rotations & Electives", "Work Experience", "Teaching", "Leadership & Community",
                                          "Conferences & Continuing Education", "Workshops", "Certifications", "Education", "Research & Publications")
    add(wb, "Entries", ENTRY_COLS, [
        ["yes", ED, "Doctor of Medicine (M.D.)", "Coastline University College of Medicine", "Port Seren", "2023", "May 2027 (expected)", "", "", ""],
        ["yes", ED, "Bachelor of Science, Biology", "Northvale University", "Northvale", "2017", "2021", "", "", ""],
        ["yes", RE, "Serum vitamin D and recovery after appendectomy: a retrospective study", "Coastline University · 140 cases", "", "2025", "", "Supervisors: Dr. Ines Navarro, Dr. Tom Akers. Completed research project.", "", ""],
        ["yes", RE, "Accuracy of a rapid troponin test in the emergency department", "Harbor View Teaching Hospital · 410 records", "", "2025", "", "Supervisors: Prof. Laila Haddad, Dr. Sam Okafor. Completed research project.", "", ""],
        ["yes", CL, "Core Clinical Clerkships", "Coastline University · Harbor View Teaching Hospital and affiliated hospitals", "Port Seren", "Sep 2025", "Present",
         "History-taking and full physical examinations in ambulatory and inpatient settings, with supervised hands-on care across the core specialties.",
         "Surgery II (in progress): orthopedics at Eastgate General and urology at St. Brendan Medical Center, Aug–Oct 2026\n"
         "Pediatrics: Harbor View and Lakeside Children's Hospital, May–Jun 2026; growth and development, age-appropriate examination\n"
         "Internal Medicine: Harbor View Teaching Hospital, Feb–Jun 2026; differential diagnoses and management plans\n"
         "Ophthalmology: Jan–Feb 2026; eye examination and common ocular conditions\n"
         "Otorhinolaryngology: Dec 2025–Jan 2026; head and neck examination\n"
         "Obstetrics & Gynecology: Oct–Dec 2025; common obstetric and gynecologic conditions\n"
         "Surgery I: Sep–Oct 2025; peri-operative, operative and postoperative care", ""],
        ["yes", CL, "Family Medicine Clinical Elective", "Pacific Shore Health Center", "California, USA", "Aug 2026", "",
         "", "Saw patients independently, then presented history, examination and plan to the attending physician\nReviewed medications and current complaints with head-to-toe examinations\nApplied current guidelines for primary and secondary prevention", ""],
        ["yes", CL, "Emergency Medicine Clinical Elective", "Bayside Community Hospital", "Florida, USA", "Jul 2026", "",
         "Community emergency department with direct patient care under attending supervision.",
         "Took full histories and performed complete physical examinations\nSutured, splinted, placed and removed IV lines; assisted with stabilization\nPerformed a paracentesis under supervision and observed a CT-guided aspiration\nPresented at weekly grand rounds", ""],
        ["yes", WK, "Medical Scribe", "Westline Clinics", "Northvale", "Oct 2021", "Feb 2023", "", "Documented about 10 patient visits a day in real time\nUpdated histories, medications and plans for the provider", ""],
        ["yes", WK, "Patient Care Assistant, ICU", "Northvale General Hospital", "Northvale", "Mar 2022", "Feb 2023", "", "Supported ICU nurses with daily patient care and transport\nAssisted the team during emergencies", ""],
        ["yes", TE, "Anatomy Lab Teaching Assistant", "Northvale University", "Northvale", "Jan 2021", "Jun 2021", "", "Taught weekly anatomy labs and ran exam reviews", ""],
        ["yes", LC, "Organizer, Heart Health Awareness Day", "Coastline University College of Medicine", "Port Seren", "Feb 2025", "", "", "Received a certificate of appreciation", ""],
        ["yes", CO, "Regional Cardiology Update", "Attendee", "Port Seren", "Mar 2024", "", "", "6 CME hours", ""],
        ["yes", CO, "Annual Endocrinology Congress", "Attendee", "Port Seren", "Feb 2026", "", "", "18 CPD points", ""],
        ["yes", WS, "Basic Surgical Skills Workshop", "Coastline University Simulation Center", "Port Seren", "Nov 2023", "", "", "", ""],
        ["yes", CE, "Basic Life Support (BLS) Provider", "Heart Association", "", "Apr 2025", "", "", "", ""],
        ["yes", CE, "Good Clinical Practice (GCP)", "Clinical Trials Network", "", "Feb 2024", "", "", "", ""],
    ])

    add(wb, "Timelines", TIMELINE_COLS, [
        ["school", "Medical school", "Medical school", "teal", "M.D., May 2027", "Rotations at Harbor View Teaching Hospital and affiliates. Each rotation: 4 case studies, an ethics review and an evidence-based medicine assignment.", "", "yes", 1],
        ["research", "Research & papers", "Career", "indigo", "At least 2 papers by the end of 2026", "Fastest routes: case reports, meta-analyses, audits. A professor supervises and signs.", "", "yes", 2],
        ["residency", "Residency 2027", "Career", "amber", "Apply in September 2027", "Programs in the USA and Europe: share of international graduates, requirements, deadlines.", "", "yes", 3],
        ["cv", "CV & portfolio", "Career", "blue", "CV and public page always up to date", "The CV and the public page come from the Profile and Entries tabs.", "", "yes", 4],
        ["boost", "CV boosters", "Career", "pink", "One experience outside university in December–January", "", "", "yes", 5],
        ["health", "Health", "Personal", "green", "Book the pending appointments", "Short titles only; details stay in the calendar.", "", "yes", 6],
        ["study", "Study", "Personal", "violet", "Study while commuting", "Downloadable study podcasts.", "", "yes", 7],
    ])

    add(wb, "Steps", STEP_COLS, [
        S("school", "Rotations", "Surgery I", "period", "2025-09-01", "2025-10-24", status="done", owner="Maya"),
        S("school", "Rotations", "Obstetrics & Gynecology", "period", "2025-10-27", "2025-12-19", status="done", owner="Maya"),
        S("school", "Rotations", "ENT", "period", "2025-12-22", "2026-01-16", status="done", owner="Maya"),
        S("school", "Rotations", "Ophthalmology", "period", "2026-01-19", "2026-02-13", status="done", owner="Maya"),
        S("school", "Rotations", "Internal Medicine I", "period", "2026-02-23", "Jun 2026", status="done", owner="Maya"),
        S("school", "Rotations", "Pediatrics", "period", "2026-05-04", "2026-06-19", status="done", owner="Maya"),
        S("school", "Electives", "Emergency Medicine elective, Florida", "period", "2026-07-01", "2026-07-31", status="done", owner="Maya", notes="Bayside Community Hospital; supervisor Dr. Grant"),
        S("school", "Electives", "Family Medicine elective, California", "period", "2026-08-01", "2026-08-31", status="done", owner="Maya", notes="Pacific Shore Health Center; supervisor Dr. Chen"),
        S("school", "Rotations", "Surgery II: Orthopedics", "period", "2026-08-31", "2026-09-25", status="done", owner="Maya"),
        S("school", "Rotations", "Surgery II: Urology", "period", "2026-09-28", "2026-10-23", status="doing", owner="Maya"),
        S("school", "Rotations", "Internal Medicine II", "period", "2026-10-26", "2026-12-18", owner="Maya"),
        S("school", "Rotations", "Psychiatry", "period", "2027-01-11", "2027-02-26", owner="Maya"),
        *[S("school", "Surgery II assignments", t, date="2026-10-13", owner="Maya", status="done" if t == "Case study 1" else "todo") for t in
          ["Case study 1", "Case study 2", "Case study 3", "Case study 4", "Ethics review", "Evidence-based medicine"]],
        S("school", "Surgery II assignments", "Surgery II exams", "milestone", date="2026-10-22", owner="Maya"),
        S("school", "Graduation", "M.D. graduation", "milestone", date="May 2027", owner="Maya", pin="yes"),
        S("research", "Goal", "2 papers", "milestone", date="2026-12-31", owner="Maya", pin="yes"),
        S("research", "Completed projects", "Vitamin D project: final report submitted", "milestone", date="2025-04-22", status="done", owner="Maya"),
        S("research", "Paper 1", "Write up the vitamin D project", "period", "2026-10-12", "2026-12-15", status="doing", progress=15, owner="Maya", phase="Write"),
        S("research", "Paper 1", "Ask Dr. Navarro to supervise and sign", date="2026-10-16", owner="Maya", phase="Plan"),
        S("research", "Paper 1", "Abstract to the regional conference", "milestone", date="2026-11-14", owner="Maya", phase="Present"),
        S("research", "Paper 2", "Choose a case report from Surgery II", owner="Maya", phase="Plan"),
        S("residency", "Program research", "Program list: USA and Europe", "period", "2026-10-05", "2026-12-20", status="doing", progress=40, owner="Assistant"),
        S("residency", "Letters", "Dr. Grant and Dr. Chen agreed to write letters", "milestone", date="2026-10-04", status="done", owner="Maya", notes="Letters go straight to the application service; she never sees them."),
        S("residency", "Exams", "Book the licensing exam", owner="Maya"),
        S("residency", "Applications", "Submit residency applications", "milestone", date="Sep 2027", owner="Maya", pin="yes"),
        S("cv", "Website", "Public page live", "milestone", date="2026-10-04", status="done"),
        S("cv", "CV", "Add the two US electives to the CV", date="2026-10-04", status="done", owner="Maya"),
        S("cv", "CV", "Confirm the endoscopy workshop year", owner="Maya"),
        S("boost", "December–January", "Experience outside university", "period", "2026-12-01", "2027-01-31", owner="Maya", notes="To choose from the Boosters page"),
        S("boost", "December–January", "Apply to the chosen option", date="2026-10-30", owner="Maya"),
        S("health", "Appointments", "Dentist", status="to book", owner="Maya"),
        S("health", "Appointments", "Follow-up visit", status="to book", owner="Maya"),
        S("study", "Podcasts", "Set up downloadable study podcasts", owner="Assistant"),
    ])

    add(wb, "Settings", ["key", "value", "meaning"], [
        ["title", "Maya's year", "Dashboard title"],
        ["window_start", "", "First month shown (YYYY-MM). Empty = this month."],
        ["window_months", "12", "Months on the roadmap"],
        ["sheet_url", "", "Link to this spreadsheet in Google Drive (adds 'Edit' buttons)"],
    ])

    add(wb, "Collections", COLLECTION_COLS, [
        ["updates", "Updates", "Updates", "feed", "title", "", "", "date", "who, timeline, text, link", "Overview", "bell", "What was finished, newest first", "", "yes", 1],
        ["programs", "Residency", "Programs", "table", "program", "status", "shortlisted, applied, researching, rejected", "deadline",
         "country, specialty, intl_grads, deadline, fit", "Work", "building", "USA and Europe · applications September 2027", "", "yes", 2],
        ["papers", "Papers", "Papers", "cards", "title", "status", "writing, picked, submitted, accepted, published, proposed, idea, dropped", "",
         "type, effort, summary", "Work", "document", "Goal: at least 2 by the end of 2026", "", "yes", 3],
        ["boosters", "CV boosters", "Boosters", "table", "option", "status", "shortlisted, applied, accepted, found, rejected", "deadline",
         "where, type, cost, deadline, why", "Work", "star", "December–January options", "", "yes", 4],
    ])
    add(wb, "Updates", ["title", "date", "who", "timeline", "text", "link", "show"], [
        ["Program list started: 9 programs, 3 shortlisted", "2026-10-05", "Assistant", "residency", "Internal and family medicine programs that take many international graduates fit best. Main gap: the licensing exam.", "", "yes"],
        ["Dr. Grant and Dr. Chen agreed to write letters", "2026-10-04", "Maya", "residency", "They will upload them to the application service once she sends the request forms.", "", "yes"],
        ["CV updated with both US electives", "2026-10-04", "Engine", "cv", "The public page and the CV PDF show the same content.", "", "yes"],
        ["Rotation dates added to the roadmap", "2026-10-03", "Assistant", "school", "From the group schedule and school emails.", "", "yes"],
    ])
    add(wb, "Programs", ["program", "country", "city", "specialty", "intl_grads", "visa", "exams", "grad_limit", "deadline", "fit", "status", "why", "gap", "link", "show"], [
        ["Lakeshore University Hospital", "USA", "Chicago", "Internal Medicine", "35%", "J-1", "Step 2 CK", "Within 5 years", "Sep 2027", "4", "shortlisted", "Takes many international graduates; values US electives.", "Licensing exam score", "", "yes"],
        ["Bayside Family Medicine Program", "USA", "Tampa", "Family Medicine", "40%", "J-1", "Step 2 CK", "Within 3 years", "Sep 2027", "4", "shortlisted", "Same region as her emergency elective; family medicine like her California elective.", "Licensing exam", "", "yes"],
        ["Riverside Community Program", "USA", "Sacramento", "Family Medicine", "15%", "J-1", "Step 2 CK ≥ 230", "Within 3 years", "Sep 2027", "3", "shortlisted", "Dr. Chen's letter is relevant here.", "One more US letter", "", "yes"],
        ["Northgate Teaching Hospital", "UK", "Leeds", "Foundation Programme", "open", "Skilled worker", "PLAB 1 and 2", "", "Oct 2027", "3", "researching", "Open to international graduates who pass PLAB.", "UK registration", "", "yes"],
        ["Hospital Costa Clara", "Spain", "Valencia", "Family Medicine", "exam", "EU", "MIR exam", "", "Jul 2027", "2", "researching", "Entry by national exam ranking.", "Degree recognition", "", "yes"],
        ["Metro Surgical Program", "USA", "Houston", "General Surgery", "2%", "H-1B", "Step 2 CK ≥ 250", "Within 1 year", "Sep 2027", "1", "rejected", "Very competitive; rarely takes international graduates.", "Research output, scores", "", "yes"],
    ])
    add(wb, "Papers", ["title", "type", "status", "effort", "supervisor", "owner", "summary", "link", "show"], [
        ["Vitamin D and recovery after appendectomy", "Original article", "writing", "Low · 6 weeks", "Dr. Ines Navarro", "Maya", "Write up the finished 140-case study with its supervisors.", "", "yes"],
        ["An unusual case from the urology rotation", "Case report", "proposed", "Low · 4 weeks", "", "Maya", "Needs one case with consent and a supervising consultant.", "", "yes"],
        ["Topic in her likely specialty", "Meta-analysis", "idea", "High · 3–4 months", "", "Assistant", "Strongest for the application but slowest; start after paper 1.", "", "yes"],
    ])
    add(wb, "Boosters", ["option", "where", "type", "cost", "deadline", "status", "why", "link", "show"], [
        ["Research observership in cardiology", "USA · Boston", "Research", "$2,500", "2026-10-30", "shortlisted", "Can lead to an abstract and another US letter.", "", "yes"],
        ["Internal medicine observership", "USA · Chicago", "Clinical", "$3,800", "2026-11-10", "found", "Hands-on US experience at a hospital on her program list.", "", "yes"],
        ["Hospital elective", "Port Seren", "Clinical", "Free", "2026-11-15", "found", "No visa needed; fits around school.", "", "yes"],
        ["Remote research project", "Remote", "Research", "Free", "", "found", "Applications any time; could become paper 2.", "", "yes"],
    ])
    save(wb, "career")
    photo(HERE / "career" / "photo.jpg", "ML")


def photo(path: Path, initials: str):
    """An illustrated placeholder portrait (not a real person)."""
    from PIL import Image, ImageDraw, ImageFont
    img = Image.new("RGB", (640, 640), "#e6f1ef")
    d = ImageDraw.Draw(img)
    d.ellipse((200, 120, 440, 360), fill="#1f5f5b")
    d.rounded_rectangle((110, 380, 530, 760), radius=200, fill="#1f5f5b")
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 84)
    except OSError:
        font = ImageFont.load_default()
    d.text((320, 240), initials, fill="#e6f1ef", font=font, anchor="mm")
    img.save(path, quality=88)


# ======================================================================= finance
def finance():
    wb = Workbook()
    add(wb, "Timelines", TIMELINE_COLS, [
        ["debt", "Pay off the car loan", "Money", "red", "Car loan paid by March 2027", "", "", "yes", 1],
        ["savings", "Emergency fund", "Money", "green", "6 months of expenses saved", "", "", "yes", 2],
        ["taxes", "Taxes", "Admin", "amber", "File on time, no surprises", "", "", "yes", 3],
        ["home", "Moving out", "Life", "blue", "Own apartment by summer 2027", "", "", "yes", 4],
    ], first=True)
    add(wb, "Steps", STEP_COLS, [
        S("debt", "Loan", "Car loan payoff", "period", "2026-06-01", "2027-03-31", status="doing", progress=55),
        S("debt", "Loan", "Extra payment", date="2026-11-01"),
        S("savings", "Fund", "Reach 3 months of expenses", "milestone", date="2026-12-31", pin="yes"),
        S("savings", "Fund", "Reach 6 months of expenses", "milestone", date="Jun 2027"),
        S("taxes", "Filing", "Collect receipts", "period", "2027-01-05", "2027-02-28"),
        S("taxes", "Filing", "Tax return due", "milestone", date="2027-04-15", pin="yes"),
        S("home", "Search", "Apartment search", "period", "2027-03-01", "2027-06-30"),
        S("home", "Search", "Decide the budget", date="2026-11-20"),
    ])
    add(wb, "Settings", ["key", "value"], [["title", "My money"], ["window_months", "12"]])
    add(wb, "Collections", COLLECTION_COLS, [
        ["bills", "Bills", "Bills", "table", "bill", "status", "overdue, due, scheduled, paid", "due", "amount, due, account, status", "Money", "calendar", "Monthly and yearly bills", "", "yes", 1],
        ["accounts", "Accounts", "Accounts", "table", "account", "", "", "", "type, balance, updated", "Money", "wallet", "Balances, updated by hand", "", "yes", 2],
        ["goals", "Goals", "Goals", "cards", "goal", "status", "doing, todo, done", "", "target, saved, notes", "Plans", "star", "", "", "yes", 3],
    ])
    add(wb, "Bills", ["bill", "amount", "due", "account", "status", "show"], [
        ["Rent", "950", "2026-11-01", "Checking", "scheduled", "yes"],
        ["Phone", "35", "2026-10-12", "Credit card", "due", "yes"],
        ["Car insurance", "420", "2026-10-02", "Checking", "overdue", "yes"],
        ["Internet", "40", "2026-10-20", "Credit card", "paid", "yes"],
    ])
    add(wb, "Accounts", ["account", "type", "balance", "updated", "show"], [
        ["Checking", "Bank", "2,140", "2026-10-01", "yes"],
        ["Savings", "Bank", "6,300", "2026-10-01", "yes"],
        ["Car loan", "Loan", "-4,800", "2026-10-01", "yes"],
    ])
    add(wb, "Goals", ["goal", "target", "saved", "status", "notes", "show"], [
        ["Emergency fund", "12,000", "6,300", "doing", "Automatic transfer on payday", "yes"],
        ["Apartment deposit", "3,000", "0", "todo", "Start after the car loan", "yes"],
    ])
    save(wb, "finance")


# ======================================================================= health
def health():
    wb = Workbook()
    add(wb, "Timelines", TIMELINE_COLS, [
        ["checkups", "Check-ups", "Care", "green", "All yearly check-ups done", "", "", "yes", 1],
        ["fitness", "Fitness", "Habits", "orange", "Run a 10 km race in spring", "", "", "yes", 2],
        ["sleep", "Sleep", "Habits", "violet", "7 hours on weeknights", "", "", "yes", 3],
    ], first=True)
    add(wb, "Steps", STEP_COLS, [
        S("checkups", "Visits", "Dentist", date="2026-10-21"),
        S("checkups", "Visits", "Eye exam", status="to book"),
        S("checkups", "Visits", "Blood test", date="2026-11-05"),
        S("fitness", "Training", "10 km training plan", "period", "2026-11-01", "2027-03-28", status="doing", progress=10),
        S("fitness", "Training", "10 km race", "milestone", date="2027-03-28", pin="yes"),
        S("sleep", "Habit", "No screens after 23:00", "period", "2026-10-01", "2026-12-31", status="doing"),
    ])
    add(wb, "Settings", ["key", "value"], [["title", "My health"], ["window_months", "9"]])
    add(wb, "Collections", COLLECTION_COLS, [
        ["appointments", "Appointments", "Appointments", "table", "appointment", "status", "to book, booked, done", "date", "with, date, status", "Care", "calendar", "", "", "yes", 1],
        ["results", "Results", "Results", "table", "test", "status", "high, low, normal", "date", "value, range, date, status", "Care", "heart", "Lab results", "", "yes", 2],
    ])
    add(wb, "Appointments", ["appointment", "with", "date", "status", "show"], [
        ["Dentist", "Dr. Ruiz", "2026-10-21", "booked", "yes"], ["Eye exam", "", "", "to book", "yes"], ["Blood test", "Lab", "2026-11-05", "booked", "yes"],
    ])
    add(wb, "Results", ["test", "value", "range", "date", "status", "show"], [
        ["Vitamin D", "22 ng/mL", "30–100", "2026-04-10", "low", "yes"], ["Cholesterol", "180 mg/dL", "< 200", "2026-04-10", "normal", "yes"],
    ])
    save(wb, "health")


if __name__ == "__main__":
    career()
    finance()
    health()

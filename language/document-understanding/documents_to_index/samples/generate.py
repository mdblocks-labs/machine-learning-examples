# /// script
# requires-python = "==3.13.*"
# dependencies = ["reportlab==4.4.4", "python-docx==1.2.0", "pillow==12.0.0"]
# ///
"""Write the synthetic sample documents in `documents/` and `extra/`.

The company and everything it says are invented. The two Word files and the
encrypted PDF aren't committed, since the Hub refuses binary files; run this
before the samples preset, from the repository root:

    uv run language/document-understanding/documents_to_index/samples/generate.py

The output is the same on every run.

Five files can be read: a PDF handbook, a Word onboarding guide, a saved web
page, Markdown and plain text. Four can't: an encrypted PDF, a truncated Word
file, a scan with no text layer and a text file that isn't UTF-8. The handbook
also has a page with no text layer. `extra/` holds one more file, for adding to
the folder to see that only it is embedded.
"""

import io
import random
import zipfile
from pathlib import Path

from docx import Document
from PIL import Image, ImageDraw
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas

HERE = Path(__file__).parent
OUT = HERE / "documents"
EXTRA = HERE / "extra"
COMPANY = "Lumen Tea Company"

HANDBOOK = [
    ("Welcome", [
        f"Welcome to {COMPANY}. This handbook explains how we work, what we offer and what we "
        "expect. It applies to every employee in every office, and it is reviewed each January.",
        "Our tea is sourced from small farms in Assam, Darjeeling and Yunnan. We visit each farm "
        "at least once a year and publish what we pay growers in our annual report.",
    ]),
    ("Working hours", [
        "The core hours are ten to four, Monday to Friday. Outside them, plan your day with your "
        "team. Part-time schedules are agreed with your manager and written into your contract.",
        "Overtime is paid at one and a half times the hourly rate, or taken as time off within "
        "three months, whichever you prefer.",
    ]),
    ("Vacation and leave", [
        "Full-time employees get 25 vacation days a year, plus public holidays. Vacation accrues "
        "monthly, and up to five unused days carry over to the next year. Part-time employees get "
        "a share in proportion to their hours.",
        "Sick leave is paid from the first day. After three days in a row, send a note from a "
        "doctor to People Operations. Parental leave is 20 weeks at full pay for every parent.",
    ]),
]

ONBOARDING = [
    ("Your first week", ["Your manager meets you at reception at nine on your first day.",
                         "You get a laptop, a badge and a tasting kit."]),
    ("Accounts", ["IT creates your email and chat accounts before you arrive. "
                  "Set up two-factor authentication on the first morning."]),
]

EXPENSES = f"""<!doctype html>
<html><head><title>Expense policy | {COMPANY}</title>
<style>body {{ font-family: serif; }}</style>
<script>console.log("tracking");</script></head>
<body>
<header><a href="/">Home</a> | <a href="/policies">Policies</a></header>
<nav><ul><li>Benefits</li><li>Expenses</li><li>Travel</li></ul></nav>
<main>
<h1>Expense policy</h1>
<p>Claim business expenses within 30 days, with a receipt for anything over 25 euros.</p>
<h2>Meals</h2>
<p>Meals while travelling are covered up to 60 euros a day. Alcohol is not reimbursed.</p>
<h2>Equipment</h2>
<ul><li>Monitors and chairs: up to 400 euros, once every three years.</li>
<li>Headsets: up to 120 euros.</li></ul>
</main>
<footer>&copy; 2026 {COMPANY}</footer>
</body></html>
"""

FAQ = """# IT questions

## How do I reset my password?

Open the account portal and choose **Forgot password**. The link in the email
works for 15 minutes.

## How do I connect to the office printer?

Run the setup script from a terminal:

```sh
# installs the driver and adds the printer
./printer-setup.sh --office berlin
```

## Who do I ask for help?

Write in the #it-help channel. Someone answers within an hour on working days.
"""

NOTES = """Team meeting, 3 November 2026

Present: Ana, Bilal, Chen, Dara.

The autumn blend launches on 1 December. Bilal confirms the packaging order.
Chen will draft the tasting notes by Friday.
Next meeting: 17 November.
"""

TRAVEL = """# Travel policy

Book trains for journeys under six hours, and economy flights otherwise.
Hotels are covered up to 150 euros a night in capital cities and 110 elsewhere.
"""


def handbook(path):
    page = canvas.Canvas(str(path), pagesize=A4, invariant=1)
    for sections in (HANDBOOK[:2], HANDBOOK[2:]):
        y = 790
        for heading, paragraphs in sections:
            page.setFont("Helvetica-Bold", 14)
            page.drawString(60, y, heading)
            y -= 24
            page.setFont("Helvetica", 11)
            for paragraph in paragraphs:
                for line in wrap(paragraph, 88):
                    page.drawString(60, y, line)
                    y -= 15
                y -= 10
            y -= 12
        page.showPage()
    # A signed form, scanned: an image with no text layer.
    page.drawImage(ImageReader(scan("Signed: acknowledgement of the handbook")), 60, 400, 470, 300)
    page.showPage()
    page.save()


def scanned_receipt(path):
    page = canvas.Canvas(str(path), pagesize=A4, invariant=1)
    page.drawImage(ImageReader(scan("Receipt: 3 x Darjeeling, 42.00 EUR")), 60, 400, 470, 300)
    page.showPage()
    page.save()


def locked(path):
    page = canvas.Canvas(str(path), pagesize=A4, invariant=1, encrypt="lumen-2026")
    page.drawString(60, 790, "Salary bands, 2027")
    page.showPage()
    page.save()


def scan(text):
    rng = random.Random(text)
    image = Image.new("L", (940, 600), 245)
    draw = ImageDraw.Draw(image)
    draw.text((40, 280), text, fill=30)
    for _ in range(4000):
        image.putpixel((rng.randrange(940), rng.randrange(600)), rng.randrange(150, 255))
    buffer = io.BytesIO()
    image.save(buffer, "PNG")
    buffer.seek(0)
    return buffer


def onboarding(path):
    document = Document()
    document.core_properties.author = COMPANY
    document.add_heading("Onboarding guide", 1)
    for heading, paragraphs in ONBOARDING:
        document.add_heading(heading, 2)
        for paragraph in paragraphs:
            document.add_paragraph(paragraph)
    document.add_heading("Checklist", 2)
    for item in ["Sign your contract", "Read the handbook", "Book your welcome tasting"]:
        document.add_paragraph(item, style="List Bullet")
    table = document.add_table(rows=1, cols=2)
    table.rows[0].cells[0].text, table.rows[0].cells[1].text = "Team", "Contact"
    for team, contact in [("People Operations", "people@example.com"), ("IT", "it@example.com")]:
        row = table.add_row()
        row.cells[0].text, row.cells[1].text = team, contact
    buffer = io.BytesIO()
    document.save(buffer)
    path.write_bytes(fixed_zip(buffer.getvalue()))


def fixed_zip(data):
    """The same archive with fixed timestamps, so the file is the same on every run."""
    out = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(data)) as source, zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as target:
        for info in source.infolist():
            fixed = zipfile.ZipInfo(info.filename, (2026, 11, 1, 0, 0, 0))
            fixed.compress_type = zipfile.ZIP_DEFLATED
            target.writestr(fixed, source.read(info))
    return out.getvalue()


def wrap(text, width):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def main():
    for folder in (OUT, EXTRA):
        folder.mkdir(exist_ok=True)
    handbook(OUT / "01-handbook.pdf")
    onboarding(OUT / "02-onboarding.docx")
    (OUT / "03-expense-policy.html").write_text(EXPENSES)
    (OUT / "04-it-faq.md").write_text(FAQ)
    (OUT / "05-meeting-notes.txt").write_text(NOTES)
    locked(OUT / "06-salary-bands.pdf")
    (OUT / "07-broken.docx").write_bytes((OUT / "02-onboarding.docx").read_bytes()[:400])
    scanned_receipt(OUT / "08-scanned-receipt.pdf")
    (OUT / "09-old-notes.txt").write_bytes("Notes from the café tasting, 2019.\n".encode("cp1252"))
    (EXTRA / "10-travel-policy.md").write_text(TRAVEL)


if __name__ == "__main__":
    main()

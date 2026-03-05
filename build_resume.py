"""
build_resume.py
Pure Python resume + cover letter PDF generator using ReportLab.
No Node.js, no Word, no external tools needed.
Works on PythonAnywhere and any cloud environment.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
import os

# ── COLORS ──────────────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1F3864")
MID_BLUE   = colors.HexColor("#2E5090")
TEXT_COLOR = colors.HexColor("#1A1A1A")
GRAY       = colors.HexColor("#555555")
LIGHT_GRAY = colors.HexColor("#F2F2F2")

# ── STYLES ───────────────────────────────────────────────────────────────────
def get_styles():
    return {
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=24,
            textColor=DARK_BLUE,
            alignment=TA_CENTER,
            spaceAfter=4
        ),
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=10,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=8
        ),
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=11,
            textColor=DARK_BLUE,
            spaceBefore=12,
            spaceAfter=4
        ),
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            textColor=TEXT_COLOR,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
            leading=14
        ),
        "job_title": ParagraphStyle(
            "job_title",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=DARK_BLUE,
            spaceBefore=8,
            spaceAfter=2
        ),
        "company": ParagraphStyle(
            "company",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=MID_BLUE,
            spaceAfter=4
        ),
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=10,
            textColor=TEXT_COLOR,
            leftIndent=16,
            firstLineIndent=-10,
            spaceAfter=3,
            leading=13
        ),
        "skill": ParagraphStyle(
            "skill",
            fontName="Helvetica",
            fontSize=10,
            textColor=TEXT_COLOR,
            leftIndent=16,
            firstLineIndent=-10,
            spaceAfter=2,
            leading=13
        ),
        "meta": ParagraphStyle(
            "meta",
            fontName="Helvetica",
            fontSize=10,
            textColor=GRAY,
            spaceAfter=2
        ),
        "cl_body": ParagraphStyle(
            "cl_body",
            fontName="Helvetica",
            fontSize=11,
            textColor=TEXT_COLOR,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16
        ),
    }


def section_divider():
    return HRFlowable(
        width="100%",
        thickness=1.5,
        color=MID_BLUE,
        spaceAfter=6
    )


def build_resume_pdf(data: dict, output_path: str):
    """Generate a professional resume PDF from resume data dict"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch
    )

    S = get_styles()
    story = []

    # ── NAME ──
    story.append(Paragraph(data["name"], S["name"]))

    # ── CONTACT ──
    story.append(Paragraph(data["contact"], S["contact"]))
    story.append(HRFlowable(width="100%", thickness=2, color=MID_BLUE, spaceAfter=8))

    # ── SUMMARY ──
    story.append(Paragraph("PROFESSIONAL SUMMARY", S["section"]))
    story.append(section_divider())
    story.append(Paragraph(data["summary"], S["body"]))

    # ── KEY SKILLS (2 columns) ──
    story.append(Paragraph("KEY SKILLS", S["section"]))
    story.append(section_divider())

    skills = data["skills"]
    half = (len(skills) + 1) // 2
    left_skills  = skills[:half]
    right_skills = skills[half:]

    skill_rows = []
    max_rows = max(len(left_skills), len(right_skills))
    for i in range(max_rows):
        left  = f"• {left_skills[i]}"  if i < len(left_skills)  else ""
        right = f"• {right_skills[i]}" if i < len(right_skills) else ""
        skill_rows.append([
            Paragraph(left,  S["skill"]),
            Paragraph(right, S["skill"])
        ])

    skill_table = Table(skill_rows, colWidths=[3.6 * inch, 3.6 * inch])
    skill_table.setStyle(TableStyle([
        ("VALIGN",     (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING",  (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING",   (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 1),
    ]))
    story.append(skill_table)

    # ── CERTIFICATIONS ──
    story.append(Spacer(1, 6))
    story.append(Paragraph("CERTIFICATIONS", S["section"]))
    story.append(section_divider())

    certs = data["certifications"]
    chalf = (len(certs) + 1) // 2
    left_certs  = certs[:chalf]
    right_certs = certs[chalf:]

    cert_rows = []
    for i in range(max(len(left_certs), len(right_certs))):
        left  = f"• {left_certs[i]}"  if i < len(left_certs)  else ""
        right = f"• {right_certs[i]}" if i < len(right_certs) else ""
        cert_rows.append([
            Paragraph(left,  S["skill"]),
            Paragraph(right, S["skill"])
        ])

    cert_table = Table(cert_rows, colWidths=[3.6 * inch, 3.6 * inch])
    cert_table.setStyle(TableStyle([
        ("VALIGN",      (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",(0, 0), (-1, -1), 4),
        ("TOPPADDING",  (0, 0), (-1, -1), 1),
        ("BOTTOMPADDING",(0,0), (-1, -1), 1),
    ]))
    story.append(cert_table)

    # ── WORK HISTORY ──
    story.append(Spacer(1, 6))
    story.append(Paragraph("WORK HISTORY", S["section"]))
    story.append(section_divider())

    for job in data["experience"]:
        # Title + dates on same row
        title_date = Table(
            [[
                Paragraph(job["title"].upper(), S["job_title"]),
                Paragraph(job["dates"], S["meta"])
            ]],
            colWidths=[4.5 * inch, 2.7 * inch]
        )
        title_date.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ("ALIGN",        (1, 0), (1, 0),   "RIGHT"),
        ]))
        story.append(title_date)

        # Company + location
        story.append(Paragraph(
            f"<font color='#2E5090'><b>{job['company']}</b></font>"
            f"  |  <font color='#555555'>{job['location']}</font>",
            S["body"]
        ))

        # Bullets
        for b in job["bullets"]:
            story.append(Paragraph(f"• {b}", S["bullet"]))

        story.append(Spacer(1, 4))

    # ── EDUCATION ──
    story.append(Paragraph("EDUCATION", S["section"]))
    story.append(section_divider())

    for edu in data["education"]:
        edu_row = Table(
            [[
                Paragraph(f"<b>{edu['degree']}</b>", S["body"]),
                Paragraph(edu["date"], S["meta"])
            ]],
            colWidths=[4.5 * inch, 2.7 * inch]
        )
        edu_row.setStyle(TableStyle([
            ("VALIGN",       (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            ("ALIGN",        (1, 0), (1, 0),   "RIGHT"),
        ]))
        story.append(edu_row)
        story.append(Paragraph(
            f"{edu['school']}  |  {edu['location']}", S["meta"]
        ))
        story.append(Spacer(1, 4))

    doc.build(story)
    print(f"✅ Resume PDF saved: {output_path}")


def build_cover_letter_pdf(job: dict, paragraphs: list, output_path: str):
    """Generate a professional cover letter PDF"""

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=1.0 * inch,
        leftMargin=1.0 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch
    )

    S = get_styles()
    story = []

    # ── NAME ──
    story.append(Paragraph("Daniel Badasu", S["name"]))

    # ── CONTACT ──
    story.append(Paragraph(
        "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
        S["contact"]
    ))
    story.append(HRFlowable(width="100%", thickness=2, color=MID_BLUE, spaceAfter=16))

    # ── DATE ──
    today = datetime.now().strftime("%B %d, %Y")
    story.append(Paragraph(today, S["meta"]))
    story.append(Spacer(1, 16))

    # ── SALUTATION ──
    story.append(Paragraph("Dear Hiring Manager,", S["cl_body"]))

    # ── PARAGRAPHS ──
    for para in paragraphs:
        # Safety: handle dict or non-string responses from AI
        if isinstance(para, dict):
            para = " ".join(str(v) for v in para.values())
        if isinstance(para, str) and para.strip():
            story.append(Paragraph(para.strip(), S["cl_body"]))

    # ── SIGN OFF ──
    story.append(Spacer(1, 16))
    story.append(Paragraph("Sincerely,", S["cl_body"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<font color='#1F3864'><b>Daniel Badasu</b></font>",
        S["cl_body"]
    ))

    doc.build(story)
    print(f"✅ Cover letter PDF saved: {output_path}")


def get_output_folder():
    """Create dated output folder and clean up folders older than 7 days"""
    import shutil

    base = os.path.expanduser("~/tailored_resumes")
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_folder = os.path.join(base, today_str)

    os.makedirs(today_folder, exist_ok=True)

    # Auto-delete folders older than 7 days
    if os.path.exists(base):
        for folder in os.listdir(base):
            folder_path = os.path.join(base, folder)
            if os.path.isdir(folder_path) and folder != today_str:
                try:
                    folder_date = datetime.strptime(folder, "%Y-%m-%d")
                    age = (datetime.now() - folder_date).days
                    if age > 7:
                        shutil.rmtree(folder_path)
                        print(f"🗑️  Deleted old folder: {folder}")
                except ValueError:
                    pass  # skip non-date folders

    return today_folder


if __name__ == "__main__":
    # Test with sample data
    sample = {
        "name": "Daniel Badasu",
        "contact": "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
        "summary": "Data Analyst focused on building financial and operational reporting functions from the ground up.",
        "skills": ["SQL & Data Querying", "Power BI & Tableau", "Python", "Excel"],
        "certifications": ["Google Data Analytics Professional", "CompTIA Security+"],
        "experience": [{
            "title": "Data Analyst",
            "company": "The Concrete Protector",
            "location": "Lima, Ohio, US",
            "dates": "3/2025 – Present",
            "bullets": ["Analyzed 10,000+ records monthly.", "Built Power BI dashboards."]
        }],
        "education": [{
            "degree": "MS, Applied Security & Data Analytics",
            "school": "University of Findlay",
            "location": "Findlay, OH",
            "date": "12/2024"
        }]
    }
    folder = get_output_folder()
    build_resume_pdf(sample, os.path.join(folder, "test_resume.pdf"))
    build_cover_letter_pdf(
        {"title": "Test", "company": "TestCo"},
        ["This is paragraph one.", "This is paragraph two."],
        os.path.join(folder, "test_cover_letter.pdf")
    )

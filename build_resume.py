"""
build_resume.py  —  2026 Edition
Modern, ATS-safe single-column resume using ReportLab.
Clean typography, subtle accent line, zero tables in the header.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable,
    Table, TableStyle, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from datetime import datetime
import os

# ── PALETTE ─────────────────────────────────────────────────────────────────
NAVY        = colors.HexColor("#0D1B2A")   # deep navy — name & section headers
ACCENT      = colors.HexColor("#1565C0")   # modern blue — dividers & highlights
BODY        = colors.HexColor("#212121")   # near-black — body text
MUTED       = colors.HexColor("#5F6368")   # gray — dates, location, meta
RULE_COLOR  = colors.HexColor("#1565C0")   # accent blue rule under sections
PAGE_W, PAGE_H = letter

# ── STYLES ───────────────────────────────────────────────────────────────────
def styles():
    return {
        # Full name — large, navy, centered
        "name": ParagraphStyle(
            "name",
            fontName="Helvetica-Bold",
            fontSize=26,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceBefore=0,
            spaceAfter=5,
            leading=30,
        ),
        # Contact line — small, muted, centered
        "contact": ParagraphStyle(
            "contact",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=14,
        ),
        # Section header — e.g. EXPERIENCE
        "section": ParagraphStyle(
            "section",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=NAVY,
            spaceBefore=10,
            spaceAfter=3,
            leading=14,
            tracking=1.5,   # subtle letter spacing
        ),
        # Summary / body paragraph
        "body": ParagraphStyle(
            "body",
            fontName="Helvetica",
            fontSize=10,
            textColor=BODY,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
            leading=14.5,
        ),
        # Job title (bold)
        "job_title": ParagraphStyle(
            "job_title",
            fontName="Helvetica-Bold",
            fontSize=10.5,
            textColor=NAVY,
            spaceBefore=6,
            spaceAfter=1,
            leading=14,
        ),
        # Company name (accent blue)
        "company": ParagraphStyle(
            "company",
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=ACCENT,
            spaceAfter=1,
            leading=13,
        ),
        # Dates / location — right-aligned meta
        "meta": ParagraphStyle(
            "meta",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=MUTED,
            alignment=TA_RIGHT,
            leading=13,
        ),
        # Meta left-aligned
        "meta_left": ParagraphStyle(
            "meta_left",
            fontName="Helvetica",
            fontSize=9.5,
            textColor=MUTED,
            alignment=TA_LEFT,
            leading=13,
        ),
        # Bullet points
        "bullet": ParagraphStyle(
            "bullet",
            fontName="Helvetica",
            fontSize=10,
            textColor=BODY,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=3,
            leading=14,
        ),
        # Skills — compact
        "skill": ParagraphStyle(
            "skill",
            fontName="Helvetica",
            fontSize=10,
            textColor=BODY,
            leftIndent=14,
            firstLineIndent=-10,
            spaceAfter=2,
            leading=13.5,
        ),
        # Cover letter body
        "cl_body": ParagraphStyle(
            "cl_body",
            fontName="Helvetica",
            fontSize=10.5,
            textColor=BODY,
            alignment=TA_JUSTIFY,
            spaceAfter=12,
            leading=16,
        ),
    }


def rule(thickness=1.2):
    return HRFlowable(
        width="100%",
        thickness=thickness,
        color=RULE_COLOR,
        spaceBefore=2,
        spaceAfter=5,
    )


def section_header(title, S):
    return [
        Paragraph(title, S["section"]),
        rule(),
    ]


def build_resume_pdf(data: dict, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=0.65 * inch,
        leftMargin=0.65 * inch,
        topMargin=0.55 * inch,
        bottomMargin=0.55 * inch,
    )

    S = styles()
    story = []

    # ── HEADER: name then contact on separate lines (no table = ATS safe) ──
    story.append(Paragraph(data["name"], S["name"]))
    story.append(Paragraph(data["contact"], S["contact"]))

    # Thick accent rule under header
    story.append(HRFlowable(
        width="100%", thickness=2.5,
        color=NAVY, spaceBefore=0, spaceAfter=10
    ))

    # ── PROFESSIONAL SUMMARY ────────────────────────────────────────────────
    story += section_header("PROFESSIONAL SUMMARY", S)
    story.append(Paragraph(data["summary"], S["body"]))

    # ── KEY SKILLS (2-col table — ATS safe: plain text cells) ───────────────
    story += section_header("KEY SKILLS", S)

    skills = data["skills"]
    half = (len(skills) + 1) // 2
    left_col  = skills[:half]
    right_col = skills[half:]

    rows = []
    for i in range(max(len(left_col), len(right_col))):
        l = Paragraph(f"• {left_col[i]}",  S["skill"]) if i < len(left_col)  else Paragraph("", S["skill"])
        r = Paragraph(f"• {right_col[i]}", S["skill"]) if i < len(right_col) else Paragraph("", S["skill"])
        rows.append([l, r])

    skill_tbl = Table(rows, colWidths=[3.55 * inch, 3.55 * inch])
    skill_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 2),
        ("TOPPADDING",    (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))
    story.append(skill_tbl)

    # ── CERTIFICATIONS ───────────────────────────────────────────────────────
    story.append(Spacer(1, 4))
    story += section_header("CERTIFICATIONS", S)

    certs = data["certifications"]
    chalf = (len(certs) + 1) // 2
    lcerts = certs[:chalf]
    rcerts = certs[chalf:]

    cert_rows = []
    for i in range(max(len(lcerts), len(rcerts))):
        l = Paragraph(f"• {lcerts[i]}", S["skill"]) if i < len(lcerts) else Paragraph("", S["skill"])
        r = Paragraph(f"• {rcerts[i]}", S["skill"]) if i < len(rcerts) else Paragraph("", S["skill"])
        cert_rows.append([l, r])

    cert_tbl = Table(cert_rows, colWidths=[3.55 * inch, 3.55 * inch])
    cert_tbl.setStyle(TableStyle([
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LEFTPADDING",   (0,0), (-1,-1), 0),
        ("RIGHTPADDING",  (0,0), (-1,-1), 2),
        ("TOPPADDING",    (0,0), (-1,-1), 1),
        ("BOTTOMPADDING", (0,0), (-1,-1), 1),
    ]))
    story.append(cert_tbl)

    # ── WORK HISTORY ─────────────────────────────────────────────────────────
    story.append(Spacer(1, 4))
    story += section_header("WORK HISTORY", S)

    for job in data["experience"]:
        block = []

        # Job title (left) + dates (right) — single row table
        title_row = Table(
            [[
                Paragraph(job["title"].upper(), S["job_title"]),
                Paragraph(job["dates"], S["meta"]),
            ]],
            colWidths=[4.6 * inch, 2.5 * inch],
        )
        title_row.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 0),
            ("TOPPADDING",    (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        block.append(title_row)

        # Company | Location
        block.append(Paragraph(
            f"<font color='#1565C0'><b>{job['company']}</b></font>"
            f"<font color='#5F6368'>  |  {job['location']}</font>",
            S["body"]
        ))

        for b in job["bullets"]:
            block.append(Paragraph(f"• {b}", S["bullet"]))

        block.append(Spacer(1, 4))
        story.append(KeepTogether(block))

    # ── EDUCATION ────────────────────────────────────────────────────────────
    story += section_header("EDUCATION", S)

    for edu in data["education"]:
        edu_row = Table(
            [[
                Paragraph(f"<b>{edu['degree']}</b>", S["body"]),
                Paragraph(edu["date"], S["meta"]),
            ]],
            colWidths=[4.6 * inch, 2.5 * inch],
        )
        edu_row.setStyle(TableStyle([
            ("VALIGN",        (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING",   (0,0), (-1,-1), 0),
            ("RIGHTPADDING",  (0,0), (-1,-1), 0),
            ("TOPPADDING",    (0,0), (-1,-1), 0),
            ("BOTTOMPADDING", (0,0), (-1,-1), 0),
        ]))
        story.append(edu_row)
        story.append(Paragraph(
            f"<font color='#1565C0'><b>{edu['school']}</b></font>"
            f"<font color='#5F6368'>  |  {edu['location']}</font>",
            S["meta_left"]
        ))
        story.append(Spacer(1, 5))

    doc.build(story)
    print(f"✅ Resume PDF saved: {output_path}")


def build_cover_letter_pdf(job: dict, paragraphs: list, output_path: str):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        rightMargin=1.0 * inch,
        leftMargin=1.0 * inch,
        topMargin=0.8 * inch,
        bottomMargin=0.8 * inch,
    )

    S = styles()
    story = []

    story.append(Paragraph("Daniel Badasu", S["name"]))
    story.append(Paragraph(
        "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
        S["contact"]
    ))
    story.append(HRFlowable(width="100%", thickness=2.5, color=NAVY, spaceAfter=16))

    story.append(Paragraph(datetime.now().strftime("%B %d, %Y"), S["meta_left"]))
    story.append(Spacer(1, 16))
    story.append(Paragraph("Dear Hiring Manager,", S["cl_body"]))

    for para in paragraphs:
        if isinstance(para, dict):
            para = " ".join(str(v) for v in para.values())
        if isinstance(para, str) and para.strip():
            story.append(Paragraph(para.strip(), S["cl_body"]))

    story.append(Spacer(1, 16))
    story.append(Paragraph("Sincerely,", S["cl_body"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<font color='#0D1B2A'><b>Daniel Badasu</b></font>",
        S["cl_body"]
    ))

    doc.build(story)
    print(f"✅ Cover letter PDF saved: {output_path}")


def get_output_folder():
    import shutil
    base = os.path.expanduser("~/tailored_resumes")
    today_str = datetime.now().strftime("%Y-%m-%d")
    today_folder = os.path.join(base, today_str)
    os.makedirs(today_folder, exist_ok=True)

    if os.path.exists(base):
        for folder in os.listdir(base):
            folder_path = os.path.join(base, folder)
            if os.path.isdir(folder_path) and folder != today_str:
                try:
                    folder_date = datetime.strptime(folder, "%Y-%m-%d")
                    if (datetime.now() - folder_date).days > 7:
                        shutil.rmtree(folder_path)
                        print(f"🗑️  Deleted old folder: {folder}")
                except ValueError:
                    pass
    return today_folder


if __name__ == "__main__":
    sample = {
        "name": "Daniel Badasu",
        "contact": "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
        "summary": "Data Analyst focused on building financial and operational reporting functions from the ground up by bridging data gaps between departments. I specialize in developing automated Power BI dashboards and optimizing SQL workflows to transform raw datasets into strategic assets.",
        "skills": [
            "SQL & Data Querying", "Power BI & Tableau", "Python (Data Analysis & Automation)",
            "Excel (Advanced Formulas, Pivot Tables)", "Data Visualization & Dashboard Development",
            "Data Cleaning, Merging & Enrichment", "Reporting & Ad Hoc Analysis",
            "Risk Metrics & Exposure Monitoring", "ETL & Data Pipeline Workflows",
            "Project Management & Workflow Optimization", "Looker Studio", "Data Uploading & Validation"
        ],
        "certifications": [
            "Google Data Analytics Professional – Google",
            "CompTIA Security+ – CompTIA",
            "AWS Cloud Essentials – Amazon Web Services",
            "Cisco Cyber Threat Management – Cisco"
        ],
        "experience": [
            {
                "title": "Data Analyst",
                "company": "The Concrete Protector",
                "location": "Lima, Ohio, US",
                "dates": "3/2025 – Present",
                "bullets": [
                    "Leverage SQL queries and advanced Excel to extract, reconcile, and analyze 10,000+ records per reporting cycle.",
                    "Create interactive dashboards in Tableau, Power BI and Looker Studio tracking key metrics for 5,000+ records annually.",
                    "Clean, merge, and enrich large datasets contributing to 10–15% improvements in reporting efficiency.",
                ]
            },
            {
                "title": "Data Analyst",
                "company": "Prempeh Consulting, CPAs",
                "location": "Washington DC, US",
                "dates": "07/2023 – 01/2025",
                "bullets": [
                    "Engineered foundational reporting functions bridging Finance and IT gaps, improving cross-departmental data visibility by 40%.",
                    "Built automated KPI dashboards in Power BI, reducing manual reporting time by 25 hours monthly.",
                    "Achieved 99.9% data accuracy across all enterprise-level financial reporting.",
                ]
            }
        ],
        "education": [
            {"degree": "Master of Science, Applied Security & Data Analytics", "school": "University of Findlay", "location": "Findlay, OH, US", "date": "12/2024"},
            {"degree": "Bachelor of Science, Information and Communications Technology", "school": "University of Winneba", "location": "Accra, Ghana", "date": "07/2019"}
        ]
    }

    folder = get_output_folder()
    out = os.path.join(folder, "Daniel_Badasu_2026_Resume.pdf")
    build_resume_pdf(sample, out)
    print(f"📄 Saved to: {out}")

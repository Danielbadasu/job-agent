import json
import subprocess
import os
from groq import Groq
from docx2pdf import convert

from config import GROQ_API_KEY
client = Groq(api_key=GROQ_API_KEY)

COVER_LETTER_PROMPT = """
You are an expert cover letter writer. Write a sharp, professional cover letter.

STRICT RULES:
1. Max 250 words — no fluff, no filler sentences
2. 3 paragraphs only:
   - Para 1: Who you are + why THIS role at THIS specific company excites you (be specific about the company)
   - Para 2: Your 2-3 strongest achievements that directly match their needs (use real metrics)
   - Para 3: Short confident close with call to action
3. Use keywords from the job description naturally
4. NEVER start with "I am writing to apply..."
5. Sound human and confident — not robotic or generic
6. Reference the company by name at least twice
7. NO fabrication — only use real background provided below

CANDIDATE BACKGROUND:
- Name: Daniel Badasu
- Experience: 1.5 years as Data Analyst
- Current Role: Data Analyst at The Concrete Protector
  * SQL queries and advanced Excel — 10,000+ records per reporting cycle
  * 20+ recurring and ad hoc reports monthly
  * Tableau, Power BI, Looker Studio dashboards — 5,000+ records annually
  * 10-15% improvements in reporting efficiency
- Previous Role: Data Analyst at Prempeh Consulting CPAs
  * Reduced manual reporting by 25 hours monthly
  * 99.9% data accuracy across enterprise financial reporting
  * 40% improvement in cross-departmental data visibility
  * 30% increase in reporting throughput
- Education: MS Applied Security & Data Analytics — University of Findlay (2024)
- Certifications: CompTIA Security+, Google Data Analytics Professional, AWS Cloud Essentials
- Skills: SQL, Tableau, Power BI, Looker Studio, Excel, Python, data cleaning, dashboards, reporting

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON:
{{
  "cover_letter_paragraphs": [
    "paragraph 1 text",
    "paragraph 2 text",
    "paragraph 3 text"
  ],
  "subject_line": "Application for {job_title} — Daniel Badasu"
}}
"""

def generate_cover_letter(job: dict) -> dict:
    """Call Groq to write tailored cover letter"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{
            "role": "user",
            "content": COVER_LETTER_PROMPT.format(
                job_title=job["title"],
                company=job["company"].upper(),
                job_description=job.get("description", "")[:3000]
            )
        }],
        response_format={"type": "json_object"},
        max_tokens=1000
    )
    return json.loads(response.choices[0].message.content)


def save_cover_letter_pdf(job: dict, content: dict) -> str:
    """Generate cover letter docx via Node.js then convert to PDF"""

    os.makedirs("tailored_resumes", exist_ok=True)
    safe_company = job["company"].replace(" ", "_").replace(",", "").replace(".", "")
    docx_path = f"tailored_resumes/CoverLetter_Daniel_Badasu_{safe_company}.docx"
    pdf_path  = f"tailored_resumes/CoverLetter_Daniel_Badasu_{safe_company}.pdf"

    paragraphs = content.get("cover_letter_paragraphs", [])

    # Build paragraph JS blocks
    para_js = ""
    for para in paragraphs:
        # Escape backticks and backslashes
        safe_para = para.replace("\\", "\\\\").replace("`", "'").replace("\n", " ")
        para_js += f"""
      new Paragraph({{
        spacing: {{ before: 0, after: 240 }},
        children: [new TextRun({{ text: `{safe_para}`, size: 22, font: "Calibri", color: "1A1A1A" }})]
      }}),"""

    today = "February 28, 2026"

    js_code = f"""
const {{ Document, Packer, Paragraph, TextRun, AlignmentType, BorderStyle }} = require('docx');
const fs = require('fs');

const doc = new Document({{
  styles: {{ default: {{ document: {{ run: {{ font: "Calibri", size: 22, color: "1A1A1A" }} }} }} }},
  sections: [{{
    properties: {{
      page: {{
        size: {{ width: 12240, height: 15840 }},
        margin: {{ top: 1440, right: 1440, bottom: 1440, left: 1440 }}
      }}
    }},
    children: [

      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ before: 0, after: 60 }},
        children: [new TextRun({{ text: "Daniel Badasu", bold: true, size: 48, font: "Calibri", color: "1F3864" }})]
      }}),

      new Paragraph({{
        alignment: AlignmentType.CENTER,
        spacing: {{ before: 0, after: 40 }},
        border: {{ bottom: {{ style: BorderStyle.SINGLE, size: 12, color: "2E5090", space: 6 }} }},
        children: [new TextRun({{ text: "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com", size: 22, font: "Calibri", color: "555555" }})]
      }}),

      new Paragraph({{
        spacing: {{ before: 280, after: 40 }},
        children: [new TextRun({{ text: "{today}", size: 22, font: "Calibri", color: "555555" }})]
      }}),

      new Paragraph({{
        spacing: {{ before: 240, after: 240 }},
        children: [new TextRun({{ text: "Dear Hiring Manager,", size: 22, font: "Calibri", color: "1A1A1A" }})]
      }}),

      {para_js}

      new Paragraph({{
        spacing: {{ before: 240, after: 80 }},
        children: [new TextRun({{ text: "Sincerely,", size: 22, font: "Calibri", color: "1A1A1A" }})]
      }}),

      new Paragraph({{
        spacing: {{ before: 80, after: 0 }},
        children: [new TextRun({{ text: "Daniel Badasu", bold: true, size: 22, font: "Calibri", color: "1F3864" }})]
      }}),

    ]
  }}]
}});

Packer.toBuffer(doc).then(buffer => {{
  fs.writeFileSync(String.raw`{docx_path.replace(chr(92), "/")}`, buffer);
  console.log('✅ Cover letter docx saved');
}}).catch(err => {{
  console.error('❌ Error:', err);
  process.exit(1);
}});
"""

    # Save JS to temp file
    js_path = "temp_cover_letter.js"
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(js_code)

    # Run Node.js
    result = subprocess.run(
        ["node", js_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"   ❌ Node error: {result.stderr}")
        return None

    # Convert to PDF
    convert(docx_path, pdf_path)

    # Cleanup
    if os.path.exists(docx_path):
        os.remove(docx_path)
    if os.path.exists(js_path):
        os.remove(js_path)

    return pdf_path


def run():
    """Generate cover letters for all jobs in proceed_jobs.json"""

    with open("proceed_jobs.json") as f:
        jobs = json.load(f)

    # Also load application queue to update it
    with open("application_queue.json") as f:
        queue = json.load(f)

    print(f"\n✉️  Generating cover letters for {len(jobs)} jobs...\n")
    print("=" * 55)

    for i, job in enumerate(jobs):
        print(f"\n📝 {job['company'].upper()} — {job['title']}")

        content = generate_cover_letter(job)
        print(f"   Subject: {content.get('subject_line', '')}")

        pdf_path = save_cover_letter_pdf(job, content)

        if pdf_path:
            print(f"   ✅ Saved: {pdf_path}")
            # Update application queue with cover letter path
            if i < len(queue):
                queue[i]["cover_letter_pdf"] = pdf_path
        else:
            print(f"   ❌ Failed")

    # Save updated queue
    with open("application_queue.json", "w") as f:
        json.dump(queue, f, indent=2)

    print(f"\n{'=' * 55}")
    print(f"✅ All cover letters done!")
    print(f"{'=' * 55}\n")
    print("📁 Your tailored_resumes folder now has:")
    print("   • Resume PDF for each job")
    print("   • Cover Letter PDF for each job")
    print("\n💾 application_queue.json updated with all file paths")
    print("➡️  Next: run main.py to wire everything together!\n")


if __name__ == "__main__":
    run()

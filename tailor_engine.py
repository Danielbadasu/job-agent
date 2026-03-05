import json
import subprocess
import os
from groq import Groq

from config import GROQ_API_KEY
client = Groq(api_key=GROQ_API_KEY)

# ── BASE RESUME DATA (frozen sections — never change these) ─────────────────
BASE = {
  "name": "Daniel Badasu",
  "contact": "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
  "education": [
    {
      "degree": "Master of Science, Applied Security & Data Analytics",
      "school": "University of Findlay",
      "location": "Findlay, OH, US",
      "date": "12/2024"
    },
    {
      "degree": "Bachelor of Science, Information and Communications Technology",
      "school": "University of Winneba",
      "location": "Accra, Ghana",
      "date": "07/2019"
    }
  ],
  "certifications": [
    "Google Data Analytics Professional – Google",
    "CompTIA Security+ – CompTIA",
    "AWS Cloud Essentials – Amazon Web Services",
    "Cisco Cyber Threat Management – Cisco"
  ],

  # ── THESE GET TAILORED PER JOB ──
  "summary": "Data Analyst focused on building financial and operational reporting functions from the ground up by bridging data gaps between departments. I specialize in developing automated Power BI dashboards and optimizing SQL workflows to transform raw datasets into strategic assets. I thrive in high-growth environments, acting as a technical partner to leadership by eliminating manual bottlenecks and delivering 99.9% accurate insights that drive scalable growth.",
  "skills": [
    "Data Analysis, Data Mining & Reporting",
    "Excel (Advanced Formulas, Pivot Tables, VBA Exposure)",
    "Looker Studio, Power BI & Tableau",
    "SQL & Data Querying",
    "Risk Metrics & Exposure Monitoring",
    "Data Uploading, Validation & Reconciliation",
    "Data Cleaning, Merging, and Enrichment",
    "Data Visualization & Dashboard Development",
    "Ad Hoc Reporting & Metrics Tracking",
    "Supply Chain & Operational Data Analysis",
    "Project Management & Workflow Optimization",
    "Python (Data Analysis & Automation)"
  ],
  "experience": [
    {
      "title": "Data Analyst",
      "company": "The Concrete Protector",
      "location": "Lima, Ohio, US",
      "dates": "3/2025 – Present",
      "bullets": [
        "Leverage SQL queries and advanced Excel to extract, reconcile, and analyze 10,000+ records per reporting cycle, ensuring data accuracy for 20+ recurring and ad hoc reports monthly.",
        "Upload and manage data feeds across analytics systems, validating 10,000+ data points per reporting cycle to ensure accuracy, consistency, and alignment with financial and risk reporting standards.",
        "Create interactive dashboards and visualizations in Tableau, Power BI and Looker Studio, tracking key metrics and enabling actionable insights for 5,000+ records annually.",
        "Clean, merge, and enrich large datasets to ensure data accuracy and reliability for analysis, contributing to 10-15% improvements in reporting efficiency.",
        "Support client and internal inquiries by providing analytical explanations for reported results, contributing to timely issue resolution and improved stakeholder confidence."
      ]
    },
    {
      "title": "Data Analyst",
      "company": "Prempeh Consulting, CPAs",
      "location": "Washington DC, US",
      "dates": "07/2023 – 01/2025",
      "bullets": [
        "Led Financial Analytics Implementation: Engineered foundational reporting functions that bridged Finance and IT gaps, improving cross-departmental data visibility by 40%.",
        "Developed Power BI Ecosystem: Built automated KPI dashboards as the primary power user, reducing manual reporting time by 25 hours monthly.",
        "Optimized Data & SQL Integrity: Audited relational datasets and technical configurations to achieve 99.9% data accuracy across all enterprise-level financial reporting.",
        "Engineered Scalable Reporting Workflows: Established automated data preparation processes that increased reporting throughput by 30% during high-growth, fast-paced cycles."
      ]
    }
  ]
}

TAILOR_PROMPT = """
You are an expert resume writer tailoring a resume for a specific job.

STRICT RULES:
1. NEVER change: name, contact, education, certifications, company names, job titles, dates, locations
2. DO change: summary, bullet point wording, bullet order, skills order
3. Keep ALL metrics exactly as-is (99.9%, 25 hours, 40%, 30%, 10-15%)
4. Reword bullets naturally to echo job keywords — do NOT fabricate new achievements
5. Put most relevant bullets FIRST for each job
6. Reorder skills list — most relevant to this job comes first
7. Summary must be 3 sentences max, mirror the job's language
8. Sound human, not robotic

CANDIDATE BASE RESUME:
{base_resume}

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON with this exact structure:
{{
  "summary": "tailored 3-sentence summary",
  "skills": ["skill1", "skill2", "...all 12 skills reordered by relevance"],
  "experience": [
    {{
      "title": "Data Analyst",
      "company": "The Concrete Protector",
      "location": "Lima, Ohio, US",
      "dates": "3/2025 – Present",
      "bullets": ["most relevant bullet first", "...all 5 bullets reworded and reordered"]
    }},
    {{
      "title": "Data Analyst",
      "company": "Prempeh Consulting, CPAs",
      "location": "Washington DC, US",
      "dates": "07/2023 – 01/2025",
      "bullets": ["most relevant bullet first", "...all 4 bullets reworded and reordered"]
    }}
  ]
}}
"""

def tailor_for_job(job: dict) -> dict:
    """Call Groq to tailor resume content for a specific job"""

    base_text = json.dumps({
        "summary": BASE["summary"],
        "skills": BASE["skills"],
        "experience": BASE["experience"]
    }, indent=2)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{
            "role": "user",
            "content": TAILOR_PROMPT.format(
                base_resume=base_text,
                job_title=job["title"],
                company=job["company"],
                job_description=job["description"][:3500]
            )
        }],
        response_format={"type": "json_object"},
        max_tokens=2000
    )

    tailored = json.loads(response.choices[0].message.content)

    # Merge tailored content with frozen sections
    full_resume = {
        **BASE,
        "summary": tailored["summary"],
        "skills": tailored["skills"],
        "experience": tailored["experience"]
    }

    return full_resume


def generate_pdf(resume_data: dict, company: str) -> str:
    """Generate tailored resume as PDF — docx is temp, only PDF is kept"""

    os.makedirs("tailored_resumes", exist_ok=True)

    safe_company = company.replace(" ", "_").replace(",", "").replace(".", "")
    docx_path = f"tailored_resumes/Daniel_Badasu_{safe_company}_DA.docx"
    pdf_path  = f"tailored_resumes/Daniel_Badasu_{safe_company}_DA.pdf"
    json_path = "temp_resume.json"

    # Step 1 — Save resume data as JSON for Node to read
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(resume_data, f, indent=2, ensure_ascii=False)

    # Step 2 — Call Node.js to generate .docx
    result = subprocess.run(
        ["node", "build_resume_v2.js", json_path, docx_path],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        print(f"   ❌ Node error: {result.stderr}")
        return None

    # Step 3 — Convert .docx to .pdf using Microsoft Word
    convert(docx_path, pdf_path)

    # Step 4 — Clean up temp files
    if os.path.exists(docx_path):
        os.remove(docx_path)
    if os.path.exists(json_path):
        os.remove(json_path)

    print(f"   ✅ PDF ready: {pdf_path}")
    return pdf_path


def run_tailoring():
    """Main runner — tailor and generate PDF resume for every matched job"""

    with open("proceed_jobs.json") as f:
        jobs = json.load(f)

    print(f"\n📋 Tailoring resumes for {len(jobs)} jobs...\n")
    print("=" * 55)

    results = []

    for job in jobs:
        print(f"\n🔄 {job['company'].upper()} — {job['title']}")

        # AI tailoring
        tailored_data = tailor_for_job(job)

        # Generate PDF
        pdf_path = generate_pdf(tailored_data, job["company"])

        if pdf_path:
            results.append({
                "company": job["company"],
                "title": job["title"],
                "url": job["url"],
                "score": job["score"]["total"],
                "resume_pdf": pdf_path,
                "cover_letter_pdf": ""  # will be filled by cover_letter_gen.py
            })
            print(f"   Score:  {job['score']['total']}%")
            print(f"   Apply:  {job['url']}")

    # Final summary
    print(f"\n{'=' * 55}")
    print(f"✅ {len(results)} tailored PDF resumes ready!")
    print(f"{'=' * 55}\n")

    for r in results:
        print(f"  {r['score']}% — {r['company']} | {r['title']}")
        print(f"  PDF:    {r['resume_pdf']}")
        print(f"  Apply:  {r['url']}\n")

    # Save to application queue for cover letter gen + final review
    with open("application_queue.json", "w") as f:
        json.dump(results, f, indent=2)

    print("💾 Saved to application_queue.json")
    print("➡️  Next: run cover_letter_gen.py to generate cover letters\n")


if __name__ == "__main__":
    run_tailoring()

import json
import os
from datetime import datetime
from groq import Groq
from config import GROQ_API_KEY
from build_resume import build_resume_pdf, get_output_folder

client = Groq(api_key=GROQ_API_KEY)

APPLIED_JOBS_FILE = os.path.expanduser("~/applied_jobs.json")

BASE = {
  "name": "Daniel Badasu",
  "contact": "Findlay, OH 45840  |  +1 (567) 294 2730  |  danielbadasu10@gmail.com",
  "education": [
    {"degree": "Master of Science, Applied Security & Data Analytics", "school": "University of Findlay", "location": "Findlay, OH, US", "date": "12/2024"},
    {"degree": "Bachelor of Science, Information and Communications Technology", "school": "University of Winneba", "location": "Accra, Ghana", "date": "07/2019"}
  ],
  "certifications": [
    "Google Data Analytics Professional – Google",
    "CompTIA Security+ – CompTIA",
    "AWS Cloud Essentials – Amazon Web Services",
    "Cisco Cyber Threat Management – Cisco"
  ],
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
9. Return EXACTLY 3 bullets for The Concrete Protector — pick the 3 most relevant to this role
10. Return EXACTLY 4 bullets for Prempeh Consulting, CPAs — pick the 4 most relevant to this role

CANDIDATE BASE RESUME:
{base_resume}

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION:
{job_description}

Return ONLY valid JSON:
{{
  "summary": "tailored 3-sentence summary",
  "skills": ["skill1", "skill2", "...all 12 skills reordered by relevance"],
  "experience": [
    {{"title": "Data Analyst", "company": "The Concrete Protector", "location": "Lima, Ohio, US", "dates": "3/2025 – Present", "bullets": ["bullet1", "bullet2", "bullet3"]}},
    {{"title": "Data Analyst", "company": "Prempeh Consulting, CPAs", "location": "Washington DC, US", "dates": "07/2023 – 01/2025", "bullets": ["bullet1", "bullet2", "bullet3", "bullet4"]}}
  ]
}}
"""

def load_applied_jobs():
    if os.path.exists(APPLIED_JOBS_FILE):
        with open(APPLIED_JOBS_FILE) as f:
            return json.load(f)
    return {}

def save_applied_jobs(applied):
    with open(APPLIED_JOBS_FILE, "w") as f:
        json.dump(applied, f, indent=2)

def get_job_url(job):
    """Safely extract job URL from any common key name."""
    return job.get("url") or job.get("link") or job.get("apply_url") or job.get("job_url") or ""

def is_duplicate(job, applied):
    url = get_job_url(job)
    if url and url in applied:
        seen_date = datetime.strptime(applied[url], "%Y-%m-%d")
        days_ago = (datetime.now() - seen_date).days
        if days_ago < 60:
            print(f"   ⏭️  Skipping — seen {days_ago} days ago")
            return True
    return False

def safe_filename(company, title):
    def clean(s):
        for ch in [" ", ",", ".", "/", "&", "(", ")", "-"]:
            s = s.replace(ch, "_")
        return s.strip("_")
    return f"{clean(company)}_{clean(title)}"

def tailor_for_job(job):
    base_text = json.dumps({"summary": BASE["summary"], "skills": BASE["skills"], "experience": BASE["experience"]}, indent=2)
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": TAILOR_PROMPT.format(
            base_resume=base_text,
            job_title=job["title"],
            company=job["company"],
            job_description=job["description"][:3500]
        )}],
        response_format={"type": "json_object"},
        max_tokens=2000
    )
    tailored = json.loads(response.choices[0].message.content)
    return {**BASE, "summary": tailored["summary"], "skills": tailored["skills"], "experience": tailored["experience"]}

def run_tailoring():
    with open("proceed_jobs.json") as f:
        jobs = json.load(f)

    applied = load_applied_jobs()
    output_folder = get_output_folder()

    print(f"\n📋 Processing {len(jobs)} matched jobs...")
    print(f"📁 Output: {output_folder}\n{'='*55}")

    results = []
    skipped = 0

    for job in jobs:
        print(f"\n🔍 {job['company'].upper()} — {job['title']}")

        if is_duplicate(job, applied):
            skipped += 1
            continue

        tailored_data = tailor_for_job(job)

        file_slug = safe_filename(job["company"], job["title"])
        pdf_path  = os.path.join(output_folder, f"Daniel_Badasu_{file_slug}.pdf")

        build_resume_pdf(tailored_data, pdf_path)
        print(f"   ✅ Resume saved")

        job_url = get_job_url(job)
        if job_url:
            applied[job_url] = datetime.now().strftime("%Y-%m-%d")

        results.append({
            "company": job["company"],
            "title": job["title"],
            "url": job_url,
            "score": job["score"]["total"],
            "resume_pdf": pdf_path,
            "cover_letter_pdf": "",
            "output_folder": output_folder,
            "file_slug": file_slug
        })
        print(f"   Score: {job['score']['total']}%  |  Apply: {job_url}")

    save_applied_jobs(applied)

    print(f"\n{'='*55}")
    print(f"✅ {len(results)} new resumes ready!")
    if skipped:
        print(f"⏭️  {skipped} duplicate jobs skipped")
    print(f"{'='*55}\n")

    with open("application_queue.json", "w") as f:
        json.dump(results, f, indent=2)
    print("💾 Saved to application_queue.json\n")

if __name__ == "__main__":
    run_tailoring()

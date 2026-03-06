import json
import os
from groq import Groq
from config import GROQ_API_KEY
from build_resume import build_cover_letter_pdf

client = Groq(api_key=GROQ_API_KEY)

COVER_LETTER_PROMPT = """
You are an expert cover letter writer. Write a sharp, professional cover letter.

STRICT RULES:
1. Max 250 words, 3 paragraphs only
2. Para 1: Who you are + why THIS role at THIS company excites you (specific)
3. Para 2: 2-3 strongest achievements matching their needs (real metrics only)
4. Para 3: Short confident close with call to action
5. Use job keywords naturally. NEVER start with "I am writing to apply..."
6. Reference company name at least twice. NO fabrication.

CANDIDATE BACKGROUND:
- Daniel Badasu, 1.5 years Data Analyst experience
- Current: The Concrete Protector — SQL, Excel, Tableau, Power BI, Looker Studio, 10,000+ records/cycle, 20+ reports monthly
- Previous: Prempeh Consulting CPAs — 25hrs/month saved, 99.9% accuracy, 40% visibility improvement, 30% throughput increase
- Education: MS Applied Security & Data Analytics, University of Findlay (2024)
- Certs: CompTIA Security+, Google Data Analytics Professional, AWS Cloud Essentials

JOB TITLE: {job_title}
COMPANY: {company}
JOB DESCRIPTION: {job_description}

Return ONLY valid JSON:
{{"cover_letter_paragraphs": ["para1", "para2", "para3"], "subject_line": "Application for {job_title} — Daniel Badasu"}}
"""

def get_job_url(job):
    """Safely extract job URL from any common key name."""
    return job.get("url") or job.get("link") or job.get("apply_url") or job.get("job_url") or ""

def generate_cover_letter(job):
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": COVER_LETTER_PROMPT.format(
            job_title=job["title"],
            company=job["company"].upper(),
            job_description=job.get("description", "")[:3000]
        )}],
        response_format={"type": "json_object"},
        max_tokens=1000
    )
    return json.loads(response.choices[0].message.content)

def run():
    with open("proceed_jobs.json") as f:
        jobs = json.load(f)
    with open("application_queue.json") as f:
        queue = json.load(f)

    print(f"\n✉️  Generating cover letters for {len(queue)} jobs...\n{'='*55}")

    updated_queue = []

    for item in queue:
        job_url = get_job_url(item)

        # Find matching job description from proceed_jobs.json
        job = next((j for j in jobs if get_job_url(j) == job_url), None)
        if not job:
            updated_queue.append(item)
            continue

        print(f"\n📝 {item['company'].upper()} — {item['title']}")

        content = generate_cover_letter(job)
        paragraphs = content.get("cover_letter_paragraphs", [])

        file_slug     = item.get("file_slug", item["company"])
        output_folder = item.get("output_folder", os.path.expanduser("~/tailored_resumes"))
        pdf_path      = os.path.join(output_folder, f"CoverLetter_Daniel_Badasu_{file_slug}.pdf")

        build_cover_letter_pdf(job, paragraphs, pdf_path)
        item["cover_letter_pdf"] = pdf_path
        updated_queue.append(item)

        print(f"   ✅ Saved: CoverLetter_Daniel_Badasu_{file_slug}.pdf")

    with open("application_queue.json", "w") as f:
        json.dump(updated_queue, f, indent=2)

    print(f"\n{'='*55}")
    print(f"✅ All cover letters done!")
    print(f"{'='*55}")
    print("💾 application_queue.json updated\n")

if __name__ == "__main__":
    run()

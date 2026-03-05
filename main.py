import subprocess
import sys
from datetime import datetime

print(f"""
╔══════════════════════════════════════════════════╗
║       JOB APPLICATION AGENT — DANIEL BADASU      ║
║       {datetime.now().strftime("%A, %B %d %Y  %I:%M %p")}           ║
╚══════════════════════════════════════════════════╝
""")

steps = [
    ("🔍 STEP 1 — Scraping jobs from 50+ companies...",     "multi_scraper.py"),
    ("🧠 STEP 2 — AI scoring all matched jobs...",           "smart_scorer.py"),
    ("📄 STEP 3 — Tailoring resumes + generating PDFs...",  "tailor_engine.py"),
    ("✉️  STEP 4 — Writing cover letters...",                "cover_letter_gen.py"),
    ("📧 STEP 5 — Sending daily report email...",           "email_notifier.py"),
]

failed = []

for message, script in steps:
    print(f"\n{message}")
    print("-" * 50)
    result = subprocess.run(
        [sys.executable, script],
        capture_output=False
    )
    if result.returncode != 0:
        print(f"\n⚠️  {script} had issues — continuing...\n")
        failed.append(script)

print(f"""
╔══════════════════════════════════════════════════╗
║              ✅ DAILY RUN COMPLETE!              ║
║                                                  ║
║  📁 Check tailored_resumes/ for your files       ║
║  📋 Check application_queue.json for links       ║
║  📧 Check danielbadasu3@gmail.com for report    ║
║                                                  ║
║  GO GET THOSE INTERVIEWS! 💪                     ║
╚══════════════════════════════════════════════════╝
""")

if failed:
    print(f"⚠️  Scripts with issues: {', '.join(failed)}")

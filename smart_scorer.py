import httpx
import json
import os
import re
import time
from groq import Groq
from config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)

MY_PROFILE = """
- 1.5 years experience as Data Analyst
- Masters in Applied Security and Data Analytics
- CompTIA Security+ certified
- Google Professional Data Analytics Certified
- Skills: SQL, Tableau, Power BI, Excel, Python, data cleaning, dashboards, reporting, automation
- Experience: building dashboards, data cleaning, reporting, scripting
- US based, open to remote or hybrid
"""

def smart_score(title: str, description: str, company: str) -> dict:
    prompt = f"""
You are a strict job fit evaluator. Score this job for this candidate.

CANDIDATE:
{MY_PROFILE}

JOB TITLE: {title}
COMPANY: {company}
JOB DESCRIPTION:
{description[:3000]}

Score from 0-100 based on:
- Skill overlap (40pts): How well candidate skills match requirements
- Tool overlap (20pts): Tableau, Power BI, SQL, Python, Excel matches
- Experience alignment (15pts): 1.5 years vs what job requires
- Domain relevance (10pts): Is this genuinely a DA/BI/reporting role?
- Security crossover (5pts): Does security background add value here?
- Keyword match (10pts): How many key terms align

Be STRICT. If job requires 3+ years and candidate has 1.5, penalize.
If job is genuinely entry-to-mid level, reward it.

Return ONLY valid JSON:
{{
  "total": 85,
  "skill_score": 35,
  "tool_score": 18,
  "experience_score": 12,
  "domain_score": 10,
  "security_score": 3,
  "keyword_score": 7,
  "decision": "PROCEED",
  "reason": "one sentence why",
  "missing_skills": ["skill1"],
  "strong_matches": ["match1"]
}}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=500
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"   ⚠️  Scoring error: {e}")
        return {
            "total": 0, "skill_score": 0, "tool_score": 0,
            "experience_score": 0, "domain_score": 0,
            "security_score": 0, "keyword_score": 0,
            "decision": "ERROR", "reason": "scoring failed",
            "missing_skills": [], "strong_matches": []
        }


companies = [
    "stripe", "cloudflare", "crowdstrike", "datadog", "elastic",
    "splunk", "coinbase", "okta", "pagerduty", "sentinelone",
    "intercom", "twilio", "amplitude", "mixpanel", "fivetran",
    "snowflake", "databricks", "asana", "hubspot",
    "dropbox", "zoom", "box", "docusign", "zendesk",
    "gitlab", "hashicorp", "confluent", "dbt-labs", "airbyte",
    "retool", "hex", "mode", "sigma-computing", "lightdash",
    "affirm", "chime", "marqeta", "unit21", "sift",
    "expel", "lacework", "snyk", "detectify", "axonius",
    "vanta", "drata", "secureframe", "thoropass", "hyperproof"
]

US_KEYWORDS = ["remote", "united states", "us", "new york", "san francisco",
               "austin", "chicago", "seattle", "hybrid", "bellevue", "menlo park"]

RELEVANT_TITLES = ["data analyst", "reporting analyst", "bi analyst",
                   "business intelligence", "security analyst",
                   "threat intelligence", "compliance analyst", "risk analyst"]

EXCLUDE_TITLES = ["senior", "staff", "principal", "director", "manager",
                  "lead", "sr.", " ii", " iii", " iv", " 2", " 3",
                  "intern", "internship"]

results = []

for company in companies:
    try:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        r = httpx.get(url, timeout=10)
        jobs = r.json().get("jobs", [])

        for j in jobs:
            title = j["title"].lower()
            location = j["location"]["name"].lower()

            if not any(t in title for t in RELEVANT_TITLES):
                continue
            if any(e in title for e in EXCLUDE_TITLES):
                continue
            if not any(us in location for us in US_KEYWORDS):
                continue

            job_id = j["id"]
            detail = httpx.get(
                f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}",
                timeout=10
            ).json()
            clean_text = re.sub(r'<[^>]+>', ' ', detail.get("content", ""))

            # ── Small delay to avoid rate limits ──
            time.sleep(2)

            score = smart_score(j["title"], clean_text, company)
            icon = "✅" if score["total"] >= 75 else "❌"

            print(f"\n{icon} {company.upper()} — {j['title']}")
            print(f"   Score: {score['total']} | {score['decision']}")
            print(f"   Reason: {score['reason']}")
            print(f"   Strong matches: {score['strong_matches']}")
            print(f"   Missing: {score['missing_skills']}")
            print(f"   Link: {j['absolute_url']}")

            if score["total"] >= 75:
                results.append({**j, "score": score, "company": company,
                                 "description": clean_text})

    except Exception:
        continue

print(f"\n\n🎯 TOTAL PROCEED: {len(results)} jobs worth applying to")

# Save for tailor engine
with open("proceed_jobs.json", "w") as f:
    json.dump(results, f, indent=2)

print("💾 Saved to proceed_jobs.json")

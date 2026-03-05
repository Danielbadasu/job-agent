import httpx
import re
import json
from groq import Groq

client = Groq(api_key="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")

MY_PROFILE = """
- 1.5 years experience as Data Analyst
- Masters in Applied Security and Data Analytics
- CompTIA Security+ certified
- Google Professional Data Analytics Certificate
- Skills: SQL, Tableau, Power BI, Excel, Python, data cleaning, dashboards, reporting, automation
- US based, open to remote or hybrid
"""

US_KEYWORDS = ["remote", "united states", "us", "new york", "san francisco",
               "austin", "chicago", "seattle", "hybrid", "bellevue", "menlo park",
               "boston", "denver", "atlanta", "dallas", "washington", "anywhere"]

RELEVANT_TITLES = ["data analyst", "reporting analyst", "bi analyst",
                   "business intelligence", "security analyst",
                   "threat intelligence", "compliance analyst", "risk analyst",
                   "analytics analyst", "insights analyst", "operations analyst"]

EXCLUDE_TITLES = ["senior", "staff", "principal", "director", "manager",
                  "lead", "sr.", " ii", " iii", " iv", " 2", " 3",
                  "intern", "internship", "vp ", "head of"]

# ─────────────────────────────────────────
# GREENHOUSE COMPANIES
# ─────────────────────────────────────────
GREENHOUSE_COMPANIES = [
    "airbnb", "dropbox", "box", "zendesk", "hubspot",
    "gitlab", "hashicorp", "confluent", "affirm", "chime",
    "brex", "gusto", "rippling", "lattice", "airtable",
    "retool", "amplitude", "mixpanel", "fullstory", "segment",
    "robinhood", "coinbase", "plaid", "stripe", "klarna",
    "cloudflare", "crowdstrike", "datadog", "elastic", "splunk",
    "okta", "pagerduty", "sentinelone", "snyk", "lacework",
    "vanta", "drata", "sift", "unit21", "expel",
    "dbt-labs", "fivetran", "airbyte", "sigma-computing",
    "twilio", "intercom", "asana", "notion", "figma",
    "sofi", "nerdwallet", "betterment", "marqeta"
]

# ─────────────────────────────────────────
# LEVER COMPANIES
# ─────────────────────────────────────────
LEVER_COMPANIES = [
    "netflix", "reddit", "canva", "scale-ai", "perplexity-ai",
    "openai", "anthropic", "mistral", "cohere", "huggingface",
    "replit", "cursor", "linear", "vercel", "supabase",
    "planetscale", "neon", "turso", "xata", "convex",
    "watershed", "arcadia", "clearscore", "benchling", "carta",
    "ripple", "kraken", "gemini-exchange", "anchorage",
    "clickup", "monday", "smartsheet", "coda", "craft",
    "deel", "remote", "oyster-hr", "papaya-global",
    "harness", "launchdarkly", "split", "statsig", "growthbook"
]


def is_relevant(title: str, location: str) -> bool:
    title_l = title.lower()
    location_l = location.lower()
    if not any(t in title_l for t in RELEVANT_TITLES):
        return False
    if any(e in title_l for e in EXCLUDE_TITLES):
        return False
    if not any(us in location_l for us in US_KEYWORDS):
        return False
    return True


def clean_html(html: str) -> str:
    return re.sub(r'<[^>]+>', ' ', html)


def smart_score(title: str, description: str, company: str) -> dict:
    prompt = f"""
You are a strict job fit evaluator. Score this job for this candidate.

CANDIDATE:
{MY_PROFILE}

JOB TITLE: {title}
COMPANY: {company}
JOB DESCRIPTION:
{description[:3000]}

Score 0-100:
- Skill overlap (40pts)
- Tool overlap (20pts)  
- Experience alignment (15pts): candidate has 1.5 years
- Domain relevance (10pts)
- Security crossover (5pts)
- Keyword match (10pts)

Be honest. Penalize 3+ year requirements. Reward entry-to-mid roles.

Return ONLY valid JSON:
{{
  "total": 85,
  "decision": "PROCEED",
  "reason": "one sentence",
  "missing_skills": ["skill1"],
  "strong_matches": ["match1"]
}}
"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            max_tokens=300
        )
        return json.loads(response.choices[0].message.content)
    except:
        return {"total": 0, "decision": "ERROR", "reason": "scoring failed",
                "missing_skills": [], "strong_matches": []}


# ─────────────────────────────────────────
# GREENHOUSE SCRAPER
# ─────────────────────────────────────────
def scrape_greenhouse(companies: list) -> list:
    results = []
    print("\n🔍 Scanning Greenhouse companies...")
    for company in companies:
        try:
            r = httpx.get(
                f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
                timeout=10
            )
            jobs = r.json().get("jobs", [])
            for j in jobs:
                if not is_relevant(j["title"], j["location"]["name"]):
                    continue
                detail = httpx.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{j['id']}",
                    timeout=10
                ).json()
                description = clean_html(detail.get("content", ""))
                results.append({
                    "source": "greenhouse",
                    "company": company,
                    "title": j["title"],
                    "location": j["location"]["name"],
                    "url": j["absolute_url"],
                    "description": description
                })
        except:
            continue
    print(f"✅ Greenhouse: {len(results)} relevant jobs found")
    return results


# ─────────────────────────────────────────
# LEVER SCRAPER
# ─────────────────────────────────────────
def scrape_lever(companies: list) -> list:
    results = []
    print("\n🔍 Scanning Lever companies...")
    for company in companies:
        try:
            r = httpx.get(
                f"https://api.lever.co/v0/postings/{company}?mode=json",
                timeout=10
            )
            jobs = r.json()
            if not isinstance(jobs, list):
                continue
            for j in jobs:
                title = j.get("text", "")
                location = j.get("categories", {}).get("location", "")
                if not is_relevant(title, location):
                    continue
                # Lever includes full description in listing
                lists = j.get("lists", [])
                additional = j.get("additional", "")
                description = " ".join(
                    [item.get("content", "") for item in lists]
                ) + " " + clean_html(additional)

                results.append({
                    "source": "lever",
                    "company": company,
                    "title": title,
                    "location": location,
                    "url": j.get("hostedUrl", ""),
                    "description": description
                })
        except:
            continue
    print(f"✅ Lever: {len(results)} relevant jobs found")
    return results


# ─────────────────────────────────────────
# MAIN RUNNER
# ─────────────────────────────────────────
def run():
    all_jobs = []
    all_jobs += scrape_greenhouse(GREENHOUSE_COMPANIES)
    all_jobs += scrape_lever(LEVER_COMPANIES)

    print(f"\n📋 Total relevant jobs to score: {len(all_jobs)}")
    print("🧠 Scoring with AI now...\n")

    proceed_jobs = []

    for job in all_jobs:
        score = smart_score(job["title"], job["description"], job["company"])
        job["score"] = score

        icon = "✅" if score["total"] >= 75 else "❌"
        print(f"{icon} {job['company'].upper()} — {job['title']}")
        print(f"   Score: {score['total']} | {score['decision']}")
        print(f"   Reason: {score['reason']}")
        print(f"   Matches: {score['strong_matches']}")
        print(f"   Missing: {score['missing_skills']}")
        print(f"   Link: {job['url']}\n")

        if score["total"] >= 75:
            proceed_jobs.append(job)

    # Sort by score
    proceed_jobs.sort(key=lambda x: x["score"]["total"], reverse=True)

    print(f"\n{'='*60}")
    print(f"🎯 TOTAL PROCEED: {len(proceed_jobs)} jobs worth applying to")
    print(f"{'='*60}")
    print("\n🏆 TOP MATCHES:\n")
    for job in proceed_jobs[:10]:
        print(f"  {job['score']['total']}% — {job['company'].upper()} | {job['title']}")
        print(f"  {job['url']}\n")

    # Save to file for resume tailoring next
    with open("proceed_jobs.json", "w") as f:
        json.dump(proceed_jobs, f, indent=2)
    print("💾 Saved to proceed_jobs.json — ready for resume tailoring!")

if __name__ == "__main__":
    run()
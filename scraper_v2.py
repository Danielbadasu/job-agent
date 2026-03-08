import httpx
import json
import os
import re
from match_scorer import score_job

# ─── GREENHOUSE COMPANIES ───────────────────────────────────────────────────
GREENHOUSE_COMPANIES = [
    # Fintech & Payments
    "stripe", "brex", "plaid", "coinbase", "robinhood", "chime",
    "affirm", "marqeta", "adyen", "checkout", "ramp", "mercury",
    "carta", "ripple", "kraken", "gemini", "bitgo",
    # Cybersecurity
    "crowdstrike", "sentinelone", "okta", "pagerduty", "datadog",
    "elastic", "splunk", "expel", "lacework", "snyk", "wiz",
    "orca-security", "abnormal-security", "exabeam", "sumo-logic",
    "rapid7", "tenable", "qualys", "sailpoint", "cyberark",
    "proofpoint", "darktrace", "vectra", "illumio",
    # Data & Analytics
    "snowflake", "databricks", "domo", "thoughtspot", "sigma",
    "fivetran", "segment", "mixpanel", "amplitude", "heap",
    "looker", "periscope", "sisense", "monte-carlo", "atlan",
    "rudderstack", "hightouch", "census",
    # Cloud & Infra
    "cloudflare", "hashicorp", "mongodb", "redis", "cockroachdb",
    "planetscale", "supabase", "vercel", "netlify", "fastly",
    # SaaS & Productivity
    "asana", "hubspot", "zendesk", "intercom", "freshworks",
    "notion", "airtable", "figma", "miro", "loom",
    "greenhouse", "lever", "gusto", "rippling", "lattice",
    # Dev Tools
    "twilio", "sendgrid", "postman", "sentry", "linear",
    "launchdarkly", "circleci", "dbt-labs",
]

# ─── LEVER COMPANIES ────────────────────────────────────────────────────────
LEVER_COMPANIES = [
    # Fintech
    "acorns", "betterment", "wealthfront", "sofi", "green-dot",
    "payoneer", "paxos", "silvergate",
    # Cybersecurity & IT
    "recorded-future", "tanium", "netskope", "observe", "hunters",
    "push-security", "grip-security", "island", "memcyco",
    # Data & Analytics
    "preset", "lightdash", "cube", "transform", "metabase",
    "mode", "chartio", "cluvio", "count",
    # SaaS
    "front", "guru", "helpscout", "drift", "outreach",
    "salesloft", "gong", "chorus", "clari", "apollo",
    "calendly", "typeform", "productboard", "pendo", "appcues",
    # HR & Ops
    "deel", "remote", "oyster", "papaya-global", "bamboohr",
    "leapsome", "culture-amp", "reflektive", "betterworks",
    # Health & Other Tech
    "tempus", "flatiron", "veracyte", "recursion", "benchling",
    "benchsci", "insitro", "manifold-bio",
    # E-commerce & Marketplace
    "faire", "shipbob", "flexport", "project44", "stord",
    "loop-returns", "returnly", "narvar",
]

# ─── ASHBY COMPANIES ────────────────────────────────────────────────────────
ASHBY_COMPANIES = [
    # AI & ML
    "openai", "anthropic", "scale-ai", "cohere", "mistral",
    "together-ai", "modal", "replicate", "huggingface",
    "anyscale", "weights-biases", "neptune-ai",
    # Fintech
    "column", "lithic", "unit", "synctera", "treasury-prime",
    "modern-treasury", "increase", "moov", "finix",
    # Cybersecurity
    "sublime-security", "veza", "astrix", "oligo", "armo",
    "ox-security", "cycode", "apiiro", "legit-security",
    # Data
    "tinybird", "clickhouse", "motherduck", "turso",
    "neon", "xata", "tembo",
    # SaaS & Dev Tools
    "retool", "airplane", "interval", "tooljet", "budibase",
    "appsmith", "superblocks", "permit-io", "cerbos", "oso",
    # Infrastructure
    "depot", "render", "railway", "fly-io", "porter",
    "coherence", "gimlet",
    # Analytics
    "june", "koala", "hyperline", "primer", "mutiny",
    "statsig", "eppo", "growthbook", "split",
]

US_KEYWORDS = [
    "remote", "united states", "us", "new york", "san francisco",
    "austin", "chicago", "seattle", "hybrid", "bellevue",
    "menlo park", "boston", "denver", "atlanta", "miami",
    "los angeles", "dallas", "washington dc", "nationwide"
]

RELEVANT_TITLES = [
    "data analyst", "reporting analyst", "bi analyst",
    "business intelligence", "security analyst",
    "threat intelligence", "compliance analyst", "risk analyst",
    "analytics engineer", "data operations"
]

EXCLUDE_TITLES = [
    "senior", "staff", "principal", "director", "manager",
    "lead", "sr.", " ii", " iii", " iv", "intern", "internship",
    "vp ", "vice president", "head of"
]

SEEN_JOBS_FILE = os.path.expanduser("~/seen_jobs.json")

def load_seen_jobs():
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen_jobs(seen):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen), f, indent=2)

def make_job_uid(source, company, job_id):
    return f"{source}_{company}_{job_id}"

def strip_html(html):
    return re.sub(r'<[^>]+>', ' ', html)

def is_relevant(title, location):
    title = title.lower()
    location = location.lower()
    if not any(t in title for t in RELEVANT_TITLES):
        return False
    if any(e in title for e in EXCLUDE_TITLES):
        return False
    if not any(us in location for us in US_KEYWORDS):
        return False
    return True

# ─── GREENHOUSE SCRAPER ──────────────────────────────────────────────────────
def scrape_greenhouse(seen, new_seen, proceed_jobs):
    print(f"\n🌱 Scraping Greenhouse ({len(GREENHOUSE_COMPANIES)} companies)...")
    for company in GREENHOUSE_COMPANIES:
        try:
            r = httpx.get(
                f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs",
                timeout=10
            )
            jobs = r.json().get("jobs", [])
            for j in jobs:
                if not is_relevant(j["title"], j["location"]["name"]):
                    continue

                uid = make_job_uid("gh", company, j["id"])
                new_seen.add(uid)
                if uid in seen:
                    continue

                detail = httpx.get(
                    f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{j['id']}",
                    timeout=10
                ).json()
                description = strip_html(detail.get("content", ""))
                result = score_job(j["title"], description)

                icon = "✅" if result["decision"] == "✅ PROCEED" else "❌"
                print(f"  {icon} [GH] {company.upper()} — {j['title']}")

                if result["decision"] == "✅ PROCEED":
                    proceed_jobs.append({
                        "uid": uid,
                        "source": "greenhouse",
                        "company": company,
                        "title": j["title"],
                        "url": j["absolute_url"],
                        "location": j["location"]["name"],
                        "description": description,
                        "score": result
                    })
        except Exception:
            continue

# ─── LEVER SCRAPER ───────────────────────────────────────────────────────────
def scrape_lever(seen, new_seen, proceed_jobs):
    print(f"\n⚙️  Scraping Lever ({len(LEVER_COMPANIES)} companies)...")
    for company in LEVER_COMPANIES:
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
                location = (
                    j.get("categories", {}).get("location", "") or
                    j.get("workplaceType", "")
                )

                if not is_relevant(title, location):
                    continue

                uid = make_job_uid("lv", company, j["id"])
                new_seen.add(uid)
                if uid in seen:
                    continue

                description = strip_html(
                    j.get("descriptionBody", "") or j.get("description", "")
                )
                result = score_job(title, description)

                icon = "✅" if result["decision"] == "✅ PROCEED" else "❌"
                print(f"  {icon} [LV] {company.upper()} — {title}")

                if result["decision"] == "✅ PROCEED":
                    proceed_jobs.append({
                        "uid": uid,
                        "source": "lever",
                        "company": company,
                        "title": title,
                        "url": j.get("hostedUrl", ""),
                        "location": location,
                        "description": description,
                        "score": result
                    })
        except Exception:
            continue

# ─── ASHBY SCRAPER ───────────────────────────────────────────────────────────
def scrape_ashby(seen, new_seen, proceed_jobs):
    print(f"\n🔷 Scraping Ashby ({len(ASHBY_COMPANIES)} companies)...")
    for company in ASHBY_COMPANIES:
        try:
            r = httpx.post(
                "https://api.ashbyhq.com/posting-api/job-board",
                json={"organizationHostedJobsPageName": company},
                timeout=10
            )
            data = r.json()
            jobs = data.get("jobPostings", [])

            for j in jobs:
                title = j.get("title", "")
                location = j.get("location", "") or j.get("locationName", "")

                if not is_relevant(title, location):
                    continue

                uid = make_job_uid("ash", company, j["id"])
                new_seen.add(uid)
                if uid in seen:
                    continue

                description = strip_html(
                    j.get("descriptionHtml", "") or j.get("description", "")
                )
                result = score_job(title, description)

                icon = "✅" if result["decision"] == "✅ PROCEED" else "❌"
                print(f"  {icon} [ASH] {company.upper()} — {title}")

                if result["decision"] == "✅ PROCEED":
                    proceed_jobs.append({
                        "uid": uid,
                        "source": "ashby",
                        "company": company,
                        "title": title,
                        "url": j.get("jobUrl", ""),
                        "location": location,
                        "description": description,
                        "score": result
                    })
        except Exception:
            continue

# ─── MAIN ────────────────────────────────────────────────────────────────────
def run():
    seen = load_seen_jobs()
    new_seen = set()
    proceed_jobs = []

    total = len(GREENHOUSE_COMPANIES) + len(LEVER_COMPANIES) + len(ASHBY_COMPANIES)
    print(f"\n🚀 Job Agent Starting — {total} companies across 3 platforms")
    print(f"{'='*60}")

    scrape_greenhouse(seen, new_seen, proceed_jobs)
    scrape_lever(seen, new_seen, proceed_jobs)
    scrape_ashby(seen, new_seen, proceed_jobs)

    with open("proceed_jobs.json", "w") as f:
        json.dump(proceed_jobs, f, indent=2)

    save_seen_jobs(seen | new_seen)

    print(f"\n{'='*60}")
    print(f"✅ {len(proceed_jobs)} new jobs to process")
    print(f"📦 {len(seen | new_seen)} total jobs tracked (no repeats ever)")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run()

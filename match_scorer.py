# match_scorer.py

MY_SKILLS = {
    "sql", "tableau", "power bi", "excel", "python",
    "data cleaning", "dashboards", "reporting", "automation",
    "scripting", "data visualization", "etl", "looker",
    "analytics", "metrics", "kpi", "pivot"
}

MY_SECURITY_SKILLS = {
    "security+", "comptia", "cybersecurity", "log analysis",
    "compliance", "risk", "threat", "siem", "vulnerability"
}

MY_TOOLS = {"tableau", "power bi", "excel", "sql", "python", "jupyter", "looker"}

MY_YEARS = 1.5

def score_job(title: str, description: str) -> dict:
    text = (title + " " + description).lower()

    # 1. Skill overlap (40pts) — 7pts each, max 40
    skill_hits = [s for s in MY_SKILLS if s in text]
    skill_score = min(40, len(skill_hits) * 7)

    # 2. Tool overlap (20pts) — 5pts each, max 20
    tool_hits = [t for t in MY_TOOLS if t in text]
    tool_score = min(20, len(tool_hits) * 5)

    # 3. Experience alignment (15pts)
    # FIXED: 3 years is NOT senior — only penalize 5+ years or explicit senior titles
    if any(x in text for x in ["0-1", "0-2", "1-2", "1-3", "entry level", "entry-level", "junior", "new grad"]):
        exp_score = 15  # perfect fit
    elif any(x in text for x in ["2-4", "2-3", "3-4", "2+ year", "3 year", "3+ year", "2-5"]):
        exp_score = 11  # slight stretch, still viable
    elif any(x in text for x in ["4-6", "4+ year", "5 year", "5+ year"]):
        exp_score = 6   # harder but possible
    elif any(x in text for x in ["7+", "8+", "10+", "senior", "staff", "principal"]):
        exp_score = 2   # too senior
    else:
        exp_score = 10  # not specified — give benefit of doubt

    # 4. Domain relevance (10pts)
    domain_keywords = [
        "analyst", "analytics", "reporting", "dashboard",
        "business intelligence", "bi ", "insights", "data ops"
    ]
    domain_score = 10 if any(w in text for w in domain_keywords) else 4

    # 5. Security boost (5pts)
    sec_hits = [s for s in MY_SECURITY_SKILLS if s in text]
    security_score = min(5, len(sec_hits) * 2)

    # 6. Keyword frequency (10pts) — deduplicated
    unique_hits = list(set(skill_hits + tool_hits))
    kw_score = min(10, len(unique_hits) * 1.5)

    total = skill_score + tool_score + exp_score + domain_score + security_score + kw_score
    total = round(min(100, total), 1)

    # Threshold: 65 (loosened from 70 to catch more valid matches)
    return {
        "total": total,
        "decision": "✅ PROCEED" if total >= 65 else "❌ SKIP",
        "skill_hits": skill_hits,
        "tool_hits": tool_hits,
        "security_hits": sec_hits,
        "breakdown": {
            "skills": skill_score,
            "tools": tool_score,
            "experience": exp_score,
            "domain": domain_score,
            "security_boost": security_score,
            "keywords": round(kw_score, 1)
        }
    }

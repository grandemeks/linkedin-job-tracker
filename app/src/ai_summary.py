import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_job_summary(job: dict) -> dict:
    """Generise AI summary za job poziciju."""

    prompt = f"""
Analiziraj ovu job poziciju i vrati strukturiran odgovor.

TITLE: {job['title']}
COMPANY: {job['company']}
DESCRIPTION: {job['description'][:3000]}

Vrati odgovor u TACNO ovom formatu (bez dodatnog teksta):

SUMMARY: [2-3 recenice o poziciji]
COMPANY_INFO: [1-2 recenice o kompaniji]
KEY_REQUIREMENTS: [top 5 zahtjeva, odvojeni sa |]
KEY_BENEFITS: [top 3 benefita, odvojeni sa |]
WORK_TYPE: [Remote / Hybrid / On-site / Not specified]
RATING: [broj od 1 do 5]
RATING_REASON: [1 recenica zasto ta ocjena]
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Ti si expert career advisor koji analizira job pozicije za DevOps inzenjere. Budi koncizan i precizan."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,
        max_tokens=1024,
    )

    raw = response.choices[0].message.content
    return parse_ai_response(raw, job)


def parse_ai_response(raw: str, job: dict) -> dict:
    """Parsira AI response u strukturiran dict."""
    result = {
        "title": job["title"],
        "company": job["company"],
        "link": job["link"],
        "summary": "",
        "company_info": "",
        "key_requirements": [],
        "key_benefits": [],
        "work_type": "Not specified",
        "rating": 0,
        "rating_reason": "",
    }

    for line in raw.strip().split("\n"):
        if line.startswith("SUMMARY:"):
            result["summary"] = line.replace("SUMMARY:", "").strip()
        elif line.startswith("COMPANY_INFO:"):
            result["company_info"] = line.replace("COMPANY_INFO:", "").strip()
        elif line.startswith("KEY_REQUIREMENTS:"):
            raw_req = line.replace("KEY_REQUIREMENTS:", "").strip()
            result["key_requirements"] = [r.strip()
                                          for r in raw_req.split("|")]
        elif line.startswith("KEY_BENEFITS:"):
            raw_ben = line.replace("KEY_BENEFITS:", "").strip()
            result["key_benefits"] = [b.strip() for b in raw_ben.split("|")]
        elif line.startswith("WORK_TYPE:"):
            result["work_type"] = line.replace("WORK_TYPE:", "").strip()
        elif line.startswith("RATING:"):
            try:
                result["rating"] = int(line.replace("RATING:", "").strip())
            except BaseException:
                result["rating"] = 0
        elif line.startswith("RATING_REASON:"):
            result["rating_reason"] = line.replace(
                "RATING_REASON:", "").strip()

    return result

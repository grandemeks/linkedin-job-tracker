import feedparser
import hashlib
import json
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# RSS Feed sources (legalni sources)
RSS_FEEDS = {
    "remotive": "https://remotive.com/remote-jobs/feed/devops",
    "weworkremotely": "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
}

KEYWORDS = [k.strip().lower() for k in os.getenv("KEYWORDS", "devops,sre,platform engineer").split(",")]


def get_job_id(title: str, company: str) -> str:
    """Generiše unique ID za svaki job da izbjegnemo duplikate."""
    raw = f"{title}-{company}".lower()
    return hashlib.md5(raw.encode()).hexdigest()


def parse_feed(feed_url: str) -> list[dict]:
    """Parsira RSS feed i vraca listu jobova."""
    jobs = []
    
    # feedparser ne salje User-Agent pa bivamo blokirani
    import requests
    response = requests.get(feed_url, headers={"User-Agent": "Mozilla/5.0"})
    feed = feedparser.parse(response.content)

    for entry in feed.entries:
        title = entry.get("title", "")
        company = entry.get("author", entry.get("company", "Unknown"))
        link = entry.get("link", "")
        summary = entry.get("summary", "")
        published = entry.get("published", str(datetime.now()))

        # Filter by keywords
        title_lower = title.lower()
        summary_lower = summary.lower()
        if not any(kw in title_lower or kw in summary_lower for kw in KEYWORDS):
            continue

        job = {
            "id": get_job_id(title, company),
            "title": title,
            "company": company,
            "link": link,
            "description": summary,
            "published": published,
            "source": feed_url,
        }
        jobs.append(job)

    return jobs


def get_all_jobs() -> list[dict]:
    """Skuplja jobove sa svih feed-ova."""
    all_jobs = []
    for source, url in RSS_FEEDS.items():
        print(f"[Scraper] Fetching jobs from {source}...")
        jobs = parse_feed(url)
        print(f"[Scraper] Found {len(jobs)} matching jobs from {source}")
        all_jobs.extend(jobs)
    return all_jobs


# Seen jobs cache (u produkciji ovo ide u Redis ili file)
SEEN_JOBS_FILE = "/tmp/seen_jobs.json"


def load_seen_jobs() -> set:
    if os.path.exists(SEEN_JOBS_FILE):
        with open(SEEN_JOBS_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_seen_jobs(seen: set):
    with open(SEEN_JOBS_FILE, "w") as f:
        json.dump(list(seen), f)


def get_new_jobs() -> list[dict]:
    """Vraca samo nove jobove koje jos nismo vidjeli."""
    seen = load_seen_jobs()
    all_jobs = get_all_jobs()
    new_jobs = [j for j in all_jobs if j["id"] not in seen]

    # Sacuvaj nove u seen
    seen.update(j["id"] for j in new_jobs)
    save_seen_jobs(seen)

    print(f"[Scraper] {len(new_jobs)} new jobs found.")
    return new_jobs
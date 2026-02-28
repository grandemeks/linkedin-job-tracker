import time
import os
import schedule
from dotenv import load_dotenv
from scraper import get_new_jobs
from ai_summary import generate_job_summary

load_dotenv()

CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_MINUTES", "30"))


def process_jobs():
    print("\n[Main] Starting job check...")
    new_jobs = get_new_jobs()

    if not new_jobs:
        print("[Main] No new jobs found. Waiting for next check...")
        return

    print(f"[Main] Processing {len(new_jobs)} new jobs...")

    for job in new_jobs:
        try:
            print(f"\n[Main] Analyzing: {job['title']} @ {job['company']}")
            summary = generate_job_summary(job)

            print("\n" + "="*50)
            print(f"Title:   {summary['title']} @ {summary['company']}")
            print(f"Type:    {summary['work_type']}")
            print(f"Rating:  {summary['rating']}/5")
            print(f"Summary: {summary['summary']}")
            print(f"Link:    {summary['link']}")
            print("="*50)

            time.sleep(2)

        except Exception as e:
            print(f"[Main] Error processing job {job['title']}: {e}")
            continue


def main():
    print(f"[Main] Job Tracker started! Checking every {CHECK_INTERVAL} minutes.")
    process_jobs()
    schedule.every(CHECK_INTERVAL).minutes.do(process_jobs)

    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()
import sys
from app.jobs.languageJob import run_language_cron_job
from app.jobs.locationJob import run_location_cron_job
from app.jobs.newsJob import run_news_cron_job


def main():
    if len(sys.argv) < 2:
        print("Usage: python script.py [language|location|news]")
        sys.exit(1)

    job_type = sys.argv[1]

    if job_type == 'language':
        print("LOG: Running language job...")
        run_language_cron_job()
    elif job_type == 'location':
        print("LOG: Running location job...")
        run_location_cron_job()
    elif job_type == 'news':
        print("LOG: Running news job...")
        run_news_cron_job()
    else:
        print("Invalid argument. Please use 'language' or 'location'.")
        sys.exit(1)


if __name__ == "__main__":
    main()

import sys
from app.jobs.languageJob import run_language_cron_job

def main():
    if len(sys.argv) != 2:
        print("Usage: python script.py [language|location]")
        sys.exit(1)

    job_type = sys.argv[1]

    if job_type == 'language':
        print("LOG: Running language job...")
        run_language_cron_job()
    elif job_type == 'location':
        run_language_cron_job()
    else:
        print("Invalid argument. Please use 'language' or 'location'.")
        sys.exit(1)

if __name__ == "__main__":
    main()
"""scrape_and_save.py
Run the Selenium scraper and write the results to JSON and CSV files only.

Usage:
    python scrape_and_save.py

Environment variables (same as scrape_and_load.py):
    ARW_USERNAME   AnnuityRateWatch username
    ARW_PASSWORD   AnnuityRateWatch password

The script overwrites output/annuity_data.json and output/annuity_data.csv on
each run so you always have the latest snapshot.
"""

import os
import json
from dotenv import load_dotenv
from paginated_selenium_scraper import PaginatedSeleniumAnnuityRateWatchScraper

# Load .env file if present
load_dotenv()


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def main():
    # 1. Credentials
    username = _env("ARW_USERNAME")
    password = _env("ARW_PASSWORD")
    if not username or not password:
        print("❌ Set ARW_USERNAME and ARW_PASSWORD as environment variables.")
        return

    # 2. Scrape
    scraper = PaginatedSeleniumAnnuityRateWatchScraper(username, password, headless=True)
    print("🚀 Starting scraper …")
    data = scraper.run()

    if not data:
        print("❌ No data scraped – nothing to save.")
        return

    # 3. Save files (overwrite on each run)
    os.makedirs("output", exist_ok=True)
    scraper.save_to_json(data, "annuity_data.json")
    scraper.save_to_csv(data, "annuity_data.csv")

    print(f"✅ Saved {len(data)} rows to output/annuity_data.json and .csv")

    # 4. Show sample row
    print("\n📋 Sample row:")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

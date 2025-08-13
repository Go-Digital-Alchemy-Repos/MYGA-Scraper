"""scrape_and_load.py
Run the Selenium scraper and push results into a MySQL database.

Make sure to: ``pip install -r requirements.txt`` first.

You can adjust credentials and DB config below or load them from environment
variables / CLI arguments as needed for production.
"""

import os
import json
from typing import Dict
from dotenv import load_dotenv

# Load environment variables from a .env file if present
load_dotenv()

from paginated_selenium_scraper import PaginatedSeleniumAnnuityRateWatchScraper
# Decide which backend to use via env var DB_TYPE (mysql|mssql)
DB_TYPE = os.environ.get("DB_TYPE", "mysql").lower()

if DB_TYPE == "mysql":
    from db_utils import save_annuity_data_to_mysql as save_fn
elif DB_TYPE == "mssql":
    from mssql_utils import save_annuity_data_to_mssql as save_fn
else:
    raise ValueError("DB_TYPE must be 'mysql' or 'mssql'")


def _env(key: str, default: str = "") -> str:
    return os.environ.get(key, default)


def main():
    # 1. Scraper credentials (username/password)
    username = _env("ARW_USERNAME", "calebshump")  # <-- replace with env vars in practice
    password = _env("ARW_PASSWORD", "TacoTuesday")

    # 2. Database configuration depending on backend
    if DB_TYPE == "mysql":
        db_config: Dict[str, str] = {
            "host": _env("MYSQL_HOST", "localhost"),
            "user": _env("MYSQL_USER", "root"),
            "password": _env("MYSQL_PASSWORD", "password"),
            "database": _env("MYSQL_DATABASE", "annuity_data"),
        }
    else:  # mssql
        db_config = {
            "host": _env("MSSQL_HOST", "localhost"),
            "port": int(_env("MSSQL_PORT", "1433")),
            "user": _env("MSSQL_USER", "sa"),
            "password": _env("MSSQL_PASSWORD", "TestPass123!"),
            "database": _env("MSSQL_DATABASE", "annuity_data"),
        }

    # 3. Initialize scraper (headless by default)
    scraper = PaginatedSeleniumAnnuityRateWatchScraper(username, password, headless=True)
    print("🚀 Starting scraper…")
    data = scraper.run(max_pages=None)

    # 4. Persist data
    if not data:
        print("❌ No data scraped – aborting DB insertion.")
        return

    print(f"✅ Scraped {len(data)} rows, saving to {DB_TYPE.upper()}…")
    save_fn(data, db_config, table_name="annuities", recreate_table=True)

    # 5. Optional: dump a preview to stdout
    print("\n📋 Sample row:")
    print(json.dumps(data[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

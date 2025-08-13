# MYGA AnnuityRateWatch Web Scraper

A Python web scraper for extracting annuity data from the Life Innovators AnnuityRateWatch website using Selenium browser automation.

## Overview

This scraper uses Selenium WebDriver to handle the complex authentication and JavaScript-loaded content of the AnnuityRateWatch website. It automatically logs in, navigates through all pages of annuity data, and exports the results to JSON format.

## Features

- **Browser Automation**: Full JavaScript execution with Selenium WebDriver
- **Robust Authentication**: Handles complex login forms with CSRF tokens
- **Complete Pagination**: Automatic traversal of all data pages (1-36)
- **Smart Table Detection**: Targets main data tables while avoiding navigation elements
- **Database Persistence**: Push data directly into **MySQL** *or* **Microsoft SQL Server**
- **Dual Format Export**: Saves data in JSON and CSV as backups
- **Error Recovery**: Robust handling of network issues and timeouts
- **Debug Support**: Screenshots and HTML dumps for troubleshooting
- **Organized Output**: All results saved to `output/` directory

## Requirements

| Component | Purpose |
|-----------|---------|
| Python 3.9+ | scraper & utils |
| Chrome browser | required for Selenium headless mode |
| Valid AnnuityRateWatch account | login |
| **MySQL** *or* **SQL Server (Docker or native)** | optional – to persist data |
| MySQL driver: `mysql-connector-python` | auto-installed by `requirements.txt` |
| SQL Server driver: **ODBC Driver 18** + `pyodbc` | see below |

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. If you plan to save into SQL Server, install Microsoft’s ODBC driver (one-time):

macOS (Homebrew)

```bash
brew tap microsoft/mssql-release
ACCEPT_EULA=Y brew install msodbcsql18    # ODBC Driver 18
```

Ubuntu

```bash
curl https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
curl https://packages.microsoft.com/config/ubuntu/22.04/prod.list \
  | sudo tee /etc/apt/sources.list.d/mssql-release.list
sudo apt update
sudo ACCEPT_EULA=Y apt install msodbcsql18
```

Skip this step if you only use MySQL.

## Usage

### Quick Scrape & Load (recommended)

`scrape_and_load.py` combines scraping with database persistence. First export environment variables, then run:

```bash
# choose backend (mysql|mssql) – default is mysql
export DB_TYPE=mssql

# Credentials (examples)
export ARW_USERNAME="your_arw_user"
export ARW_PASSWORD="your_arw_pass"

# SQL Server
export MSSQL_USER=sa
export MSSQL_PASSWORD=TestPass123!

python scrape_and_load.py
```

The script will:
1. Login and scrape all pages
2. Recreate table `annuities` inside the configured database
3. Insert rows (numeric columns typed INT/DECIMAL automatically)
4. Also save JSON + CSV backups in `output/`

To use MySQL instead set `DB_TYPE=mysql` and the matching `MYSQL_*` vars.

### Legacy Scraping Only

You can still run the standalone scraper:

```bash
python paginated_selenium_scraper.py
```
... and call the DB helpers manually if desired.

### Programmatic Usage

```python
from paginated_selenium_scraper import PaginatedSeleniumAnnuityRateWatchScraper

scraper = PaginatedSeleniumAnnuityRateWatchScraper("username", "password")
data = scraper.run()

# Save in both formats
scraper.save_to_json(data, "my_data.json")
scraper.save_to_csv(data, "my_data.csv")
```

## Database Persistence Helpers

### MySQL

```python
from db_utils import save_annuity_data_to_mysql
save_annuity_data_to_mysql(data, {
    "host": "localhost",
    "user": "root",
    "password": "password",
    "database": "annuity_data"
})
```

### Microsoft SQL Server

```python
from mssql_utils import save_annuity_data_to_mssql
save_annuity_data_to_mssql(data, {
    "host": "localhost",
    "port": 1433,
    "user": "sa",
    "password": "TestPass123!",
    "database": "annuity_data"
})
```

Both helpers:
* Create the database/table if missing.
* Infer numeric column types (INT or DECIMAL) automatically.
* Accept `recreate_table=True` to drop/rebuild the table each run (default in `scrape_and_load.py`).

## Docker Quick-Start (SQL Server example)

```yaml
# docker-compose.yml
version: "3.9"
services:
  sqlserver:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      ACCEPT_EULA: "Y"
      MSSQL_SA_PASSWORD: "TestPass123!"
    ports:
      - "1433:1433"
  scraper:
    build: .
    environment:
      DB_TYPE: mssql
      ARW_USERNAME: ${ARW_USERNAME}
      ARW_PASSWORD: ${ARW_PASSWORD}
      MSSQL_USER: sa
      MSSQL_PASSWORD: TestPass123!
    depends_on:
      sqlserver:
        condition: service_started
```

Then: `docker compose up --build`.

## Data Structure

The scraper extracts annuity product data including:
- Company/Product Name
- AM Best Rating
- Max Issue Age  
- Min Premium
- Rate information and product features

Output format:
```json
[
  {
    "page_number": 1,
    "table_index": 0,
    "row_index": 0,
    "Company_Product": "Company Name - Product Name",
    "AM_Best": "A+",
    "Max_Issue_Age": "85",
    "Min_Premium": "$10,000"
  }
]
```

## File Organization

```
MYGA/
├── paginated_selenium_scraper.py  # Main scraper script
├── requirements.txt              # Python dependencies
├── README.md                     # This file
└── output/                       # All results and debug files
    ├── annuity_data_*.json       # Scraped data (JSON format)
    ├── annuity_data_*.csv        # Scraped data (CSV format)
    ├── debug_*.html              # Page source dumps
    └── screenshots/              # Debug screenshots
```

## Expected Results

- **Total Records**: ~1,793 annuity products
- **Pages**: 36 pages (Page 1: ~10 records, Pages 2+: ~62 records each)
- **Processing Time**: ~5-10 minutes for full scrape
- **File Size**: ~500KB-1MB JSON output

## Troubleshooting

### Login Issues
- Verify credentials for AnnuityRateWatch account
- Check for CAPTCHA or additional security measures
- Ensure account has access to CD-type annuities section

### Data Extraction Issues
- Check if website structure has changed
- Review debug screenshots in `output/screenshots/`
- Verify table selection logic in scraper code

### Selenium Issues
- Ensure Chrome browser is installed and up-to-date
- Check ChromeDriver compatibility
- Increase wait times for slow network connections

## Important Notes

- **Authentication Required**: Valid AnnuityRateWatch membership needed
- **Rate Limiting**: Built-in delays to respect server resources
- **Legal Compliance**: Ensure compliance with website terms of service
- **Data Verification**: Always validate extracted data accuracy

## License

Educational and legitimate business use only. Respect website terms of service and rate limits.

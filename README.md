# MYGA AnnuityRateWatch Web Scraper

A Python web scraper for extracting annuity data from the Life Innovators AnnuityRateWatch website using Selenium browser automation.

## Overview

This scraper uses Selenium WebDriver to handle the complex authentication and JavaScript-loaded content of the AnnuityRateWatch website. It automatically logs in, navigates through all pages of annuity data, and exports the results to JSON format.

## Features

- **Browser Automation**: Full JavaScript execution with Selenium WebDriver
- **Robust Authentication**: Handles complex login forms with CSRF tokens
- **Complete Pagination**: Automatic traversal of all data pages (1-36)
- **Smart Table Detection**: Targets main data tables while avoiding navigation elements
- **Dual Format Export**: Saves data in both JSON and CSV formats
- **Error Recovery**: Robust handling of network issues and timeouts
- **Debug Support**: Screenshots and HTML dumps for troubleshooting
- **Organized Output**: All results saved to `output/` directory

## Requirements

- Python 3.7+
- Chrome browser (for Selenium)
- Valid AnnuityRateWatch account credentials

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome browser is installed (ChromeDriver will be automatically managed)

## Usage

### Command Line

```bash
python paginated_selenium_scraper.py
```

This will:
1. Prompt for username/password securely
2. Login to the AnnuityRateWatch website
3. Scrape all pages (1-36) with ~1,793 total records
4. Save results to both `output/annuity_data_[timestamp].json` and `output/annuity_data_[timestamp].csv`
5. Generate debug files if issues occur

### Programmatic Usage

```python
from paginated_selenium_scraper import PaginatedSeleniumAnnuityRateWatchScraper

scraper = PaginatedSeleniumAnnuityRateWatchScraper("username", "password")
data = scraper.run()

# Save in both formats
scraper.save_to_json(data, "my_data.json")
scraper.save_to_csv(data, "my_data.csv")
```

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

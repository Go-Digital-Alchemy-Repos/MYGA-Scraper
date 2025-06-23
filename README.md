# MYGA AnnuityRateWatch Web Scraper

A collection of Python web scrapers for extracting annuity data from the Life Innovators AnnuityRateWatch website and converting it to JSON format.

## Project Overview

This project evolved through multiple iterations to handle the complex authentication and data loading mechanisms of the AnnuityRateWatch website. It includes several scraper implementations, each designed to overcome specific challenges encountered during development.

## Scraper Implementations

### 1. Basic HTTP Scraper (`annuity_scraper.py`)
- **Purpose**: Initial attempt using requests library for HTTP-based scraping
- **Limitations**: Cannot handle JavaScript-loaded content
- **Status**: Functional for login but limited data extraction

### 2. AJAX Scraper (`ajax_scraper.py`)
- **Purpose**: Attempts to replicate AJAX calls made by the website
- **Features**: Discovered backend endpoints and parameters
- **Limitations**: AJAX responses often empty due to session/state requirements
- **Status**: Research tool for understanding backend API

### 3. Selenium Scraper (`selenium_scraper.py`)
- **Purpose**: Browser automation for handling dynamic content
- **Features**: Full JavaScript execution, reliable login detection
- **Limitations**: Single page scraping only
- **Status**: Functional baseline implementation

### 4. Paginated Selenium Scraper (`paginated_selenium_scraper.py`) ⭐ **RECOMMENDED**
- **Purpose**: Complete solution with pagination support
- **Features**: 
  - Automated login with robust detection
  - Full pagination through all 36 pages
  - Proper table selection and data extraction
  - Error handling and recovery
- **Status**: Primary production scraper

## Features

- **Multi-method Authentication**: Handles complex login forms with CSRF tokens
- **JavaScript Support**: Full browser automation with Selenium WebDriver
- **Pagination**: Automatic traversal of all data pages (1-36)
- **Table Detection**: Smart selection of main data tables vs navigation tables
- **JSON Export**: Structured output with metadata
- **Error Recovery**: Robust handling of network issues and timeouts
- **Organized Output**: All results saved to `output/` directory

## Requirements

- Python 3.7+
- Chrome browser (for Selenium)
- Required packages in `requirements.txt`

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure Chrome browser is installed (for Selenium WebDriver)

## Usage

### Recommended: Paginated Selenium Scraper

```bash
python paginated_selenium_scraper.py
```

This will:
1. Prompt for username/password securely
2. Login to the website
3. Scrape all pages (1-36) with ~1,793 total records
4. Save results to `output/annuity_data_[timestamp].json`
5. Generate debug screenshots if needed

### Alternative Scrapers

For testing or specific use cases:

```bash
# Basic HTTP scraper
python annuity_scraper.py

# AJAX research tool
python ajax_scraper.py

# Single page Selenium
python selenium_scraper.py
```

### Programmatic Usage

```python
from paginated_selenium_scraper import PaginatedAnnuityScraper

scraper = PaginatedAnnuityScraper("username", "password")
data = scraper.scrape_all_pages()
scraper.save_to_json(data, "output/my_data.json")
```

## Data Structure

The scraper extracts annuity product data with columns including:
- Company/Product Name
- AM Best Rating
- Max Issue Age  
- Min Premium
- Various rate and feature information

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
    "Min_Premium": "$10,000",
    // ... additional columns
  }
]
```

## Project Evolution

This project demonstrates iterative problem-solving in web scraping:

1. **Initial HTTP Approach**: Standard requests-based scraping
2. **AJAX Discovery**: Reverse-engineering backend API calls
3. **Selenium Implementation**: Browser automation for JavaScript content
4. **Pagination Solution**: Handling multi-page data sets
5. **Table Selection**: Targeting correct data tables vs navigation elements

## File Organization

```
MYGA/
├── annuity_scraper.py           # Basic HTTP scraper
├── ajax_scraper.py              # AJAX research tool
├── selenium_scraper.py          # Single page Selenium
├── paginated_selenium_scraper.py # Main production scraper
├── test_alternative_urls.py     # URL testing utility
├── run_scraper.py              # Execution wrapper
├── requirements.txt            # Dependencies
├── README.md                   # This file
└── output/                     # All results and debug files
    ├── annuity_data_*.json     # Scraped data
    ├── debug_*.html            # Page source dumps
    └── screenshots/            # Debug screenshots
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

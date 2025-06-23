# AnnuityRateWatch Web Scraper

A Python web scraper for extracting table data from the Life Innovators AnnuityRateWatch website and converting it to JSON format.

## Features

- **Authentication handling**: Automatically logs into the AnnuityRateWatch website
- **Pagination support**: Scrapes multiple pages automatically
- **Table extraction**: Finds and extracts all data tables from each page
- **JSON output**: Converts table data to structured JSON format
- **Error handling**: Robust error handling and session management
- **Configurable**: Support for custom page ranges and output files

## Requirements

- Python 3.7+
- Required packages listed in `requirements.txt`

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Usage

Basic usage:
```bash
python annuity_scraper.py <username> <password>
```

With options:
```bash
python annuity_scraper.py <username> <password> --start-page 1 --max-pages 5 --output my_data.json
```

### Command Line Options

- `username`: Your AnnuityRateWatch username (required)
- `password`: Your AnnuityRateWatch password (required)
- `--start-page`: Starting page number (default: 1)
- `--max-pages`: Maximum number of pages to scrape (optional, scrapes all if not specified)
- `--output` or `-o`: Output JSON filename (optional, auto-generates if not specified)

### Programmatic Usage

```python
from annuity_scraper import AnnuityRateWatchScraper

# Create scraper instance
scraper = AnnuityRateWatchScraper("your_username", "your_password")

# Scrape specific page range
data = scraper.scrape_all_pages(start_page=1, max_pages=3)

# Save to JSON
scraper.save_to_json(data, "annuity_data.json")
```

## Output Format

The scraper extracts table data and converts it to JSON with the following structure:

```json
[
  {
    "table_index": 0,
    "row_index": 0,
    "page_number": 1,
    "Column_Name_1": "Cell Value 1",
    "Column_Name_2": "Cell Value 2",
    "Column_Name_3": "Cell Value 3",
    "Column_Name_1_links": [
      {
        "text": "Link Text",
        "href": "/link/url"
      }
    ]
  }
]
```

Each row includes:
- `table_index`: Index of the table on the page (if multiple tables exist)
- `row_index`: Index of the row within the table
- `page_number`: Page number where this row was found
- Column data with actual column names as keys
- Any links found in cells are captured separately with `_links` suffix

## Features

### Authentication
- Handles login form detection and submission
- Captures CSRF tokens and hidden form fields
- Maintains session across page requests
- Auto-retry login if session expires

### Table Detection
- Automatically finds data tables on each page
- Skips navigation/layout tables
- Extracts column headers from `<th>` or first `<td>` row
- Captures both text content and links within cells

### Pagination
- Automatically increments page numbers
- Stops when reaching empty pages or errors
- Configurable maximum page limits
- Polite delays between requests

### Error Handling
- Graceful handling of network errors
- Login failure detection
- Session expiration handling
- Detailed error messages and logging

## Example Output

Running the scraper will produce output like:

```
Starting AnnuityRateWatch scraper...
Login successful!
Scraping page 1: https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm?pageNo=1
Extracted 25 rows from page 1
Scraping page 2: https://members.annuityratewatch.com/lifeinnovators/instn/cd-type-annuities.htm?pageNo=2
Extracted 25 rows from page 2
...
Scraping completed! Total rows extracted: 150
Data saved to annuity_data_1703123456.json
```

## Important Notes

- **Rate Limiting**: The scraper includes delays between requests to be respectful to the server
- **Authentication Required**: You must have valid AnnuityRateWatch credentials
- **Legal Compliance**: Ensure you have permission to scrape this data and comply with the website's terms of service
- **Data Accuracy**: Always verify the extracted data for accuracy

## Troubleshooting

### Login Issues
- Verify your username and password are correct
- Check if the website login form has changed
- Ensure your account has access to the specific pages

### No Data Extracted
- The page might not contain table data
- Tables might be dynamically loaded with JavaScript (this scraper handles static HTML only)
- Check if you're accessing the correct URL

### Session Expiration
- The scraper will automatically attempt to re-login
- If re-login fails repeatedly, check your credentials

## License

This tool is for educational and legitimate business purposes only. Please respect the website's terms of service and robots.txt file. # MYGA-Scraper

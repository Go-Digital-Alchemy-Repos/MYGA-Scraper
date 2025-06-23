#!/usr/bin/env python3
"""
Example usage of the AnnuityRateWatch scraper
"""

from annuity_scraper import AnnuityRateWatchScraper
import json

def example_usage():
    # Replace with your actual credentials
    username = "your_username"
    password = "your_password"
    
    # Create scraper instance
    scraper = AnnuityRateWatchScraper(username, password)
    
    # Option 1: Scrape just a few pages
    print("Scraping first 3 pages...")
    data = scraper.scrape_all_pages(start_page=1, max_pages=3)
    
    if data:
        print(f"Extracted {len(data)} total rows")
        
        # Save to JSON
        scraper.save_to_json(data, "sample_annuity_data.json")
        
        # Print first few rows as sample
        print("\nFirst 3 rows of data:")
        for i, row in enumerate(data[:3]):
            print(f"Row {i+1}:")
            print(json.dumps(row, indent=2))
            print("-" * 50)
    else:
        print("No data extracted")

    # Option 2: Scrape all pages (be careful with this!)
    # print("Scraping all available pages...")
    # all_data = scraper.scrape_all_pages()
    # scraper.save_to_json(all_data, "complete_annuity_data.json")

if __name__ == "__main__":
    example_usage() 
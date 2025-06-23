#!/usr/bin/env python3
"""
Quick run script for AnnuityRateWatch scraper with your credentials
"""

from annuity_scraper import AnnuityRateWatchScraper
import json

def main():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    print("🚀 Starting AnnuityRateWatch scraper...")
    
    # Create scraper instance
    scraper = AnnuityRateWatchScraper(username, password)
    
    # Test with just the first few pages to start
    print("📊 Scraping first 3 pages as a test...")
    data = scraper.scrape_all_pages(start_page=1, max_pages=3)
    
    if data:
        print(f"✅ Success! Extracted {len(data)} total rows")
        
        # Save to JSON
        output_file = "annuity_data_test.json"
        scraper.save_to_json(data, output_file)
        
        # Show sample of the data
        print(f"\n📋 Sample of extracted data (first row):")
        if len(data) > 0:
            print(json.dumps(data[0], indent=2))
        
        print(f"\n💾 Data saved to: {output_file}")
        print(f"📈 Total rows extracted: {len(data)}")
        
        # Show unique column names
        if data:
            all_columns = set()
            for row in data:
                all_columns.update(row.keys())
            print(f"\n📊 Columns found: {sorted(list(all_columns))}")
        
    else:
        print("❌ No data was extracted. Check your credentials and connection.")

if __name__ == "__main__":
    main() 
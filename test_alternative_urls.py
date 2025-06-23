#!/usr/bin/env python3
"""
Test alternative URLs that might have the table data
"""

from annuity_scraper import AnnuityRateWatchScraper
from bs4 import BeautifulSoup
import json

def test_alternative_urls():
    # Your credentials
    username = "calebshump"
    password = "TacoTuesday"
    
    scraper = AnnuityRateWatchScraper(username, password)
    
    print("🔍 Testing alternative URLs...")
    
    if not scraper.login():
        print("❌ Login failed")
        return
    
    # URLs to test
    test_urls = [
        "https://members.annuityratewatch.com/lifeinnovators/instn/cd-spreadsheet.htm",  # MYGA Detail Sheet
        "https://members.annuityratewatch.com/lifeinnovators/instn/top-cd-annuities.htm",  # MYGA Top Rates
        "https://members.annuityratewatch.com/lifeinnovators/instn/myCollection.htm?dpl=1&searchCollection",  # View Products on Grid
        "https://members.annuityratewatch.com/lifeinnovators/instn/annuities-by-company.htm",  # Product List by Company
    ]
    
    for i, url in enumerate(test_urls):
        print(f"\n🔄 Testing URL {i+1}: {url}")
        
        try:
            response = scraper.session.get(url)
            
            if response.status_code == 200:
                print(f"✅ Successfully accessed URL")
                
                # Save HTML for inspection
                filename = f"alternative_page_{i+1}.html"
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                print(f"💾 HTML saved to: {filename}")
                
                # Analyze the content
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Look for tables
                tables = soup.find_all('table')
                print(f"🗂️  Tables found: {len(tables)}")
                
                for table_idx, table in enumerate(tables):
                    rows = table.find_all('tr')
                    if len(rows) > 1:  # Has data rows
                        print(f"  Table {table_idx}: {len(rows)} rows")
                        
                        # Check if this looks like product data
                        first_row_text = ' '.join([cell.get_text(strip=True) for cell in rows[0].find_all(['th', 'td'])])
                        print(f"  Headers: {first_row_text[:100]}...")
                        
                        # If this table has many rows, extract some data
                        if len(rows) > 5:
                            print(f"  🎯 This table looks promising! Extracting data...")
                            data = scraper.extract_table_data(response.text)
                            if data:
                                json_filename = f"table_data_url_{i+1}.json"
                                with open(json_filename, 'w', encoding='utf-8') as f:
                                    json.dump(data, f, indent=2, ensure_ascii=False)
                                print(f"  💾 Data extracted to: {json_filename}")
                                print(f"  📊 Total rows: {len(data)}")
                                
                                # Show sample
                                if data:
                                    print(f"  📋 Sample row:")
                                    print(f"  {json.dumps(data[0], indent=4)}")
                
                # Check page title
                title = soup.title.string if soup.title else "No title"
                print(f"📄 Page title: {title}")
                
            else:
                print(f"❌ Failed to access URL: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error testing URL: {str(e)}")
    
    print(f"\n🔍 Alternative URL testing completed")

if __name__ == "__main__":
    test_alternative_urls() 